import abc
from typing import Callable
from datetime import date

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
    def get_daily_offre_realisee(self, date: date, dsp: str = "", ligne: str = "") -> pd.DataFrame:
        """Récupération des données d'offre réalisée pour une date.

        Parameters
        ----------
        date : date
            Date pour laquelle nous voulons les données d'offre théorique.
        dsp : str
            DSP pour laquelle les mesures de qualité de service doivent être calculées, par défaut à "".
        ligne : str
            Ligne pour laquelle les mesures de qualité de service doivent être calculées, par défaut à "".

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée.
        """
        pass

    @abc.abstractmethod
    def save_daily_mesure_qs(
        self, df_mesure_qs: pd.DataFrame, date: date, dsp: str, mesure_type: MesureType
    ) -> None:
        """Sauvegarde du DataFrame de mesure de Qualité de Service (QS).

        Parameters
        ----------
        df_mesure_qs : DataFrame
            DataFrame que nous voulons sauvegarder.
        date : date
            Date des données de mesure QS.
        dsp : str
            DSP des données de mesure QS.
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).
        """
        pass

    @abc.abstractmethod
    def save_error_mesure_qs(
            self, df_mesure_qs: pd.DataFrame, date: date, mesure_type: MesureType, dsp: str, ligne: str
    ) -> None:
        """Sauvegarde du DataFrame de mesure de Qualité de Service (QS) en erreur.

        Parameters
        ----------
        df_mesure_qs : DataFrame
            DataFrame que nous voulons sauvegarder.
        date : date
            Date des données de mesure QS.
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).
        dsp : str
            DSP des données de mesure QS.
        ligne : str
            Ligne des données de mesure QS
        """
        pass

    @abc.abstractmethod
    def save_mesure_qs_by_aggregation(
        self, df_mesure_qs: pd.DataFrame, date: date, dsp: str,
        aggregation_level: AggregationLevel, mesure_type: MesureType,
        suffix_by_agg: dict[AggregationLevel, Callable]
    ) -> None:
        """Sauvegarde du DataFrame de mesure de Qualité de Service (QS).

        Parameters
        ----------
        df_mesure_qs : DataFrame
            DataFrame que nous voulons sauvegarder.
        date : date
            Date des données de mesure QS.
        dsp : str
            DSP des données de mesure QS.
        aggregation_level : AggregationLevel
            Niveau d’agrégation de la mesure QS (by_week, by_year, ...).
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).
        suffix_by_agg: Dict[AggregationLevel, Callable]
            Dictionnaire de fonction de génération de suffix basé sur la date et le calendrier scolaire.
        """
        pass

    @abc.abstractmethod
    def get_daily_mesure_qs(self, date: date, dsp: str, mesure_type: MesureType,
                            suffix_by_agg: dict[AggregationLevel, Callable]) -> pd.DataFrame:
        """Récupération des données de mesure QS par jour.

        Parameters
        ----------
        date : date
            Date des données de mesure QS.
        dsp : str
            DSP des données de mesure QS.
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).
        suffix_by_agg: Dict[AggregationLevel, Callable]
            Dictionnaire de fonction de génération de suffix basé sur la date et le calendrier scolaire.

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée par jour.
        """
        pass

    @abc.abstractmethod
    def get_calendrier_scolaire(self, **kwargs) -> pd.DataFrame:
        """Récupération des données de calendrier scolaire.

        Parameters
        ----------
        **kwargs :
            Keyword arguments supplémentaires passés à la fonction pandas read_parquet.

        Returns
        -------
        df : DataFrame
            DataFrame du calendrier scolaire.
        """
        pass
