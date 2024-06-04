from datetime import datetime

import pandas as pd
from workalendar.europe import France

from offre_realisee.config.aggregation_config import AggregationLevel, PeriodeName, CalendrierScolaireColumns


def get_period_name(date: datetime, df_calendrier_scolaire: pd.DataFrame):
    df_filtered = df_calendrier_scolaire[df_calendrier_scolaire[
        CalendrierScolaireColumns.description].str.startswith('Vacances')]
    row = df_filtered[(df_filtered[CalendrierScolaireColumns.start_date] <= date) & (
            df_filtered[CalendrierScolaireColumns.end_date] >= date)]
    if row.empty:
        return PeriodeName.plein_trafic
    elif row[CalendrierScolaireColumns.description].values[0] == 'Vacances d\'Été':
        return PeriodeName.ete
    else:
        return PeriodeName.vacances_scolaires


def generate_suffix_by_aggregation(df_calendrier_scolaire: pd.DataFrame) -> dict:
    calendrier = France()

    suffix_by_agg = {
        AggregationLevel.by_day: lambda x: x.strftime('%Y_%m_%d'),
        AggregationLevel.by_month: lambda x: x.strftime('%Y_%m'),
        AggregationLevel.by_year: lambda x: x.strftime('%Y'),
        AggregationLevel.by_period: lambda x: x.strftime('%Y_') + get_period_name(x, df_calendrier_scolaire),
        AggregationLevel.by_period_weekdays: lambda x: (
            x.strftime('%Y_sunday_or_holiday_') + get_period_name(x, df_calendrier_scolaire)
            if (x.weekday() == 6) or calendrier.is_holiday(x.date())
            else (
                x.strftime('%Y_week_') + get_period_name(x, df_calendrier_scolaire) if x.weekday() < 5 else
                x.strftime('%Y_saturday_') + get_period_name(x, df_calendrier_scolaire)
            )
        ),
        AggregationLevel.by_year_weekdays: lambda x: (
            x.strftime('%Y_week') if x.weekday() < 5 else x.strftime('%Y_weekend')
        )
    }

    return suffix_by_agg
