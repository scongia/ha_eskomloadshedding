"""Support for Speedtest.net internet speed testing sensor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

# from . import EskomLoadsheddingDataCoordinator
from .const import ATTR_SHEDDING_STAGE, DEFAULT_NAME, DOMAIN, ICON
from .entity import EskomLoadsheddingEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([EskomStageSensor(coordinator, entry)])


class EskomStageSensor(EskomLoadsheddingEntity, SensorEntity):
    """Implementation of a Eskom Loadshedding sensor."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{ATTR_SHEDDING_STAGE}"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def native_value(self):
        """Return native value for entity."""
        state = self.coordinator.data.get(ATTR_SHEDDING_STAGE)
        return state
