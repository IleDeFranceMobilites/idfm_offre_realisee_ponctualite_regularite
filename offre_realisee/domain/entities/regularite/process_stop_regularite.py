import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite
from offre_realisee.domain.entities.regularite.compliance_score import (
    calculate_compliance_score_for_each_borne)
from offre_realisee.domain.entities.regularite.compliance_score import choose_best_score
from offre_realisee.domain.entities.regularite.matching_heure_theorique_reelle_regularite import (
    matching_heure_theorique_reelle_regularite)


def process_stop_regularite(df_by_stop: pd.DataFrame):

    #  If no passage reel is present no regularity score is computed
    if df_by_stop[MesureRegularite.heure_reelle].count() == 0:
        return pd.DataFrame()

    #  If only one passage theorique is present no regularity score can be computed
    if df_by_stop[MesureRegularite.heure_theorique].count() <= 1:
        return pd.DataFrame()

    matched_df = matching_heure_theorique_reelle_regularite(df_by_stop)

    if all(matched_df[MesureRegularite.difference_reelle] != matched_df[
            MesureRegularite.difference_reelle]):
        return pd.DataFrame()

    df_score = calculate_compliance_score_for_each_borne(matched_df)

    df_score = choose_best_score(df_score)

    df_score[MesureRegularite.ligne] = df_by_stop[MesureRegularite.ligne].unique()[0]
    df_score[MesureRegularite.sens] = df_by_stop[MesureRegularite.sens].unique()[0]
    df_score[MesureRegularite.arret] = df_by_stop[MesureRegularite.arret].unique()[0]

    return df_score
