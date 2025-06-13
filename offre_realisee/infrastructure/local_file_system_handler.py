import os
from datetime import date, datetime

import pandas as pd

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.calendrier_scolaire_config import PARQUET_ENGINE, PARQUET_COMPRESSION
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.domain.port.calendrier_scolaire_file_system_handler import CalendrierScolaireFileSystemHandler
from offre_realisee.domain.port.file_system_handler import FileSystemHandler

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MESURE_TYPE

from offre_realisee.config.logger import logger


class LocalFileSystemHandler(FileSystemHandler, CalendrierScolaireFileSystemHandler):

    def __init__(self, data_path: str, input_path: str, output_path: str, input_file_name: str,
                 calendrier_scolaire_file_name: str):
        self.data_path = data_path
        self.input_path = input_path
        self.output_path = output_path
        self.input_file_name = input_file_name
        self.calendrier_scolaire_file_name = calendrier_scolaire_file_name

    def read_offre_realisee(self, **kwargs) -> pd.DataFrame:
        """Récupération des données d'offre réalisée.

        Parameters
        ----------
        `**kwargs` :
            Keyword arguments supplémentaires passés à la fonction pandas read_parquet.

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée.
        """
        file_path = os.path.join(self.data_path, self.input_path, self.input_file_name)

        logger.info(f"Reading input data from: {file_path}")
        return pd.read_parquet(file_path, **kwargs)

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
        df_offre_realisee : DataFrame
            DataFrame d'offre réalisée.
        """
        filters = [[(InputColumns.jour, 'in', {date.strftime("%Y-%m-%d")})]]
        if dsp:
            filters[0].append((InputColumns.dsp, 'in', dsp))
        if ligne:
            filters[0].append((InputColumns.ligne, 'in', ligne))
        df_offre_realisee = self.read_offre_realisee(
            columns=[InputColumns.ligne, InputColumns.arret,
                     InputColumns.sens, InputColumns.heure_theorique,
                     InputColumns.heure_reelle, InputColumns.is_terminus],
            filters=filters
        )

        return df_offre_realisee

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
        mesure_qs = MESURE_TYPE[mesure_type]

        folder_path = os.path.join(self.data_path, self.output_path, dsp, mesure_type)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"mesure_{mesure_type}_{date.strftime('%Y_%m_%d')}" + FileExtensions.csv)

        logger.info(f"Writing a dataframe of shape {df_mesure_qs.shape} in {file_path}")
        df_mesure_qs[mesure_qs.column_order].to_csv(file_path)

    def save_mesure_qs_by_aggregation(
            self, df_mesure_qs: pd.DataFrame, suffix: str,
            date_range: tuple[date, date], dsp: str, aggregation_level: AggregationLevel,
            mesure_type: MesureType, periode_ete: tuple[str],
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
        list_journees_exceptionnelles : Optional[List[date]]
            La liste des journées exceptionnelles à exclure (ex: émeutes, grèves...). Par défaut, cette liste est vide.
        window_name : Optional[str]
            Nom de la fenêtre d'aggregation, optionnel par défaut égal à ""
        **kwargs : dict
            Arguments supplémentaires pour la sauvegarde, comme le niveau d'agrégation.
        """
        mesure_qs = MESURE_TYPE[mesure_type]

        folder_path = os.path.join(self.data_path, self.output_path, dsp, aggregation_level, mesure_type)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"mesure_{mesure_type}_{suffix}" + FileExtensions.csv)

        logger.info(f"Writing a dataframe of shape {df_mesure_qs.shape} in {file_path}")
        df_mesure_qs[mesure_qs.column_order].to_csv(file_path)

    def save_error_mesure_qs(self, df_mesure_qs: pd.DataFrame, date: date, mesure_type: MesureType, dsp: str,
                             ligne: str) -> None:
        mesure_qs = MESURE_TYPE[mesure_type]
        folder_path = os.path.join(self.data_path, self.output_path, dsp, mesure_type)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path,
                                 f"mesure_{mesure_type}_{ligne}_{date.strftime('%Y_%m_%d')}_error" +
                                 FileExtensions.csv)

        logger.info(f"Writing a dataframe of shape {df_mesure_qs.shape} in {file_path}")

        df_mesure_qs[mesure_qs.column_order].to_csv(file_path)

    def get_daily_mesure_qs(self, date: date, dsp: str, mesure_type: MesureType) -> pd.DataFrame:
        """Récupération des données de mesure QS par jour.

        Parameters
        ----------
        date : date
            Date des données de mesure QS.
        dsp : str
            DSP des données de mesure QS.
        mesure_type : MesureType
            Le type de mesure (ponctualite, regularite).

        Returns
        -------
        df : DataFrame
            DataFrame d'offre réalisée par jour.
        """
        folder_path = os.path.join(self.data_path, self.output_path, dsp, mesure_type)
        file_path = os.path.join(folder_path, f"mesure_{mesure_type}_{date.strftime('%Y_%m_%d')}" + FileExtensions.csv)

        logger.info(f"Reading daily mesure qs for date: {date.strftime('%Y-%m-%d')}, from: {file_path}")
        return pd.read_csv(file_path)

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
        file_path = os.path.join(self.data_path, self.input_path, self.calendrier_scolaire_file_name)

        logger.info(f"Reading input data from: {file_path}")
        return pd.read_parquet(file_path, **kwargs)

    def save_calendrier_scolaire(self, filtered_calendrier_scolaire: pd.DataFrame) -> None:
        """Sauvegarde les données du calendrier scolaire dans le dossier input.

        Parameters
        ----------
        filtered_calendrier_scolaire :
            DataFrame du calendrier scolaire.
        """
        file_path = os.path.join(self.data_path, self.input_path, self.calendrier_scolaire_file_name)
        logger.info(f"Saving holidays to {file_path}")
        filtered_calendrier_scolaire.to_parquet(file_path, engine=PARQUET_ENGINE, compression=PARQUET_COMPRESSION)
