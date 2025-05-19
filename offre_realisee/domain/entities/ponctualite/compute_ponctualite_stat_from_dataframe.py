from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.logger import logger
from offre_realisee.domain.entities.add_frequency import add_frequency
from offre_realisee.domain.entities.drop_duplicates_heure_theorique import drop_duplicates_heure_theorique
from offre_realisee.domain.entities.drop_stop_without_real_time import drop_stop_without_real_time
from offre_realisee.domain.entities.ponctualite.process_stop_ponctualite import process_stop_ponctualite
from offre_realisee.domain.entities.ponctualite.stat_compliance_score_ponctualite import (
    stat_compliance_score_ponctualite)


import pandas as pd


def compute_ponctualite_stat_from_dataframe(
    df_offre_realisee: pd.DataFrame, metadata_cols: list[str] = []
) -> pd.DataFrame:
    """Calcule les statistiques de ponctualité à partir d'un DataFrame d'offre réalisée.

    Parameters
    ----------
    df_offre_realisee : DataFrame
        DataFrame contenant les données d'offre réalisée.
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].

    Returns
    -------
    df : DataFrame
        DataFrame contenant les statistiques de conformité pour chaque ligne.
    """
    df_offre_realisee = drop_duplicates_heure_theorique(df_offre_realisee)

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

    return stat_compliance_score_ponctualite(df=df_concat_ponctualite, metadata_cols=metadata_cols)
