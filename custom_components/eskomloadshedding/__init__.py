"""The Eskom Load Shedding integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Config, CoreState, HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, IntegrationError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from load_shedding.providers.eskom import Province, Stage, Suburb

from .api import EskomAPI, EskomLoadsheddingResults

from .const import (  # DEFAULT_PROVINCE,; DEFAULT_STAGE,
    CONF_MANUAL,
    CONF_PROVINCE_ID,
    CONF_SUBURB_ID,
    DEBUG_FLAG,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ESKOM_LOADSHEDDING_SERVICE,
    PLATFORMS,
    STARTUP_MESSAGE,
    ISSUE_URL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eskom Loadshedding component."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    province = entry.options.get(CONF_PROVINCE_ID)
    suburb = entry.options.get(CONF_SUBURB_ID)
    client = EskomAPI(
        province,
        suburb,
        DEBUG_FLAG,
    )

    coordinator = EskomLoadsheddingDataCoordinator(hass, client=client)
    await coordinator.async_refresh()

    coordinator.update_interval = timedelta(
        minutes=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Eskom Entry from config_entry."""
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

    return


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


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
        try:
            return await self.hass.async_add_executor_job(self.api.get_data)
        except Exception as exception:
            raise UpdateFailed() from exception


async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    if entry.options[CONF_MANUAL]:
        hass.data[DOMAIN][entry.entry_id].update_interval = None
        return

    hass.data[DOMAIN][entry.entry_id].update_interval = timedelta(
        minutes=entry.options[CONF_SCAN_INTERVAL]
    )

    hass.data[DOMAIN][entry.entry_id].api.setProvince(entry.options[CONF_PROVINCE_ID])
    hass.data[DOMAIN][entry.entry_id].api.setSuburb(entry.options[CONF_SUBURB_ID])

    await hass.data[DOMAIN][entry.entry_id].async_request_refresh()
