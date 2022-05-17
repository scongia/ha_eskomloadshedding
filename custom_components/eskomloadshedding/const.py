"""Constants for the Eskom Loadshedding integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
from homeassistant.const import Platform
from load_shedding.providers.eskom import Province, Stage

DOMAIN = "eskomloadshedding"

DEBUG_FLAG = False

DEBUG_STAGE: Final = Stage.STAGE_2
DEBUG_SCHEDULE: Final = [
    ["2022-05-11 06:00", "2022-05-11 08:30"],
    ["2022-05-12 06:00", "2022-05-12 08:30"],
    ["2022-05-12 14:00", "2022-05-12 16:30"],
    ["2022-05-13 12:00", "2022-05-13 14:30"],
    ["2022-05-13 20:00", "2022-05-13 22:30"],
    ["2022-05-14 20:00", "2022-05-14 22:30"],
    ["2022-05-15 04:00", "2022-05-15 06:30"],
    ["2022-05-16 04:00", "2022-05-16 06:30"],
    ["2022-05-16 12:00", "2022-05-16 14:30"],
    ["2022-05-17 10:00", "2022-05-17 12:30"],
    ["2022-05-17 18:00", "2022-05-17 20:30"],
    ["2022-05-18 18:00", "2022-05-18 20:30"],
    ["2022-05-19 02:00", "2022-05-19 04:30"],
    ["2022-05-20 02:00", "2022-05-20 04:30"],
    ["2022-05-20 10:00", "2022-05-20 12:30"],
    ["2022-05-21 08:00", "2022-05-21 10:30"],
    ["2022-05-21 16:00", "2022-05-21 18:30"],
    ["2022-05-22 16:00", "2022-05-22 18:30"],
    ["2022-05-23 00:00", "2022-05-23 02:30"],
    ["2022-05-24 00:00", "2022-05-24 02:30"],
    ["2022-05-24 08:00", "2022-05-24 10:30"],
    ["2022-05-25 06:00", "2022-05-25 08:30"],
    ["2022-05-25 14:00", "2022-05-25 16:30"],
    ["2022-05-26 14:00", "2022-05-26 16:30"],
    ["2022-05-26 22:00", "2022-05-26 00:30"],
    ["2022-05-27 22:00", "2022-05-27 00:30"],
    ["2022-05-28 06:00", "2022-05-28 08:30"],
    ["2022-05-29 04:00", "2022-05-29 06:30"],
    ["2022-05-29 12:00", "2022-05-29 14:30"],
    ["2022-05-30 12:00", "2022-05-30 14:30"],
    ["2022-05-30 20:00", "2022-05-30 22:30"],
    ["2022-06-01 18:00", "2022-06-01 20:30"],
    ["2022-06-02 02:00", "2022-06-02 04:30"],
    ["2022-06-03 02:00", "2022-06-03 04:30"],
    ["2022-06-03 10:00", "2022-06-03 12:30"],
    ["2022-06-04 10:00", "2022-06-04 12:30"],
    ["2022-06-04 18:00", "2022-06-04 20:30"],
    ["2022-06-05 16:00", "2022-06-05 18:30"],
    ["2022-06-06 00:00", "2022-06-06 02:30"],
    ["2022-06-07 00:00", "2022-06-07 02:30"],
    ["2022-06-07 08:00", "2022-06-07 10:30"],
    ["2022-06-08 08:00", "2022-06-08 10:30"],
    ["2022-06-08 16:00", "2022-06-08 18:30"],
    ["2022-06-09 14:00", "2022-06-09 16:30"],
    ["2022-06-09 22:00", "2022-06-09 00:30"],
]

ESKOM_LOADSHEDDING_SERVICE: Final = "eskomloadshedding"


@dataclass
class EskomLoadsheddingSensorEntityDescription(SensorEntityDescription):
    """Class describing Speedtest sensor entities."""

    value: Callable = round


SENSOR_TYPES: Final[tuple[EskomLoadsheddingSensorEntityDescription, ...]] = (
    EskomLoadsheddingSensorEntityDescription(
        key="stage",
        name="Stage",
        # native_unit_of_measurement=TIME_MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EskomLoadsheddingSensorEntityDescription(
        key="next_outage",
        name="Next Outage",
        # native_unit_of_measurement=TIME_HOURS
    ),
)

ICON = "mdi:lightning-bolt"

NAME = "Eskom Loadshedding Interface"
VERSION = "1.0.6"

PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]

USER_PROVINCE_NAME: Final = "province_name"
USER_SUBURB_NAME = "suburb_name"
USER_SUBURB_SEARCH = "suburb_search"
USER_FLAG_SET_AREA = "set_area_flag"

CONF_PROVINCE_ID = "province_id"
CONF_SUBURB_ID = "suburb_id"
CONF_MANUAL: Final = "manual"
CONF_SCAN_PERIOD = "scan_interval"

ATTR_PROVINCE_NAME: Final = "province_name"
ATTR_PROVINCE_ID: Final = "province_id"
ATTR_SUBURB_ID: Final = "suburb_id"
ATTR_SHEDDING_STAGE: Final = "stage"
ATTR_SHEDDING_NEXT: Final = "next_outage"
ATTR_SCHEDULE: Final = "schedule"
ATTR_SCAN_INTERVAL: Final = "scan_interval"

ATTR_CALENDAR_ICON = "mdi:lightning-bolt"
ATTR_CALENDAR_NAME = "Eskom Schedule"
ATTR_CALENDAR_ID = "eskom_calendar"
ATTR_CALENDAR_EVENT_SUMMARY = "Load Shedding"

DEFAULT_NAME = "EskomLoadshedding"
DEFAULT_SCAN_INTERVAL: Final = 15
DEFAULT_MANUAL_FLAG: Final = False
DEFAULT_SET_AREA_FLAG: Final = True
DEFAULT_PROVINCE_ID = 9

ATTRIBUTION: Final = "Data retrieved from Eskom Loadshedding API"

PROVINCE_LIST: Final = {
    str(Province.EASTERN_CAPE): Province.EASTERN_CAPE,
    str(Province.FREE_STATE): Province.FREE_STATE,
    str(Province.GAUTENG): Province.GAUTENG,
    str(Province.KWAZULU_NATAL): Province.KWAZULU_NATAL,
    str(Province.LIMPOPO): Province.LIMPOPO,
    str(Province.MPUMALANGA): Province.MPUMALANGA,
    str(Province.NORTH_WEST): Province.NORTH_WEST,
    str(Province.NORTERN_CAPE): Province.NORTERN_CAPE,
    str(Province.WESTERN_CAPE): Province.WESTERN_CAPE,
}
