"""Test component setup"""
from custom_components.eskomloadshedding import (
    EskomLoadsheddingDataCoordinator, async_reload_entry, async_setup_entry,
    async_unload_entry)
from custom_components.eskomloadshedding.const import (ATTR_CALENDAR_ID,
                                                       ATTR_SHEDDING_STAGE,
                                                       DOMAIN)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG

ENTITY_STAGE = f"sensor.{DOMAIN}_{ATTR_SHEDDING_STAGE}"
ENTITY_SCHED = f"calendar.{DOMAIN}_{ATTR_CALENDAR_ID}"


async def test_setup_unload_and_reload_entry(hass):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    # config_entry = MockConfigEntry(
    #     domain=DOMAIN, data={}, entry_id=""
    # )

    #

    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the ocppDataUpdateCoordinator.async_get_data
    # call, no code from custom_components/ocpp/api.py actually runs.
    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == EskomLoadsheddingDataCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == EskomLoadsheddingDataCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]
