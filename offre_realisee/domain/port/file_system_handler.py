import abc
from datetime import datetime

import pandas as pd

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.offre_realisee_config import MesureType


class FileSystemHandler(abc.ABC):
    @abc.abstractmethod
    def read_offre_realisee(self, **kwargs) -> pd.DataFrame:
        """Récupération des données d'offre réalisée.

        Parameters
        ----------
        **kwargs :
            Keyword arguments supplémentaires passés à la fonction pandas read_parquet.

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée.
        """
        pass

    @abc.abstractmethod
    def get_daily_offre_realisee(self, date: datetime) -> pd.DataFrame:
        """Récupération des données d'offre réalisée pour une date.

        Parameters
        ----------
        date : datetime
            Date pour laquelle nous voulons les données d'offre théorique.

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée.
        """
        pass

    @abc.abstractmethod
    def save_mesure_qs(
        self, df_mesure_qs: pd.DataFrame, date: datetime,
        aggregation_level: AggregationLevel, mesure_type: MesureType
    ) -> None:
        """Sauvegarde du DataFrame de mesure de Qualité de Service (QS).

        Parameters
        ----------
        df_mesure_qs : DataFrame
            DataFrame que nous voulons sauvegarder.
        date : datetime
            Date des données de mesure QS.
        aggregation_level : AggregationLevel
            Niveau d'aggrégation de la mesure QS (by_day, by_week, by_year, ...).
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).
        """
        pass

    @abc.abstractmethod
    def get_daily_mesure_qs(self, date: datetime, mesure_type: MesureType) -> pd.DataFrame:
        """Récupération des données de mesure QS par jour.

        Parameters
        ----------
        date : datetime
            Date des données de mesure QS.
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée par jour.
        """
        pass
