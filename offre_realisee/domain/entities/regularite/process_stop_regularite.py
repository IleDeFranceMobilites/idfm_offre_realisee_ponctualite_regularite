import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite
from offre_realisee.domain.entities.regularite.compliance_score import (
    calculate_compliance_score_for_each_borne)
from offre_realisee.domain.entities.regularite.compliance_score import choose_best_score
from offre_realisee.domain.entities.regularite.matching_heure_theorique_reelle_regularite import (
    matching_heure_theorique_reelle_regularite)


def process_stop_regularite(df_by_stop: pd.DataFrame, metadata_cols: list[str] = []) -> pd.DataFrame:
    """Calcule le score de conformité pour tous les passages d'un arrêt sur la période analysée.
    Les étapes de calcul sont les suivantes :
    1. Association d'un passage à l'heure réelle à 2 passages à l'heure théorique (inf.=précédent, sup.=suivant)
    2. Calcul du score de conformité en fonction de chacun des 2 passages à l'heure théorique
    3. Sélection du score de conformité le plus optimal en fonction des résultats précédents

    Parameters
    ----------
    df_by_stop : DataFrame
        DataFrame qui contient les données de passages réels et théoriques pour un arrêt sur toute la période analysée
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].

    Returns
    ----------
     df_score : DataFrame
        DataFrame qui contient les scores de conformité pour tous les passages d'un arrêt sur la période analysée
    """
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

    for metadata_column in metadata_cols:
        df_score[metadata_column] = df_by_stop[metadata_column].iloc[0]

    return df_score
