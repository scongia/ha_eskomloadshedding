"""EskomLoadsheddingEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from load_shedding.providers.eskom import Stage

from .const import (
    ATTR_SCAN_INTERVAL,
    ATTR_SHEDDING_STAGE,
    ATTRIBUTION,
    CONF_SCAN_PERIOD,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NAME,
    VERSION,
)


class EskomLoadsheddingEntity(CoordinatorEntity):
    """EskomLoadsheddingEntity class"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": DEFAULT_NAME,
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        attrs.update(
            {
                "attribution": ATTRIBUTION,
                # "id": str(self.coordinator.data.get("id")),
                "integration": DOMAIN,
            }
        )

        if self.coordinator.config_entry is not None:
            attrs.update(
                {
                    ATTR_SCAN_INTERVAL: self.coordinator.config_entry.options.get(
                        CONF_SCAN_PERIOD, DEFAULT_SCAN_INTERVAL
                    ),
                }
            )

        if self.coordinator.data is not None:
            attrs[ATTR_SHEDDING_STAGE] = str(
                Stage(self.coordinator.data.get(ATTR_SHEDDING_STAGE))
            )
        return attrs

        # @property
        # def extra_state_attributes(self) -> dict[str, Any]:
        #     """Return the state attributes."""
        #     attrs = {}
        #     if self.coordinator.data is not None:
        #         attrs.update(
        #             {
        #                 ATTR_SCAN_INTERVAL: self.coordinator.config_entry.options.get(
        #                     CONF_SCAN_PERIOD, DEFAULT_SCAN_INTERVAL
        #                 ),
        #             }
        #         )

        #         attrs[ATTR_SHEDDING_STAGE] = str(
        #             Stage(self.coordinator.data[ATTR_SHEDDING_STAGE])
        #         )
        #     return attrs

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update entity."""
        await self.coordinator.async_request_refresh()
