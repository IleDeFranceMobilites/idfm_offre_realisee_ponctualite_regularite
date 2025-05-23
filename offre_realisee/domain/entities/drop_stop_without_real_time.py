import pandas as pd

from offre_realisee.config.input_config import InputColumns


def drop_stop_without_real_time(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les arrêts sans heure réelle du DataFrame.

    Parameters
    ----------
    df : DataFrame
        DataFrame ayant une colonne d'heure réelle.

    Returns
    -------
    df : DataFrame
        DataFrame filtré excluant les arrêts sans heure réelle.
    """
    if df[InputColumns.heure_reelle].isna().all():
        return df
    return df.groupby(InputColumns.arret).filter(
        lambda x: x[InputColumns.heure_reelle].notna().any()
    )
