import abc
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
    def get_daily_mesure_qs(self, date: date, dsp: str, mesure_type: MesureType, **kwargs) -> pd.DataFrame:
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
        **kwargs : dict
            Options complémentaires de lecture.

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée par jour.
        """
        pass

    @abc.abstractmethod
    def save_mesure_qs_by_aggregation(
        self, df_mesure_qs: pd.DataFrame, suffix: str, date_range: tuple[date, date], dsp: str,
        aggregation_level: AggregationLevel, mesure_type: MesureType, periode_ete: tuple[str],
        list_journees_exceptionnelles: list[date], window_name: str = "",
        **kwargs
    ) -> None:
        """Sauvegarde du DataFrame de mesure de Qualité de Service (QS).

        Parameters
        ----------
        df_mesure_qs : DataFrame
            DataFrame que nous voulons sauvegarder.
        suffix: str
            Suffix de l'agrégation, par exemple '2024_01' pour une agrégation mensuelle.
        date_range : Tuple[date, date]
            Plage de dates pour l'agrégation.
        dsp : str
            DSP à agréger.
        aggregation_level : AggregationLevel
            Niveau d'agrégation des données.
        mesure_type : MesureType
            Type de mesure à agréger (ponctualite ou regularite).
        periode_ete : tuple[date, date]
            Période d'été sous forme de tuple (début, fin) - Requis si l'aggregation concerne une period.
        list_journees_exceptionnelles : Optional[List[date]]
            La liste des journées exceptionnelles à exclure (ex: émeutes, grèves...). Par défaut, cette liste est vide.
        window_name : Optional[str]
            Nom de la fenêtre d'aggregation, optionnel par défaut égal à ""
        **kwargs : dict
            Options complémentaires d'écriture.
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
