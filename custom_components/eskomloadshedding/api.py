from datetime import datetime, timedelta, timezone
import logging

from load_shedding.load_shedding import ScheduleError, get_schedule
from load_shedding.providers.eskom import Eskom, ProviderError, Province, Stage, Suburb

from .const import (
    ATTR_SCHEDULE,
    ATTR_SHEDDING_STAGE,
    DEBUG_SCHEDULE,
    DEBUG_STAGE
)

TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


# class EskomProviderError(Exception):
#     pass


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

    def find_suburbs(self, search_text):
        """Searh for suburb"""
        try:
            eskom = Eskom()
            return eskom.find_suburbs(search_text)
        except ProviderError as ex:
            _LOGGER.info("Provider Error %s", ex)
        except ValueError as ex:
            raise EskomRequestRejectedException("Request Rejected") from ex
        except Exception as ex:
            raise EskomException("Esception calling find_suburbs") from ex

    def set_province(self, province):
        """Set Province"""
        self._province = province

    def set_suburb(self, suburb):
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
            except ProviderError as ex:
                _LOGGER.info("Provider Error %s", ex)
            except Exception as ex:
                _LOGGER.info("Exception %s", ex)

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

        self.clear_schedule()

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
            except ScheduleError as ex:
                _LOGGER.error( ex.args[0] )
            except ProviderError as ex:
                _LOGGER.error( ex.args[0] )

        utc_tz = timezone.utc
        days = 7
        for item in schedule:
            start = datetime.fromisoformat(item[0])
            end = datetime.fromisoformat(item[1])
            if start > datetime.now(utc_tz) + timedelta(days=days):
                continue
            if end < datetime.now(utc_tz):
                continue
            self.results.schedule.append(item)

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


class EskomException(Exception):
    """Base exception for this module"""


class EskomRequestRejectedException(EskomException):
    """Request Rejected Exception"""
