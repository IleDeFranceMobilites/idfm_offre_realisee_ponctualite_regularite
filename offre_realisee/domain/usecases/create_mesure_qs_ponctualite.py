from datetime import datetime
from functools import partial
from typing import Tuple

import pandas as pd
from multiprocess import Pool

from offre_realisee.config.logger import logger
from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.entities.drop_stop_without_real_time import drop_stop_without_real_time
from offre_realisee.domain.entities.add_frequency import add_frequency
from offre_realisee.domain.entities.ponctualite.stat_compliance_score_ponctualite import (
    stat_compliance_score_ponctualite)
from offre_realisee.domain.entities.ponctualite.process_stop_ponctualite import process_stop_ponctualite
from offre_realisee.domain.port.file_system_handler import FileSystemHandler


NUMBER_OF_PARALLEL_PROCESS = 6


def create_mesure_qs_ponctualite(file_system_handler: FileSystemHandler, date: datetime):
    """Crée et sauvegarde les mesures de qualité de service de type ponctualité.

    Cette fonction récupère les données d'offre réalisée pour une date donnée, effectue des calculs de ponctualité pour
    chaque arrêt, agrège les résultats et sauvegarde le DataFrame résultant.

    Parameters
    ----------
    file_system_handler : FileSystemHandler
        Gestionnaire du système de fichiers.
    date : datetime
        Date pour laquelle les mesures de qualité de service doivent être calculées.
    """

    logger.info(f'Process: {date.strftime("%Y-%m-%d")}')
    df_offre_realisee = file_system_handler.get_daily_offre_realisee(date=date)

    df_offre_realisee = drop_stop_without_real_time(df_offre_realisee)
    df_grouped = df_offre_realisee.groupby(by=[
        InputColumns.ligne, InputColumns.sens, InputColumns.arret
    ])

    df_concat_ponctualite = pd.DataFrame()
    for (ligne, sens, arret), df_by_stop in df_grouped:
        logger.debug(f'Process: ligne {ligne} - sens {sens} - arret {arret}')

        df_by_stop = add_frequency(df_by_stop)

        logger.debug('Ponctualite')
        score_by_stop_ponctualite = process_stop_ponctualite(df_by_stop)
        if not score_by_stop_ponctualite.empty:
            df_concat_ponctualite = pd.concat([df_concat_ponctualite, score_by_stop_ponctualite], ignore_index=True)

    df_stat_ponctualite = stat_compliance_score_ponctualite(df_concat_ponctualite)
    file_system_handler.save_mesure_qs(
        df_stat_ponctualite, date, AggregationLevel.by_day, MesureType.ponctualite
    )


def create_mesure_qs_ponctualite_date_range(
        file_system_handler: FileSystemHandler, date_range: Tuple[datetime, datetime],
        n_thread: int = NUMBER_OF_PARALLEL_PROCESS
) -> None:
    """Appelle la fonction create_mesure_qs_ponctualite sur une plage de date, en parallélisant les calculs.

    Parameters
    ----------
    file_system_handler : FileSystemHandler
        Gestionnaire du système de fichiers.
    date_range : datetime
        Dates de début et de fin pour laquelle les mesures de qualité de service doivent être calculées.
    n_thread: int
        Nombre de processus en parallèle.
    """
    date_range_list = pd.date_range(start=date_range[0], end=date_range[1])

    create_mesure_qs_ponctualite_partial = partial(
        create_mesure_qs_ponctualite,
        file_system_handler
    )

    with Pool(processes=n_thread) as pool:
        pool.map(create_mesure_qs_ponctualite_partial, date_range_list)
