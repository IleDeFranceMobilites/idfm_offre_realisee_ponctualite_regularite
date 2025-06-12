from datetime import date, datetime
from typing import Callable
from zoneinfo import ZoneInfo

import pandas as pd
from workalendar.europe import France

from offre_realisee.config.aggregation_config import AggregationLevel, PeriodeName, CalendrierScolaireColumns


IDF_TIMEZONE = ZoneInfo("Europe/Paris")


def get_period_name(date: date, df_calendrier_scolaire: pd.DataFrame, periode_ete: tuple[date, date]) -> str:
    """
    Récupère le nom de la période en fonction de la date donnée et du calendrier scolaire.
    La période peut être 'plein_trafic', 'vacances_scolaires', 'ete' ou 'scolaire'.

    Parameters
    ----------
    date : date
        La date pour laquelle nous voulons récupérer le nom de la période.
    df_calendrier_scolaire : DataFrame
        DataFrame contenant le calendrier scolaire.
    periode_ete : tuple[date, date]
        Période d'été sous forme de tuple (début, fin).
    """

    if date >= periode_ete[0] and date <= periode_ete[1]:
        return PeriodeName.ete

    date_as_localized_datetime = datetime(date.year, date.month, date.day, tzinfo=IDF_TIMEZONE)

    df_filtered = df_calendrier_scolaire[df_calendrier_scolaire[
        CalendrierScolaireColumns.description].str.startswith('Vacances')]
    row = df_filtered[
        (pd.to_datetime(df_filtered[CalendrierScolaireColumns.start_date]) <= date_as_localized_datetime) &
        (pd.to_datetime(df_filtered[CalendrierScolaireColumns.end_date]) > date_as_localized_datetime)
    ]
    if row.empty:
        return PeriodeName.plein_trafic
    else:
        return PeriodeName.vacances_scolaires


def generate_suffix_by_aggregation(
    df_calendrier_scolaire: pd.DataFrame, periode_ete: tuple[date, date] | None = None, window_name: str = ""
) -> dict:
    """
    Génère un dictionnaire de suffixes basés sur la date et le calendrier scolaire.

    Parameters
    ----------
    df_calendrier_scolaire : pd.DataFrame
        DataFrame contenant le calendrier scolaire.
    periode_ete : tuple[date, date], optional
        Période d'été sous forme de tuple (début, fin) - Requis si l'aggregation concerne une period.
    window_name : str, optional
        Nom de la fenêtre, par défaut "".
        Si une fenêtre est spécifiée, elle sera ajoutée au suffixe pour les niveaux d'agrégation
        'by_period_weekdays_window'.

    Returns
    -------
    dict
        Dictionnaire contenant les suffixes pour chaque niveau d'agrégation.
    """
    calendrier = France()

    suffix_by_agg: dict[str, Callable[[date], str]] = {
        AggregationLevel.by_month: lambda x: x.strftime('%Y_%m'),
        AggregationLevel.by_year: lambda x: x.strftime('%Y'),
        AggregationLevel.by_period: lambda x: x.strftime('%Y_') + get_period_name(
            x, df_calendrier_scolaire, periode_ete),
        AggregationLevel.by_period_weekdays: lambda x: (
            x.strftime('%Y_sunday_or_holiday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
            if (x.weekday() == 6) or calendrier.is_holiday(x)
            else (
                x.strftime('%Y_week_') + get_period_name(x, df_calendrier_scolaire, periode_ete) if x.weekday() < 5 else
                x.strftime('%Y_saturday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
            )
        ),
        AggregationLevel.by_period_weekdays_window: lambda x: (
            window_name + x.strftime('sunday_or_holiday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
            if (x.weekday() == 6) or calendrier.is_holiday(x)
            else (
                window_name + x.strftime('week_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
                if x.weekday() < 5
                else (
                    window_name + x.strftime('saturday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
                )
            )
        ),
        AggregationLevel.by_year_weekdays: lambda x: (
            x.strftime('%Y_week') if x.weekday() < 5 else x.strftime('%Y_weekend')
        ),
        AggregationLevel.by_window: lambda _: window_name,
    }

    return suffix_by_agg
