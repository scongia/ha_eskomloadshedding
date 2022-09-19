"""The Eskom Load Shedding integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EskomAPI

from .const import (  # DEFAULT_PROVINCE,; DEFAULT_STAGE,
    CONF_MANUAL,
    CONF_PROVINCE_ID,
    CONF_SUBURB_ID,
    DEBUG_FLAG,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    UNKNOWN_STAGE,
    PLATFORMS,
    STARTUP_MESSAGE,
    NOTIFICATION_ID,
    NOTIFICATION_CONFIG_ID,
    NOTIF_MSG_NO_ESKOM,
    NOTIF_MSG_NO_CONFIG,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eskom Loadshedding component."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    client = EskomAPI(
        entry.options.get(CONF_PROVINCE_ID),
        entry.options.get(CONF_SUBURB_ID),
        DEBUG_FLAG,
    )

    # Create Data Coordinator object and set update interval
    coordinator = EskomLoadsheddingDataCoordinator(hass, client)
    await coordinator.async_refresh()

    coordinator.update_interval = timedelta(
        minutes=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup Platforms for SENSOR and CALENDAR
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


class EskomLoadsheddingDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: EskomAPI) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.platforms = []
        self.api: EskomAPI = client

        super().__init__(self.hass, _LOGGER, name=DOMAIN)

    async def _async_update_data(self):
        """Update data via library."""
        results: dict[str, Any] = {}

        try:
            results = await self.hass.async_add_executor_job(self.api.get_data)
        except Exception as exception:
            _LOGGER.error("Error while updating")
            raise UpdateFailed() from exception

        # Create notification if Eskom is unavailable
        if results["stage"] == UNKNOWN_STAGE.value:
            _LOGGER.error("Unable to reach Eskom")
            persistent_notification.async_create(
                self.hass,
                title="Eskom communication error",
                message=NOTIF_MSG_NO_ESKOM,
                notification_id=NOTIFICATION_ID,
            )
        else:
            persistent_notification.async_dismiss(self.hass, NOTIFICATION_ID)

        # Create notification if no schedule
        if results["schedule"] == [] and results["stage"] != UNKNOWN_STAGE.value:
            _LOGGER.error("Unable to reach Eskom")
            persistent_notification.async_create(
                self.hass,
                title="Eskom configuration missing",
                message=NOTIF_MSG_NO_CONFIG,
                notification_id=NOTIFICATION_CONFIG_ID,
            )
        else:
            persistent_notification.async_dismiss(self.hass, NOTIFICATION_CONFIG_ID)

        return results


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Eskom Entry from config_entry."""
    # unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # if unload_ok:
    #     del hass.data[DOMAIN][entry.entry_id]
    # return unload_ok
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Integration Reload"""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    if entry.options[CONF_MANUAL]:
        hass.data[DOMAIN][entry.entry_id].update_interval = None
        return

    hass.data[DOMAIN][entry.entry_id].update_interval = timedelta(
        minutes=entry.options[CONF_SCAN_INTERVAL]
    )

    hass.data[DOMAIN][entry.entry_id].api.set_province(entry.options[CONF_PROVINCE_ID])
    hass.data[DOMAIN][entry.entry_id].api.set_suburb(entry.options[CONF_SUBURB_ID])

    await hass.data[DOMAIN][entry.entry_id].async_request_refresh()
