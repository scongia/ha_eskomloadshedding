import asyncio
from datetime import datetime, timedelta, timezone
import json
import logging

import async_timeout
from homeassistant.helpers.config_validation import boolean
from load_shedding.load_shedding import ScheduleError, get_schedule
from load_shedding.providers.eskom import Eskom, ProviderError, Province, Stage, Suburb

from .const import ATTR_SCHEDULE, ATTR_SHEDDING_STAGE, DEBUG_SCHEDULE, DEBUG_STAGE

TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


class EskomProviderError(Exception):
    pass


class EskomAPI:
    """Interface class to obtain loadshedding information using the Eskom API"""

    def __init__(self, province: str, suburb: str, debug=False):
        """Initializes class parameters"""
        # self.eskom = Eskom()
        self.results = EskomLoadsheddingResults()

        self._stage_changed_flag = True
        self._province = province
        self._suburb = suburb
        self._debug_flag: bool = debug

    def setProvince(self, province):
        """Set Province"""
        self._province = province

    def setSuburb(self, suburb):
        """Set Suburb"""
        self._suburb = suburb

    def get_stage(self) -> Stage:
        """Return load shedding stage"""
        stage: Stage = Stage.UNKNOWN

        if self._debug_flag:
            stage = DEBUG_STAGE
        else:

            try:
                eskom = Eskom()
                stage = eskom.get_stage()
            except ProviderError as exception:
                raise EskomProviderError from None
            except Exception as exception:
                _LOGGER.exception(exception)

        # Is new stage same as previous results stage
        if stage == self.results.stage:
            self._stage_changed_flag = False

        self.results.stage = stage
        return self.results.stage

    def clear_schedule(self) -> None:
        """Clear schedule"""
        self.results.schedule = []

    def get_schedule(self, province: Province, suburb: Suburb, stage: Stage) -> tuple:
        """Return schedule"""
        schedule = []
        _LOGGER.info("Get_Schedule: Getting info for suburb: %s", suburb.id)
        if self._debug_flag:
            _LOGGER.info("Get_Schedule: DEBUG SET")
            schedule = DEBUG_SCHEDULE
        else:
            try:
                provider = Eskom()
                schedule = get_schedule(
                    provider, province=province, suburb=suburb, stage=stage
                )
                _LOGGER.info("Schedule for %s %s: %s", suburb.id, stage, schedule)
            except (ProviderError, ScheduleError) as ex:
                _LOGGER.info(
                    "Error: %s",
                    str(ex),
                )

        utc_tz = timezone.utc
        days = 7
        for s in schedule:
            start = datetime.fromisoformat(s[0])
            end = datetime.fromisoformat(s[1])
            if start.date() > datetime.now(utc_tz).date() + timedelta(days=days):
                continue
            if end.date() < datetime.now(utc_tz).date():
                continue
            self.results.schedule.append(s)

        return self.results.schedule

    def get_data(self):
        """get data"""
        _LOGGER.info("GetData:Stage: Trigger getStage()")
        stage: Stage = self.get_stage()
        _LOGGER.info("GetData:Stage: Received Stage %s", stage.value)

        if stage is not Stage.UNKNOWN:
            if self._province and self._suburb:
                if stage is Stage.NO_LOAD_SHEDDING:
                    _LOGGER.info("GetData:Schedule: Stage is 0... Clearing Schedule")
                    self.clear_schedule()
                else:
                    _LOGGER.info(
                        "GetData:Schedule: Has the stage changed? %s ",
                        self._stage_changed_flag,
                    )
                    if (self._stage_changed_flag) or (len(self.results.schedule) == 0):
                        _LOGGER.info(
                            "GetData:Schedule: Schedule: Read and update Schedule "
                        )
                        self.get_schedule(
                            province=Province(self._province),
                            suburb=Suburb(id=self._suburb),
                            stage=stage,
                        )
                        _LOGGER.info("GetData:Schedule: Schedule: Done.... ")
            else:
                _LOGGER.info(
                    "GetData:Schedule: Skipping.. Either Province or Suburb aren't missing"
                )
        else:
            _LOGGER.info("GetData:Schedule: Skipping.. Stage is UNKNOWN")

        return self.results.dict()

    # async def async_get_data(self):
    #     """Get the latest data from loadshedding.eskom.co.za"""

    #     try:
    #         async with async_timeout.timeout(TIMEOUT):
    #             return await self.get_data()
    #     except asyncio.TimeoutError as exception:
    #         _LOGGER.error(
    #             "Timeout error fetching schedule information from Eskom - %s",
    #             exception,
    #         )


class EskomLoadsheddingResults:
    """Class for holding the results"""

    def __init__(self, stage=Stage.UNKNOWN, schedule=[]):
        """Init Results"""
        self.stage = stage
        self.schedule = schedule

    def dict(self):
        """Return dictionary of result data"""
        data = {ATTR_SHEDDING_STAGE: self.stage.value, ATTR_SCHEDULE: self.schedule}
        return data
