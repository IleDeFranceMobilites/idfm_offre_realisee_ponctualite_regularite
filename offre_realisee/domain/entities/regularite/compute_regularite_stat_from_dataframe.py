from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.logger import logger
from offre_realisee.config.offre_realisee_config import FrequenceType, MesureRegularite
from offre_realisee.domain.entities.add_frequency import add_frequency
from offre_realisee.domain.entities.drop_duplicates_heure_theorique import drop_duplicates_heure_theorique
from offre_realisee.domain.entities.drop_stop_without_real_time import drop_stop_without_real_time
from offre_realisee.domain.entities.regularite.process_stop_regularite import process_stop_regularite
from offre_realisee.domain.entities.regularite.stat_compliance_score_regularite import stat_compliance_score_regularite


import pandas as pd


from collections import defaultdict


def compute_regularite_stat_from_dataframe(
    df_offre_realisee: pd.DataFrame, metadata_cols: list[str] = [],
) -> pd.DataFrame:
    """Calcule les statistiques de régularité à partir d'un DataFrame d'offre réalisée.

    Parameters
    ----------
    df_offre_realisee : DataFrame
        DataFrame contenant les données d'offre réalisée.
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].
    """
    df_offre_realisee = drop_duplicates_heure_theorique(df_offre_realisee)

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
        score_by_stop_regularite = process_stop_regularite(
            df_by_stop=df_by_stop,
            metadata_cols=[MesureRegularite.ligne, MesureRegularite.sens, MesureRegularite.arret] + metadata_cols
        )
        if not score_by_stop_regularite.empty:
            df_concat_regularite = pd.concat([df_concat_regularite, score_by_stop_regularite], ignore_index=True)
            theorique_passages_by_lignes[ligne] += df_by_stop[InputColumns.heure_theorique].notna().sum()

        if any(df_by_stop[MesureRegularite.frequence] == FrequenceType.haute_frequence):
            any_high_frequency_on_lignes[ligne] = True
    if df_concat_regularite.empty:
        return pd.DataFrame()
    return stat_compliance_score_regularite(
        df_concat_regularite, theorique_passages_by_lignes, any_high_frequency_on_lignes, metadata_cols=metadata_cols)
