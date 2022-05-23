"""Support for Speedtest.net internet speed testing sensor."""
from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from load_shedding.providers.eskom import Stage

from . import EskomLoadsheddingDataCoordinator
from .const import (
    ATTR_SCAN_INTERVAL,
    ATTR_SHEDDING_STAGE,
    ATTRIBUTION,
    CONF_SCAN_PERIOD,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ICON,
    SENSOR_TYPES,
    EskomLoadsheddingSensorEntityDescription,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Speedtestdotnet sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        EskomLoadsheddingSensor(coordinator, description)
        for description in SENSOR_TYPES
    )


class EskomLoadsheddingSensor(
    CoordinatorEntity[EskomLoadsheddingDataCoordinator], RestoreEntity, SensorEntity
):
    """Implementation of a Eskom Loadshedding sensor."""

    entity_description: EskomLoadsheddingSensorEntityDescription
    _attr_icon = ICON

    def __init__(
        self,
        coordinator: EskomLoadsheddingDataCoordinator,
        description: EskomLoadsheddingSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{DEFAULT_NAME} {description.name}"
        self._attr_unique_id = description.key
        self._state: StateType = None
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=DEFAULT_NAME,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> StateType:
        """Return native value for entity."""
        if self.coordinator.data:
            if self.entity_description.key == ATTR_SHEDDING_STAGE:
                self._state = self.coordinator.data[self.entity_description.key]
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is not None:
            self._attrs.update(
                {
                    ATTR_SCAN_INTERVAL: self.coordinator.config_entry.options.get(
                        CONF_SCAN_PERIOD, DEFAULT_SCAN_INTERVAL
                    ),
                }
            )

            self._attrs[ATTR_SHEDDING_STAGE] = str(
                Stage(self.coordinator.data[ATTR_SHEDDING_STAGE])
            )

        return self._attrs

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if state := await self.async_get_last_state():
            self._state = state.state
