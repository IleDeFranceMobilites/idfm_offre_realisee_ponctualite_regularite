import pandas as pd

from offre_realisee.config.input_config import InputColumns


def drop_duplicates_heure_theorique(df_offre_realisee: pd.DataFrame) -> pd.DataFrame:
    """Suppression des heures théoriques dupliquées. Si une heure théorique non null (pour un arrêt/sens/ligne) est lié
    à deux heure réelle, on prend la première heure réelle. Si la colonne heure théorique est null, dans ce cas, on
    fait un drop duplicates classique.

    Cette fonction prend en entrée un DataFrame contenant les données d'offre réalisée, et renvoie un DataFrame de ces
    données sans doublons dans les heures théoriques.

    Parameters
    ----------
    df_offre_realisee : pd.DataFrame
        DataFrame contenant les données d'offre réalisée.

    Returns
    -------
    df_offre_realisee : DataFrame
        DataFrame dédupliqué.
    """
    df_offre_realisee = df_offre_realisee.drop_duplicates()
    mask = df_offre_realisee[InputColumns.heure_theorique].notnull()

    df_offre_realisee_not_null = df_offre_realisee[mask].sort_values(by=InputColumns.heure_reelle).drop_duplicates(
        subset=[InputColumns.ligne, InputColumns.sens, InputColumns.arret, InputColumns.is_terminus,
                InputColumns.heure_theorique]
    )

    return pd.concat([df_offre_realisee_not_null, df_offre_realisee[~mask]])
