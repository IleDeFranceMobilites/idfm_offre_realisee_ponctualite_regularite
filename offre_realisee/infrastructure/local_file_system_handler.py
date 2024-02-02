import os
from datetime import datetime

import pandas as pd

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.config.aggregation_config import (AggregationLevel, suffix_by_agg)
from offre_realisee.domain.port.file_system_handler import FileSystemHandler

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MESURE_TYPE

from offre_realisee.config.logger import logger


class LocalFileSystemHandler(FileSystemHandler):

    def __init__(self, data_path: str, input_path: str, output_path: str, input_file_name: str):
        self.data_path = data_path
        self.input_path = input_path
        self.output_path = output_path
        self.input_file_name = input_file_name

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

    def get_daily_offre_realisee(self, date: datetime) -> pd.DataFrame:
        """Récupération des données d'offre réalisée pour une date.

        Parameters
        ----------
        date : datetime
            Date pour laquelle nous voulons les données d'offre théorique.

        Returns
        -------
        df_offre_realisee : DataFrame
            DataFrame d'offre réalisée.
        """
        filters = [(InputColumns.jour, 'in', {date.strftime("%Y-%m-%d")})]
        df_offre_realisee = self.read_offre_realisee(
            columns=[InputColumns.ligne, InputColumns.arret,
                     InputColumns.sens, InputColumns.heure_theorique,
                     InputColumns.heure_reelle, InputColumns.is_terminus],
            filters=filters
        )

        return df_offre_realisee

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
        mesure_qs = MESURE_TYPE[mesure_type]

        folder_path = os.path.join(self.data_path, self.output_path, aggregation_level, mesure_type)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        suffix = suffix_by_agg[aggregation_level](date)
        file_path = os.path.join(folder_path, f"mesure_{mesure_type}_{suffix}" + FileExtensions.csv)

        logger.info(f"Writing a dataframe of shape {df_mesure_qs.shape} in {file_path}")
        df_mesure_qs[mesure_qs.column_order].to_csv(file_path)

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
        suffix = suffix_by_agg[AggregationLevel.by_day](date)
        folder_path = os.path.join(
            self.data_path, self.output_path, AggregationLevel.by_day, mesure_type
        )
        file_path = os.path.join(folder_path, f"mesure_{mesure_type}_{suffix}" + FileExtensions.csv)

        logger.info(f"Reading daily mesure qs for date: {date.strftime('%Y-%m-%d')}, from: {file_path}")
        return pd.read_csv(file_path)
