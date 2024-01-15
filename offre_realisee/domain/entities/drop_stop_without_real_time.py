import pandas as pd

from offre_realisee.config.input_config import InputColumns


def drop_stop_without_real_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(InputColumns.arret).filter(
        lambda x: x[InputColumns.heure_reelle].notna().any()
    )
