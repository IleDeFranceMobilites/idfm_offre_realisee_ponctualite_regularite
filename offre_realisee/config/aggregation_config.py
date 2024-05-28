from offre_realisee.config.file_extensions import FileExtensions


class AggregationLevel:
    by_day = "by_day"
    by_month = "by_month"
    by_year = "by_year"
    by_period = "by_period"
    by_period_weekdays = "by_period_weekdays"
    by_year_weekdays = "by_year_weekdays"


class PeriodeName:
    plein_trafic = 'plein_trafic'
    vacances_scolaires = 'vacances_scolaires'
    ete = 'ete'


class CalendrierScolaireColumns:
    description = 'description'
    start_date = 'start_date'
    end_date = 'end_date'


calendrier_scolaire_filename = 'calendrier_scolaire' + FileExtensions.parquet
