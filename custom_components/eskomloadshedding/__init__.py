"""The Eskom Load Shedding integration."""
from __future__ import annotations
from ast import Sub

from datetime import timedelta
import logging

from .ha_eskomloadshedding import EskomAPI, EskomLoadsheddingResults
from load_shedding.providers.eskom import Province, Stage, Suburb
# , EskomException, EskomAPIError, EskomNoStage
# from load_shedding.providers.eskom import Eskom, ProviderError, Province, Stage, Suburb

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Config, CoreState, HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import IntegrationError

from .const import (
    CONF_SUBURB_ID,
    DEBUG_FLAG,
    CONF_MANUAL,
    CONF_PROVINCE_ID,
    # DEFAULT_PROVINCE,
    DEFAULT_SCAN_INTERVAL,
    # DEFAULT_STAGE,
    DOMAIN,
    ESKOM_LOADSHEDDING_SERVICE,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Eskom Loadshedding component."""
    coordinator = EskomLoadsheddingDataCoordinator(hass, config_entry)
    await coordinator.async_setup()

    async def _enable_scheduled_status_tests(*_):
        """Activate the data update coordinator."""
        coordinator.update_interval = timedelta( minutes=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL) )
        await coordinator.async_refresh()

    if not config_entry.options.get(CONF_MANUAL, False):
        if hass.state == CoreState.running:
            await _enable_scheduled_status_tests()
        else:
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_status_tests
            )

    hass.data[DOMAIN] = coordinator

    hass.config_entries.async_setup_platforms(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload Eskom Entry from config_entry."""
    hass.services.async_remove(DOMAIN, ESKOM_LOADSHEDDING_SERVICE)

    unload_ok = await hass.config_entries.async_unload_platforms( config_entry, PLATFORMS )
    if unload_ok:
        hass.data.pop(DOMAIN)
    return unload_ok


class EskomLoadsheddingDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.config_entry: ConfigEntry = config_entry
        self.api: EskomAPI | None = None

        super().__init__(
            self.hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self.async_update
        )

    def initialize(self) -> None:
        """Initialize eskom loadshedding api."""
        self.api = EskomAPI(DEBUG_FLAG)

    def update_data(self):
        """Get the latest data from loadshedding.eskom.co.za"""

        stage: Stage  = self.api.get_stage()

        if  ( self.config_entry.options.get(CONF_PROVINCE_ID) ) and ( self.config_entry.options.get(CONF_SUBURB_ID) ):
            if (self.api.results.stage is not Stage.UNKNOWN) or (self.api.results.stage is not Stage.NO_LOAD_SHEDDING):
                if (self.api.stage_changed()) or (len(self.api.results.schedule) == 0):
                    self.api.get_schedule(
                        province=Province(self.config_entry.options.get(CONF_PROVINCE_ID)),
                        suburb=Suburb(id=self.config_entry.options.get(CONF_SUBURB_ID)),
                        stage=stage
                        )

                # _LOGGER.info(
                #     ">>>>>>>>>>>>>>Stage is : %s",
                #     self.stage,
                # )
        return self.api.results.dict()

    async def async_update(self) -> dict[str, str]:
        """Update Speedtest data."""
        try:
            return await self.hass.async_add_executor_job(self.update_data)
        except Exception as err:
            raise IntegrationError from err

    async def async_setup(self) -> None:
        """Setup Eskom Loadshedding"""
        try:
             await self.hass.async_add_executor_job(self.initialize)
        except Exception as err:
            raise ConfigEntryNotReady from err

        async def request_update(call: ServiceCall) -> None:
            """Request update."""
            await self.async_request_refresh()

        self.hass.services.async_register(
            DOMAIN, ESKOM_LOADSHEDDING_SERVICE, request_update
        )

        self.config_entry.async_on_unload(
            self.config_entry.add_update_listener(options_updated_listener)
        )


async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    if entry.options[CONF_MANUAL]:
        hass.data[DOMAIN].update_interval = None
        return

    hass.data[DOMAIN].update_interval = timedelta(minutes=entry.options[CONF_SCAN_INTERVAL])
    await hass.data[DOMAIN].async_request_refresh()
