from datetime import date
from functools import partial

import pandas as pd
from multiprocess import Pool

from offre_realisee.config.logger import logger
from offre_realisee.domain.entities.preparation.transform_offre_realisee_brute import transform_offre_realisee_brute
from offre_realisee.domain.port.offre_realisee_brute_file_system_handler import OffreRealiseeBruteFileSystemHandler


NUMBER_OF_PARALLEL_PROCESS: int = 6


def prepare_offre_realisee(
    file_system_handler: OffreRealiseeBruteFileSystemHandler,
    date: date
) -> None:
    """Transforme et sauvegarde les données brutes d'offre réalisée au format attendu par le calcul des mesures.

    Cette fonction récupère les données brutes livrées par le transporteur pour une date donnée, les transforme
    (passages évaluables, fusion des heures de départ et d'arrivée, localisation en UTC) et sauvegarde le DataFrame
    résultant dans le dataset d'entrée partitionné par jour.

    Parameters
    ----------
    file_system_handler : OffreRealiseeBruteFileSystemHandler
        Gestionnaire du système de fichiers.
    date : date
        Date pour laquelle les données brutes doivent être préparées.
    """

    logger.info(f'Process: {date.strftime("%Y-%m-%d")}')

    try:
        df_offre_realisee_brute = file_system_handler.get_daily_offre_realisee_brute(date=date)
    except FileNotFoundError:
        logger.info(f'No raw data to process for {date.strftime("%Y-%m-%d")}')
        return

    df_offre_realisee = transform_offre_realisee_brute(df_offre_realisee_brute)

    # Si aucun passage n'est évaluable, il n'y a rien à calculer sur cette journée.
    if df_offre_realisee.empty:
        logger.info(f'No evaluable data to save for {date.strftime("%Y-%m-%d")}')
        return

    file_system_handler.save_daily_offre_realisee(df_offre_realisee=df_offre_realisee, date=date)


def prepare_offre_realisee_date_range(
        file_system_handler: OffreRealiseeBruteFileSystemHandler,
        date_range: tuple[date, date], n_thread: int = NUMBER_OF_PARALLEL_PROCESS
) -> None:
    """Appelle la fonction prepare_offre_realisee sur une plage de date, en parallélisant les traitements.

    Parameters
    ----------
    file_system_handler : OffreRealiseeBruteFileSystemHandler
        Gestionnaire du système de fichiers.
    date_range : tuple[date, date]
        Dates de début et de fin pour lesquelles les données brutes doivent être préparées.
    n_thread: int
        Nombre de processus en parallèle.
    """
    date_range_list = pd.date_range(start=date_range[0], end=date_range[1])

    prepare_offre_realisee_partial = partial(prepare_offre_realisee, file_system_handler=file_system_handler)

    with Pool(processes=n_thread) as pool:
        pool.map(lambda date: prepare_offre_realisee_partial(date=date), date_range_list)
