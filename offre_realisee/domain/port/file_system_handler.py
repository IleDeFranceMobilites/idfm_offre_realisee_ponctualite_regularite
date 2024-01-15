import abc
from datetime import datetime

import pandas as pd

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.offre_realisee_config import MesureType


class FileSystemHandler(abc.ABC):
    @abc.abstractmethod
    def read_offre_realisee(self, **kwargs) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_daily_offre_realisee(self, date: datetime) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def save_mesure_qs(
        self, df_mesure_qs: pd.DataFrame, date: datetime,
        aggregation_level: AggregationLevel, mesure_type: MesureType
    ):
        pass

    @abc.abstractmethod
    def get_daily_mesure_qs(self, date: datetime, mesure_type: MesureType) -> pd.DataFrame:
        pass
