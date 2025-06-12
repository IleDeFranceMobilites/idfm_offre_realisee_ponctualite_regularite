class AggregationLevel:
    by_month = "by_month"
    by_year = "by_year"
    by_period = "by_period"
    by_period_weekdays = "by_period_weekdays"
    by_period_weekdays_window = "by_period_weekdays_window"
    by_year_weekdays = "by_year_weekdays"
    by_window = "by_window"


class PeriodeName:
    plein_trafic = 'plein_trafic'
    vacances_scolaires = 'vacances_scolaires'
    ete = 'ete'


class CalendrierScolaireColumns:
    description = 'description'
    start_date = 'start_date'
    end_date = 'end_date'
