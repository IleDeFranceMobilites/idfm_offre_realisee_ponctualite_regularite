class CalendrierScolaireColumns:
    zones = "zones"
    start_date = "start_date"
    end_date = "end_date"
    population = "population"
    description = "description"


IDF_CALENDRIER_SCOLAIRE_ZONE = 'Zone C'
CALENDRIER_SCOLAIRE_POPULATION = ["-", "Élèves"]

PARQUET_COMPRESSION = "brotli"
PARQUET_ENGINE = 'pyarrow'
