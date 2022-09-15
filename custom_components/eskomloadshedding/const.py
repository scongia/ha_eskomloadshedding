"""Constants for the Eskom Loadshedding integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
from homeassistant.const import Platform
from load_shedding.providers.eskom import Province, Stage

DOMAIN = "eskomloadshedding"
VERSION = "1.0.7"

DEBUG_FLAG = False

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%f%z"  # Consider moving to const
DEBUG_STAGE: Final = Stage.STAGE_2
DEBUG_SCHEDULE: Final = [
    ("2022-05-23T02:00:00+00:00", "2022-05-23T04:30:00+00:00"),
    ("2022-05-24T02:00:00+00:00", "2022-05-24T04:30:00+00:00"),
    ("2022-05-24T10:00:00+00:00", "2022-05-24T12:30:00+00:00"),
    ("2022-05-25T08:00:00+00:00", "2022-05-25T10:30:00+00:00"),
    ("2022-05-25T16:00:00+00:00", "2022-05-25T18:30:00+00:00"),
    ("2022-05-26T16:00:00+00:00", "2022-05-26T18:30:00+00:00"),
    ("2022-05-27T00:00:00+00:00", "2022-05-27T02:30:00+00:00"),
    ("2022-05-28T00:00:00+00:00", "2022-05-28T02:30:00+00:00"),
    ("2022-05-28T08:00:00+00:00", "2022-05-28T10:30:00+00:00"),
    ("2022-05-29T06:00:00+00:00", "2022-05-29T08:30:00+00:00"),
    ("2022-05-29T14:00:00+00:00", "2022-05-29T16:30:00+00:00"),
    ("2022-05-30T14:00:00+00:00", "2022-05-30T16:30:00+00:00"),
    ("2022-05-30T22:00:00+00:00", "2022-05-31T00:30:00+00:00"),
    ("2022-06-01T20:00:00+00:00", "2022-05-31T22:30:00+00:00"),
    ("2022-06-02T04:00:00+00:00", "2022-06-02T06:30:00+00:00"),
    ("2022-06-03T04:00:00+00:00", "2022-06-03T06:30:00+00:00"),
    ("2022-06-03T12:00:00+00:00", "2022-06-03T14:30:00+00:00"),
    ("2022-06-04T12:00:00+00:00", "2022-06-04T14:30:00+00:00"),
    ("2022-06-04T20:00:00+00:00", "2022-06-03T22:30:00+00:00"),
    ("2022-06-05T18:00:00+00:00", "2022-06-05T20:30:00+00:00"),
    ("2022-06-06T02:00:00+00:00", "2022-06-06T04:30:00+00:00"),
    ("2022-06-07T02:00:00+00:00", "2022-06-07T04:30:00+00:00"),
    ("2022-06-07T10:00:00+00:00", "2022-06-07T12:30:00+00:00"),
    ("2022-06-08T10:00:00+00:00", "2022-06-08T12:30:00+00:00"),
    ("2022-06-08T18:00:00+00:00", "2022-06-08T20:30:00+00:00"),
    ("2022-06-09T16:00:00+00:00", "2022-06-09T18:30:00+00:00"),
    ("2022-06-10T00:00:00+00:00", "2022-06-10T02:30:00+00:00"),
    ("2022-06-11T00:00:00+00:00", "2022-06-11T02:30:00+00:00"),
    ("2022-06-11T08:00:00+00:00", "2022-06-11T10:30:00+00:00"),
    ("2022-06-12T08:00:00+00:00", "2022-06-12T10:30:00+00:00"),
    ("2022-06-12T16:00:00+00:00", "2022-06-12T18:30:00+00:00"),
    ("2022-06-13T14:00:00+00:00", "2022-06-13T16:30:00+00:00"),
    ("2022-06-13T22:00:00+00:00", "2022-06-14T00:30:00+00:00"),
    ("2022-06-14T22:00:00+00:00", "2022-06-15T00:30:00+00:00"),
    ("2022-06-15T06:00:00+00:00", "2022-06-15T08:30:00+00:00"),
    ("2022-06-16T06:00:00+00:00", "2022-06-16T08:30:00+00:00"),
    ("2022-06-16T14:00:00+00:00", "2022-06-16T16:30:00+00:00"),
    ("2022-06-17T12:00:00+00:00", "2022-06-17T14:30:00+00:00"),
    ("2022-06-17T20:00:00+00:00", "2022-06-16T22:30:00+00:00"),
    ("2022-06-18T20:00:00+00:00", "2022-06-17T22:30:00+00:00"),
    ("2022-06-19T04:00:00+00:00", "2022-06-19T06:30:00+00:00"),
    ("2022-06-20T04:00:00+00:00", "2022-06-20T06:30:00+00:00"),
    ("2022-06-20T12:00:00+00:00", "2022-06-20T14:30:00+00:00"),
]

# ESKOM_LOADSHEDDING_SERVICE: Final = "eskomloadshedding"


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
    # EskomLoadsheddingSensorEntityDescription(
    #     key="next_outage",
    #     name="Next Outage",
    #     # native_unit_of_measurement=TIME_HOURS
    # ),
)

ICON = "mdi:lightning-bolt"

NAME = "Eskom Loadshedding Interface"

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

ERR_MSG_REQUEST_REJECTED = "Request Rejected"

ATTRIBUTION: Final = "Data retrieved from Eskom Loadshedding API"
NOT_CONFIGURED: Final = "PLEASE CONFIGURE INTEGRATION"

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
ISSUE_URL = "https://github.com/scongia/ha_eskomloadshedding/issues"
STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
Eskom Loadshedding Integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
