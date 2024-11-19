from datetime import datetime
from pytz import timezone

import pandas as pd
from workalendar.europe import France

from offre_realisee.config.aggregation_config import (
    DEFAULT_PERIODE_ETE, AggregationLevel, PeriodeName, CalendrierScolaireColumns
)

IDF_TIMEZONE = timezone('Europe/Paris')


def get_period_name(date: datetime, df_calendrier_scolaire: pd.DataFrame, periode_ete: tuple[str]):

    if date.strftime("%m_%d") >= periode_ete[0] and date.strftime("%m_%d") <= periode_ete[1]:
        return PeriodeName.ete

    df_filtered = df_calendrier_scolaire[df_calendrier_scolaire[
        CalendrierScolaireColumns.description].str.startswith('Vacances')]
    row = df_filtered[
        (pd.to_datetime(df_filtered[CalendrierScolaireColumns.start_date]) <= IDF_TIMEZONE.localize(date)) &
        (pd.to_datetime(df_filtered[CalendrierScolaireColumns.end_date]) > IDF_TIMEZONE.localize(date))
    ]
    if row.empty:
        return PeriodeName.plein_trafic
    else:
        return PeriodeName.vacances_scolaires


def generate_suffix_by_aggregation(
    df_calendrier_scolaire: pd.DataFrame, periode_ete: tuple[str] = DEFAULT_PERIODE_ETE, window_name: str = ""
) -> dict:
    calendrier = France()

    suffix_by_agg = {
        AggregationLevel.by_day: lambda x: x.strftime('%Y_%m_%d'),
        AggregationLevel.by_month: lambda x: x.strftime('%Y_%m'),
        AggregationLevel.by_year: lambda x: x.strftime('%Y'),
        AggregationLevel.by_period: lambda x: x.strftime('%Y_') + get_period_name(
            x, df_calendrier_scolaire, periode_ete),
        AggregationLevel.by_period_weekdays: lambda x: (
            x.strftime('%Y_sunday_or_holiday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
            if (x.weekday() == 6) or calendrier.is_holiday(x.date())
            else (
                x.strftime('%Y_week_') + get_period_name(x, df_calendrier_scolaire, periode_ete) if x.weekday() < 5 else
                x.strftime('%Y_saturday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
            )
        ),
        AggregationLevel.by_period_weekdays_window: lambda x: (
            window_name + x.strftime('sunday_or_holiday_') + get_period_name(x, df_calendrier_scolaire, periode_ete)
            if (x.weekday() == 6) or calendrier.is_holiday(x.date())
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
