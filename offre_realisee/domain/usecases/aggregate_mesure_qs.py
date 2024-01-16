from datetime import datetime
from typing import List, Tuple

import pandas as pd

from offre_realisee.config.logger import logger
from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.offre_realisee_config import MesureType, Mesure, MESURE_TYPE
from offre_realisee.domain.entities.aggregation.generate_date_aggregation_lists import (
    generate_date_aggregation_lists)
from offre_realisee.domain.port.file_system_handler import FileSystemHandler


def aggregate_mesure_qs(file_system_handler: FileSystemHandler, date_range: Tuple[datetime, datetime],
                        aggregation_level: AggregationLevel, mesure_type: MesureType):
    dict_date_lists = generate_date_aggregation_lists(date_range, aggregation_level)

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
    grouped_df = df_all_mesure.groupby(mesure.ligne)

    columns_to_sum = [
        mesure.nombre_theorique,
        mesure.nombre_reel,
        mesure.score_de_conformite,
        *mesure.situation_inacceptable_types
    ]

    df_aggregated = grouped_df[columns_to_sum].sum()

    df_aggregated[mesure.taux_de_conformite] = (
            df_aggregated[mesure.score_de_conformite] / df_aggregated[mesure.nombre_theorique] * 100)

    df_aggregated[mesure.taux_absence_de_donnees] = (
            (df_aggregated[mesure.nombre_theorique] - df_aggregated[mesure.nombre_reel]) /
            df_aggregated[mesure.nombre_theorique] * 100
    )

    return df_aggregated.reset_index()
