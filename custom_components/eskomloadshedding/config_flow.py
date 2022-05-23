"""Adds config flow for the Eskom Loadshedding Interface."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import IntegrationError
from load_shedding.providers.eskom import Eskom, ProviderError, Province, Stage, Suburb
import voluptuous as vol

from .const import (
    CONF_MANUAL,
    CONF_PROVINCE_ID,
    CONF_SUBURB_ID,
    DEFAULT_MANUAL_FLAG,
    DEFAULT_NAME,
    DEFAULT_PROVINCE_ID,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SET_AREA_FLAG,
    DOMAIN,
    PROVINCE_LIST,
    USER_FLAG_SET_AREA,
    USER_PROVINCE_NAME,
    USER_SUBURB_NAME,
    USER_SUBURB_SEARCH,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class EskomLoadsheddingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Speedtest.net config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return EskomLoadsheddingOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title=DEFAULT_NAME, data=user_input)


class EskomLoadsheddingOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Eskom Loadshedding options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._user_input: dict = {}
        self._suburbs_select = {}
        self._config_data = {
            CONF_SCAN_INTERVAL: self.config_entry.options.get(
                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
            ),
            CONF_MANUAL: self.config_entry.options.get(
                CONF_MANUAL, DEFAULT_MANUAL_FLAG
            ),
            CONF_PROVINCE_ID: self.config_entry.options.get(
                CONF_PROVINCE_ID, str(Province(DEFAULT_PROVINCE_ID))
            ),
            CONF_SUBURB_ID: self.config_entry.options.get(CONF_SUBURB_ID),
        }

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""

        errors: dict[str, str] = {}

        if user_input is not None:
            self._config_data[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
            self._config_data[CONF_MANUAL] = user_input[CONF_MANUAL]
            if user_input[USER_FLAG_SET_AREA]:
                return await self.async_step_suburb_search()
            else:
                return self.async_create_entry(title="", data=self._config_data)

        options = {
            # Scan Interval
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): int,
            # Manual Scan Interval Override Flag
            vol.Optional(
                CONF_MANUAL,
                default=self.config_entry.options.get(CONF_MANUAL, DEFAULT_MANUAL_FLAG),
            ): bool,
            # Continue
            vol.Optional(USER_FLAG_SET_AREA, default=DEFAULT_SET_AREA_FLAG): bool,
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options), errors=errors
        )

    async def async_step_suburb_search(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle suburb search flow."""
        errors = {}

        if user_input is not None:
            # Province ID
            selected_province = PROVINCE_LIST[user_input[USER_PROVINCE_NAME]]
            # Province Search
            search_result: list[Suburb] | None = None
            try:
                search_text: str = user_input[USER_PROVINCE_NAME]
                _LOGGER.info(
                    "Eskomloadshedding:config_flow:step:suburb_search>> Start Suburb Search for suburb %s in %s",
                    search_text,
                    str(Province(selected_province)),
                )

                api = Eskom()
                search_result = await self.hass.async_add_executor_job(
                    api.find_suburbs, user_input[USER_SUBURB_SEARCH]
                )

                _LOGGER.info(
                    "Eskomloadshedding:config_flow:step:suburb_search>> End Suburb Search. No suburbs found  %s",
                    len(search_result),
                )
            except Exception as err:
                raise IntegrationError from err

            # Filter by province
            for suburb in search_result:
                if suburb.province == selected_province:
                    self._suburbs_select[suburb.name] = suburb

            self._config_data[CONF_PROVINCE_ID] = selected_province.value
            return await self.async_step_suburb_select()

        options = {
            # Province Name
            vol.Optional(
                USER_PROVINCE_NAME,
                default=str(
                    Province(
                        self.config_entry.options.get(
                            (CONF_PROVINCE_ID), DEFAULT_PROVINCE_ID
                        )
                    )
                ),
            ): vol.In(PROVINCE_LIST.keys()),
            # Scan Interval
            vol.Required(USER_SUBURB_SEARCH): str,
        }

        return self.async_show_form(
            step_id="suburb_search", data_schema=vol.Schema(options), errors=errors
        )

    async def async_step_suburb_select(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""

        errors: dict[str, str] = {}

        if user_input is not None:

            selected_suburb = self._suburbs_select[user_input[USER_SUBURB_NAME]]
            self._config_data[CONF_SUBURB_ID] = selected_suburb.id
            return self.async_create_entry(title="", data=self._config_data)

        options = {
            # Suburb Select (No Default)
            vol.Optional(
                USER_SUBURB_NAME,
            ): vol.In(self._suburbs_select.keys()),
        }

        return self.async_show_form(
            step_id="suburb_select", data_schema=vol.Schema(options), errors=errors
        )


async def _async_eskom_find_suburb(hass, search_text: str):
    api = Eskom()
    return await hass.async_add_executor_job(api.find_suburbs, search_text)
