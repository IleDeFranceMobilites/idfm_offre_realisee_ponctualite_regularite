from datetime import timedelta

import pandas as pd

from offre_realisee.config.offre_realisee_config import MesurePonctualite, FrequenceType

FREQUENCY_THRESHOLD = timedelta(hours=1)


def add_frequency(df_by_stop: pd.DataFrame) -> pd.DataFrame:
    """Ajout d'une colonne de fréquence aux données de ponctualité par arrêt.

    Cette fonction prend en entrée un DataFrame contenant des données de ponctualité par arrêt et ajoute une colonne
    indiquant la fréquence de passage pour chaque enregistrement. La fréquence est déterminée en comparant la différence
    entre l'heure théorique actuelle et celle du cinquième passage suivant. Si cette différence est inférieure au seuil
    FREQUENCY_THRESHOLD (défini à 1h), la fréquence est considérée comme haute (HF), sinon elle est considérée comme
    basse (BF). Elle retourne le DataFrame modifié avec la colonne de fréquence ajoutée.

    Parameters
    ----------
    df_by_stop : pd.DataFrame
        DataFrame contenant les données de ponctualité par arrêt.

    Returns
    -------
    df_by_stop : DataFrame
        DataFrame modifié avec une colonne de fréquence ajoutée.
    """
    df_by_stop = df_by_stop.sort_values(by=MesurePonctualite.heure_theorique)
    heure_theorique_col = df_by_stop[MesurePonctualite.heure_theorique]

    difference_current_and_fifth_following = heure_theorique_col.dropna().diff(5).shift(-5)
    difference_under_threshold = difference_current_and_fifth_following < FREQUENCY_THRESHOLD
    difference_under_threshold_index = difference_under_threshold[difference_under_threshold].index

    df_by_stop.loc[heure_theorique_col.notna(), MesurePonctualite.frequence] = FrequenceType.basse_frequence
    df_by_stop.loc[difference_under_threshold_index, MesurePonctualite.frequence] = FrequenceType.haute_frequence

    if len(difference_under_threshold_index) > 0:
        df_by_stop[MesurePonctualite.tag_frequence] = FrequenceType.haute_frequence
    else:
        df_by_stop[MesurePonctualite.tag_frequence] = FrequenceType.basse_frequence

    return df_by_stop
