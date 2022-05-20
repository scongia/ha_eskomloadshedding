from datetime import datetime, timedelta, timezone
import logging

from homeassistant.helpers.config_validation import boolean
from load_shedding.providers.eskom import Eskom, ProviderError, Province, Stage, Suburb

from .const import (
    ATTR_SCHEDULE,
    ATTR_SHEDDING_NEXT,
    ATTR_SHEDDING_STAGE,
    DEBUG_SCHEDULE,
    DEBUG_STAGE,
)

_LOGGER = logging.getLogger(__name__)


class EskomProviderError(Exception):
    pass


class EskomAPI:
    """Interface class to obtain loadshedding information using the Eskom API"""

    def __init__(self, debug_flag=False):
        """Initializes class parameters"""
        self.eskom = Eskom()
        self.stage = Stage.UNKNOWN
        self.stage_changed_flag = True
        self.results = EskomLoadsheddingResults()

        self.debug_flag: bool = debug_flag

    def get_stage(self) -> Stage:
        """Return load shedding stage"""
        stage = Stage.UNKNOWN

        if self.debug_flag:
            stage = DEBUG_STAGE
        else:

            try:
                stage = self.eskom.get_stage()
            except ProviderError as exception:
                raise EskomProviderError from None
            except Exception as exception:
                _LOGGER.exception(exception)

        if stage == self.results.stage:
            self.stage_changed_flag = False

        self.results.stage = stage
        return self.results.stage

    def clear_schedule(self) -> None:
        """Clear schedule"""
        self.results.schedule = []

    def get_schedule(self, province: Province, suburb: Suburb, stage: Stage) -> tuple:
        """Return schedule"""
        schedule = []
        if self.debug_flag:
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

    def stage_changed(self) -> boolean:
        """Return stage_changed_flag"""

        return self.stage_changed_flag


class EskomLoadsheddingResults:
    """Class for holding the results"""

    def __init__(self, stage=Stage.UNKNOWN, schedule=[]):
        """Init Results"""
        self.stage = stage
        self.schedule = schedule

    def dict(self):
        """Return dictionary of result data"""
        data = {ATTR_SHEDDING_STAGE: self.stage, ATTR_SCHEDULE: self.schedule}
        if len(self.schedule) > 0:
            next_outage = self.schedule[0][0]
            data.update({ATTR_SHEDDING_NEXT: next_outage})
        else:
            data.update({ATTR_SHEDDING_NEXT: None})
        return data
