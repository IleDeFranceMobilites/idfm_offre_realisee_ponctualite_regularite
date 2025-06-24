from datetime import date
from functools import partial

import pandas as pd
from multiprocess import Pool

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.logger import logger
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.port.file_system_handler import FileSystemHandler
from offre_realisee.domain.entities.ponctualite.compute_ponctualite_stat_from_dataframe import (
    compute_ponctualite_stat_from_dataframe)


NUMBER_OF_PARALLEL_PROCESS: int = 6


def create_mesure_qs_ponctualite(
    file_system_handler: FileSystemHandler,
    date: date, dsp: str = "", ligne: str = "", metadata_cols: list[str] = []
) -> None:
    """Crée et sauvegarde les mesures de qualité de service de type ponctualité.

    Cette fonction récupère les données d'offre réalisée pour une date donnée, effectue des calculs de ponctualité pour
    chaque arrêt, agrège les résultats et sauvegarde le DataFrame résultant.

    Parameters
    ----------
    file_system_handler : FileSystemHandler
        Gestionnaire du système de fichiers.
    date : date
        Date pour laquelle les mesures de qualité de service doivent être calculées.
    dsp : str
        DSP pour laquelle les mesures de qualité de service doivent être calculées, par défaut à "".
    ligne : str
        Ligne pour laquelle les mesures de qualité de service doivent être calculées, par défaut à "".
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].
    """

    logger.info(f'Process: {date.strftime("%Y-%m-%d")}')

    try:
        df_offre_realisee = file_system_handler.get_daily_offre_realisee(date=date, dsp=dsp, ligne=ligne)
    except FileNotFoundError:
        logger.info(f'No data to process for {date.strftime("%Y-%m-%d")} with dsp: [{dsp}] and ligne: [{ligne}]')
        return
    if (df_offre_realisee[InputColumns.heure_theorique].isna().all() or
            df_offre_realisee[InputColumns.sens].isna().any() or df_offre_realisee[InputColumns.arret].isna().any()):
        file_system_handler.save_error_mesure_qs(
            df_mesure_qs=df_offre_realisee, date=date, mesure_type=MesureType.ponctualite, dsp=dsp, ligne=ligne)
    else:
        df_stat_ponctualite = compute_ponctualite_stat_from_dataframe(
            df_offre_realisee=df_offre_realisee, metadata_cols=metadata_cols)
        file_system_handler.save_daily_mesure_qs(
            df_mesure_qs=df_stat_ponctualite, date=date, dsp=dsp, mesure_type=MesureType.ponctualite
        )


def create_mesure_qs_ponctualite_date_range(
        file_system_handler: FileSystemHandler,
        date_range: tuple[date, date], dsp: str = "", ligne: str = "", metadata_cols: list[str] = [],
        n_thread: int = NUMBER_OF_PARALLEL_PROCESS
) -> None:
    """Appelle la fonction create_mesure_qs_ponctualite sur une plage de date, en parallélisant les calculs.

    Parameters
    ----------
    file_system_handler : FileSystemHandler
        Gestionnaire du système de fichiers.
    date_range : datetime
        Dates de début et de fin pour laquelle les mesures de qualité de service doivent être calculées.
    dsp : str
        DSP pour laquelle les mesures de qualité de service doivent être calculées, par défaut à "".
    ligne : str
        Ligne pour laquelle les mesures de qualité de service doivent être calculées, par défaut à "".
    n_thread: int
        Nombre de processus en parallèle.
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].
    """
    date_range_list = pd.date_range(start=date_range[0], end=date_range[1])

    create_mesure_qs_ponctualite_partial = partial(
        create_mesure_qs_ponctualite,
        file_system_handler=file_system_handler, dsp=dsp, ligne=ligne, metadata_cols=metadata_cols
    )

    with Pool(processes=n_thread) as pool:
        pool.map(lambda date: create_mesure_qs_ponctualite_partial(date=date), date_range_list)
