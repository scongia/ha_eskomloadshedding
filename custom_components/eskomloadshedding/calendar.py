"""Support for Eskom Load Shedding Calendar."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from load_shedding.providers.eskom import Province

from . import EskomLoadsheddingDataCoordinator
from .const import (
    ATTR_CALENDAR_EVENT_SUMMARY,
    ATTR_CALENDAR_ICON,
    ATTR_CALENDAR_ID,
    ATTR_CALENDAR_NAME,
    ATTR_PROVINCE_ID,
    ATTR_PROVINCE_NAME,
    ATTR_SCHEDULE,
    ATTR_SUBURB_ID,
    ATTRIBUTION,
    CONF_PROVINCE_ID,
    CONF_SUBURB_ID,
    DATE_TIME_FORMAT,
    DOMAIN,
    NOT_CONFIGURED,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Twente Milieu calendar based on a config entry."""
    eskom_loadshedding_coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EskomLoadsheddingCalendar(eskom_loadshedding_coordinator)])


class EskomLoadsheddingCalendar(
    CoordinatorEntity[EskomLoadsheddingDataCoordinator], CalendarEntity
):
    """Defines a Twente Milieu calendar."""

    _attr_name = ATTR_CALENDAR_NAME
    _attr_icon = ATTR_CALENDAR_ICON

    def __init__(
        self,
        coordinator: EskomLoadsheddingDataCoordinator,
        # entry: ConfigEntry,
    ) -> None:
        """Initialize the LoadShedding Calendar."""
        super().__init__(coordinator)
        self._attr_unique_id = ATTR_CALENDAR_ID
        self._attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        self._event: CalendarEvent | None = None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.config_entry is not None:
            if self.coordinator.config_entry.options.get(CONF_PROVINCE_ID) is not None:
                self._attrs.update(
                    {
                        ATTR_PROVINCE_NAME: str(
                            Province(
                                self.coordinator.config_entry.options.get(
                                    CONF_PROVINCE_ID
                                )
                            )
                        )
                    }
                )
            else:
                self._attrs.update({ATTR_PROVINCE_NAME: NOT_CONFIGURED})

            self._attrs.update(
                {
                    ATTR_PROVINCE_ID: self.coordinator.config_entry.options.get(
                        CONF_PROVINCE_ID, NOT_CONFIGURED
                    ),
                    ATTR_SUBURB_ID: self.coordinator.config_entry.options.get(
                        CONF_SUBURB_ID, NOT_CONFIGURED
                    ),
                }
            )

        return self._attrs

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events: list[CalendarEvent] = []

        if self.coordinator.data is not None:
            schedule = self.coordinator.data[ATTR_SCHEDULE]
            utc_tz = timezone.utc
            days = 7

            for s in schedule:
                start = datetime.fromisoformat(s[0])
                end = datetime.fromisoformat(s[1])
                if start.date() > datetime.now(utc_tz).date() + timedelta(days=days):
                    continue
                if end.date() < datetime.now(utc_tz).date():
                    continue
                events.append(
                    CalendarEvent(
                        summary=ATTR_CALENDAR_EVENT_SUMMARY,
                        start=start,
                        end=end,
                    )
                )

        return events

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._event = None
        if self.coordinator.data is not None:
            if len(self.coordinator.data[ATTR_SCHEDULE]) > 0:
                date_time_start = datetime.strptime(
                    self.coordinator.data[ATTR_SCHEDULE][0][0], DATE_TIME_FORMAT
                )
                date_time_end = datetime.strptime(
                    self.coordinator.data[ATTR_SCHEDULE][0][1], DATE_TIME_FORMAT
                )
                self._event = CalendarEvent(
                    summary=ATTR_CALENDAR_EVENT_SUMMARY,
                    start=date_time_start,
                    end=date_time_end,
                )

        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
