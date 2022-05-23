import asyncio
from datetime import datetime, timedelta, timezone
import json
import logging

import async_timeout
from homeassistant.helpers.config_validation import boolean
from load_shedding.providers.eskom import Eskom, ProviderError, Province, Stage, Suburb

from .const import (
    ATTR_SCHEDULE,
    ATTR_SHEDDING_NEXT,
    ATTR_SHEDDING_STAGE,
    DEBUG_SCHEDULE,
    DEBUG_STAGE,
)

TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


class EskomProviderError(Exception):
    pass


class EskomAPI:
    """Interface class to obtain loadshedding information using the Eskom API"""

    def __init__(self, province: str, suburb: str, debug=False):
        """Initializes class parameters"""
        self.eskom = Eskom()
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
                stage = self.eskom.get_stage()
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
        if self._debug_flag:
            schedule = DEBUG_SCHEDULE
        else:

            schedule = self.eskom.get_schedule(
                province=province, suburb=suburb, stage=stage
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
        stage: Stage = self.get_stage()

        if (self._province) and (self._suburb):
            if stage is not Stage.UNKNOWN:
                if stage is Stage.NO_LOAD_SHEDDING:
                    self.clear_schedule()
                else:
                    if (self._stage_changed_flag) or (len(self.results.schedule) == 0):
                        self.get_schedule(
                            province=Province(self._province),
                            suburb=Suburb(id=self._suburb),
                            stage=stage,
                        )

        return self.results.dict()

    async def async_get_data(self):
        """Get the latest data from loadshedding.eskom.co.za"""

        try:
            async with async_timeout.timeout(TIMEOUT):
                return await self.get_data()
        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching schedule information from Eskom - %s",
                exception,
            )


class EskomLoadsheddingResults:
    """Class for holding the results"""

    def __init__(self, stage=Stage.UNKNOWN, schedule=[]):
        """Init Results"""
        self.stage = stage
        self.schedule = schedule

    def dict(self):
        """Return dictionary of result data"""
        data = {ATTR_SHEDDING_STAGE: self.stage.value, ATTR_SCHEDULE: self.schedule}
        if len(self.schedule) > 0:
            next_outage = self.schedule[0][0]
            data.update({ATTR_SHEDDING_NEXT: next_outage})
        else:
            data.update({ATTR_SHEDDING_NEXT: None})
        return data
