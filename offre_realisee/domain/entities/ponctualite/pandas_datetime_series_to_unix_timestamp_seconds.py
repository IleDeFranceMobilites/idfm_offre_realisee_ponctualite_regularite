import pandas as pd


from datetime import UTC


def pandas_datetime_series_to_unix_timestamp_seconds(series: pd.Series) -> pd.Series:
    """Convertit une série de timestamps pandas en secondes depuis l'époque Unix.

    Parameters
    ----------
    series : pd.Series
        Série de timestamps pandas.

    Returns
    -------
    pd.Series
        Série de timestamps convertis en secondes depuis l'époque Unix.
    """
    return (series - pd.Timestamp('1970-01-01', tz=UTC)) // pd.Timedelta(seconds=1)
