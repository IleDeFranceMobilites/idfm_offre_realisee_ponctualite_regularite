from datetime import datetime

from workalendar.europe import France


class AggregationLevel:
    by_day = "by_day"
    by_month = "by_month"
    by_year = "by_year"
    by_period = "by_period"
    by_period_weekdays = "by_period_weekdays"
    by_year_weekdays = "by_year_weekdays"


def get_period_name(date):
    return [p[2] for p in periode_2023 if p[0] <= date <= p[1]][0]


calendrier = France()

suffix_by_agg = {
    AggregationLevel.by_day: lambda x: x.strftime('%Y_%m_%d'),
    AggregationLevel.by_month: lambda x: x.strftime('%Y_%m'),
    AggregationLevel.by_year: lambda x: x.strftime('%Y'),
    AggregationLevel.by_period: lambda x: x.strftime('%Y_') + get_period_name(x),
    AggregationLevel.by_period_weekdays: lambda x: (
        x.strftime('%Y_sunday_or_holiday_') + get_period_name(x)
        if (x.weekday() == 6) or calendrier.is_holiday(x.date())
        else (
            x.strftime('%Y_week_') + get_period_name(x) if x.weekday() < 5 else
            x.strftime('%Y_saturday_') + get_period_name(x)
        )
    ),
    AggregationLevel.by_year_weekdays: lambda x: (
        x.strftime('%Y_week') if x.weekday() < 5 else x.strftime('%Y_weekend')
    )
}


class PeriodeName:
    plein_trafic = 'plein_trafic'
    vacances_scolaires = 'vacances_scolaires'
    ete = 'ete'


periode_2023 = [
    (datetime(2023, 1, 1), datetime(2023, 1, 2), PeriodeName.vacances_scolaires),
    (datetime(2023, 1, 3), datetime(2023, 2, 18), PeriodeName.plein_trafic),
    (datetime(2023, 2, 19), datetime(2023, 3, 5), PeriodeName.vacances_scolaires),
    (datetime(2023, 3, 6), datetime(2023, 4, 22), PeriodeName.plein_trafic),
    (datetime(2023, 4, 23), datetime(2023, 5, 8), PeriodeName.vacances_scolaires),
    (datetime(2023, 5, 9), datetime(2023, 6, 30), PeriodeName.plein_trafic),
    (datetime(2023, 7, 1), datetime(2023, 8, 31), PeriodeName.ete),
    (datetime(2023, 9, 1), datetime(2023, 9, 3), PeriodeName.vacances_scolaires),
    (datetime(2023, 9, 4), datetime(2023, 10, 21), PeriodeName.plein_trafic),
    (datetime(2023, 10, 22), datetime(2023, 11, 5), PeriodeName.vacances_scolaires),
    (datetime(2023, 11, 6), datetime(2023, 12, 23), PeriodeName.plein_trafic),
    (datetime(2023, 12, 24), datetime(2023, 12, 31), PeriodeName.vacances_scolaires),
]
