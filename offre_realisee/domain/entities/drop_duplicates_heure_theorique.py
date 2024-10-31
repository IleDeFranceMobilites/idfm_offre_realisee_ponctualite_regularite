import pandas as pd

from offre_realisee.config.input_config import InputColumns


def drop_duplicates_heure_theorique(df_offre_realisee: pd.DataFrame) -> pd.DataFrame:
    df_offre_realisee = df_offre_realisee.sort_values(by=InputColumns.heure_reelle)
    df_offre_realisee = df_offre_realisee.drop_duplicates(subset=[
        InputColumns.ligne, InputColumns.jour, InputColumns.sens, InputColumns.arret, InputColumns.is_terminus,
        InputColumns.heure_theorique
    ])

    return df_offre_realisee.reset_index(drop=True)
