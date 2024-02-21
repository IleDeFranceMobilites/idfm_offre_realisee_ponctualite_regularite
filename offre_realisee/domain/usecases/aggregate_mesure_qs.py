from datetime import datetime
from typing import List, Tuple, Optional

import pandas as pd

from offre_realisee.config.logger import logger
from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.offre_realisee_config import MesureType, Mesure, MESURE_TYPE
from offre_realisee.domain.entities.aggregation.generate_date_aggregation_lists import (
    generate_date_aggregation_lists)
from offre_realisee.domain.port.file_system_handler import FileSystemHandler


def aggregate_mesure_qs(file_system_handler: FileSystemHandler, date_range: Tuple[datetime, datetime],
                        aggregation_level: AggregationLevel, mesure_type: MesureType,
                        list_journees_exceptionnelles: Optional[List[datetime]] = None) -> None:
    """Agrège les mesures journalières de la qualité de service et les sauvegarde selon les spécifications fournies.

    Agrège les dates contenu dans la plage de données date_range en fonction du type de mesure: ponctualité ou
    régularité.

    Parameters
    ----------
    file_system_handler : FileSystemHandler
        Gestionnaire du système de fichiers.
    date_range : Tuple[datetime, datetime]
        Plage de dates pour l'agrégation.
    aggregation_level : AggregationLevel
        Niveau d'agrégation des données.
    mesure_type : MesureType
        Type de mesure à agréger (ponctualite ou regularite).
    list_journees_exceptionnelles : Optional[List[datetime]]
        La liste des journées exceptionnelles à excluse (ex: émeutes, grèves...). Par défaut, cette liste est vide.
    """

    dict_date_lists = generate_date_aggregation_lists(date_range, aggregation_level, list_journees_exceptionnelles)

    for suffix, date_list in dict_date_lists.items():
        logger.info(f"Processing {mesure_type} aggregation: {suffix}")
        mesure_list: List[pd.DataFrame] = []

        for date_to_agg in date_list:
            df = file_system_handler.get_daily_mesure_qs(date=date_to_agg, mesure_type=mesure_type)
            mesure_list.append(df)

        df_all_mesure = pd.concat(mesure_list)
        df_aggregated = aggregate_df(df_all_mesure, MESURE_TYPE[mesure_type])
        file_system_handler.save_mesure_qs(df_aggregated, date_list[0], aggregation_level, mesure_type)


def aggregate_df(df_all_mesure: pd.DataFrame, mesure: Mesure) -> pd.DataFrame:
    """Agrège les mesures de la qualité de service.

    Cette fonction prend un DataFrame de toutes les mesures quotidiennes de qualité de service et agrège ces mesures par
    lignes. Les colonnes agrégées incluent le nombre théorique, le nombre réel, le score de conformité, et les types de
    situations inacceptables. De plus, elle calcule le taux de conformité et le taux d'absence de données.

    Parameters
    ----------
    df_all_mesure : pd.DataFrame
        DataFrame contenant les mesures quotidiennes de qualité de service.
    mesure : Mesure
        Objet Mesure spécifiant les colonnes à agréger.

    Returns
    -------
    pd.DataFrame: DataFrame agrégé des mesures de qualité de service.
    """
    grouped_df = df_all_mesure.groupby(mesure.ligne)

    columns_to_sum = [
        mesure.nombre_theorique,
        mesure.nombre_reel,
        mesure.score_de_conformite,
        *mesure.situation_inacceptable_types
    ]

    df_aggregated = grouped_df[columns_to_sum].sum()

    df_aggregated[mesure.taux_de_conformite] = round(
            df_aggregated[mesure.score_de_conformite] / df_aggregated[mesure.nombre_theorique] * 100, 2
    )

    df_aggregated[mesure.taux_absence_de_donnees] = round(
            (df_aggregated[mesure.nombre_theorique] - df_aggregated[mesure.nombre_reel]) /
            df_aggregated[mesure.nombre_theorique] * 100, 2
    )

    return df_aggregated.reset_index()
