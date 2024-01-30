from datetime import datetime
from collections import defaultdict
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
from offre_realisee.domain.entities.regularite.stat_compliance_score_regularite import (
    stat_compliance_score_regularite)
from offre_realisee.domain.entities.regularite.process_stop_regularite import process_stop_regularite
from offre_realisee.domain.port.file_system_handler import FileSystemHandler

from offre_realisee.config.offre_realisee_config import MesureRegularite, FrequenceType


NUMBER_OF_PARALLEL_PROCESS = 6


def create_mesure_qs_regularite(
        file_system_handler: FileSystemHandler, date: datetime
):
    """Crée et sauvegarde les mesures de qualité de service de type régularité.

    Cette fonction récupère les données d'offre réalisée pour une date donnée, effectue des calculs de régularité pour
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

    df_concat_regularite = pd.DataFrame()
    theorique_passages_by_lignes = defaultdict(int)
    any_high_frequency_on_lignes = defaultdict(bool)
    for (ligne, sens, arret), df_by_stop in df_grouped:
        logger.debug(f'Process: ligne {ligne} - sens {sens} - arret {arret}')

        df_by_stop = add_frequency(df_by_stop)

        logger.debug('Regularite')
        score_by_stop_regularite = process_stop_regularite(df_by_stop)
        if not score_by_stop_regularite.empty:
            df_concat_regularite = pd.concat([df_concat_regularite, score_by_stop_regularite], ignore_index=True)
            theorique_passages_by_lignes[ligne] += df_by_stop[InputColumns.heure_theorique].notna().sum()

        if any(df_by_stop[MesureRegularite.frequence] == FrequenceType.haute_frequence):
            any_high_frequency_on_lignes[ligne] = True

    df_stat_regularite = stat_compliance_score_regularite(df_concat_regularite, theorique_passages_by_lignes,
                                                          any_high_frequency_on_lignes)
    file_system_handler.save_mesure_qs(
        df_stat_regularite, date, AggregationLevel.by_day, MesureType.regularite
    )


def create_mesure_qs_regularite_date_range(
        file_system_handler: FileSystemHandler, date_range: Tuple[datetime, datetime],
        n_thread: int = NUMBER_OF_PARALLEL_PROCESS
) -> None:
    """Appelle la fonction create_mesure_qs_regularite sur une plage de date, en parallélisant les calculs.

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

    create_mesure_qs_regularite_partial = partial(
        create_mesure_qs_regularite,
        file_system_handler
    )

    with Pool(processes=n_thread) as pool:
        pool.map(create_mesure_qs_regularite_partial, date_range_list)
