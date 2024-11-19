from datetime import datetime
from typing import Optional

import pandas as pd

from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import generate_suffix_by_aggregation
from offre_realisee.config.logger import logger
from offre_realisee.config.aggregation_config import DEFAULT_PERIODE_ETE, AggregationLevel
from offre_realisee.config.offre_realisee_config import (MesureType, Mesure, MESURE_TYPE, MesurePonctualite,
                                                         MesureRegularite)
from offre_realisee.domain.entities.aggregation.generate_date_aggregation_lists import (
    generate_date_aggregation_lists)
from offre_realisee.domain.port.file_system_handler import FileSystemHandler


def aggregate_mesure_qs(file_system_handler: FileSystemHandler, date_range: tuple[datetime, datetime], dsp: str,
                        aggregation_level: AggregationLevel, mesure_type: MesureType,
                        periode_ete: tuple[str] = DEFAULT_PERIODE_ETE,
                        list_journees_exceptionnelles: Optional[list[datetime]] = None,
                        window_name: str = "") -> None:
    """Agrège les mesures journalières de la qualité de service et les sauvegarde selon les spécifications fournies.

    Agrège les dates contenu dans la plage de données date_range en fonction du type de mesure: ponctualité ou
    régularité.

    Parameters
    ----------
    file_system_handler : FileSystemHandler
        Gestionnaire du système de fichiers.
    date_range : Tuple[datetime, datetime]
        Plage de dates pour l'agrégation.
    dsp : str
        DSP à agréger.
    aggregation_level : AggregationLevel
        Niveau d'agrégation des données.
    mesure_type : MesureType
        Type de mesure à agréger (ponctualite ou regularite).
    list_journees_exceptionnelles : Optional[List[datetime]]
        La liste des journées exceptionnelles à exclure (ex: émeutes, grèves...). Par défaut, cette liste est vide.
    window_name : Optional[str]
        Nom de la fenêtre d'aggregation, optionnel par défaut égal à ""
    """

    df_calendrier_scolaire = file_system_handler.get_calendrier_scolaire()
    suffix_by_agg = generate_suffix_by_aggregation(
        df_calendrier_scolaire=df_calendrier_scolaire, periode_ete=periode_ete, window_name=window_name)
    dict_date_lists = generate_date_aggregation_lists(
        date_range=date_range, aggregation_level=aggregation_level, suffix_by_agg=suffix_by_agg,
        list_journees_exceptionnelles=list_journees_exceptionnelles
    )

    for suffix, date_list in dict_date_lists.items():
        logger.info(f"Processing {mesure_type} aggregation: {suffix}")
        mesure_list: list[pd.DataFrame] = []

        for date_to_agg in date_list:
            df = file_system_handler.get_daily_mesure_qs(date=date_to_agg, dsp=dsp, mesure_type=mesure_type,
                                                         suffix_by_agg=suffix_by_agg)
            mesure_list.append(df)

        if len(mesure_list) != 0:
            df_all_mesure = pd.concat(mesure_list)
            df_aggregated = aggregate_df(df_all_mesure, MESURE_TYPE[mesure_type])
        elif mesure_type == MesureType.ponctualite:
            df_aggregated = pd.DataFrame(columns=MesurePonctualite.column_order)
        else:
            df_aggregated = pd.DataFrame(columns=MesureRegularite.column_order)
        file_system_handler.save_mesure_qs_by_aggregation(
            df_mesure_qs=df_aggregated, date=date_list[0], dsp=dsp,
            aggregation_level=aggregation_level, mesure_type=mesure_type, suffix_by_agg=suffix_by_agg
        )


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
