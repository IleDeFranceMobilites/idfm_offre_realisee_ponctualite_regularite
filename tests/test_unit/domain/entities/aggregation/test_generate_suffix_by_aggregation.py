from datetime import datetime, date

import pandas as pd

from offre_realisee.config.aggregation_config import PeriodeName
from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import IDF_TIMEZONE, get_period_name


TEST_PERIODE_ETE = (date(2023, 7, 1), date(2023, 8, 31))


def test_get_period_name_plein_trafic():
    # Given
    test_date = date(2023, 9, 4)
    df_calendrier_scolaire = pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 3, tzinfo=IDF_TIMEZONE)]
    })

    expected_result = PeriodeName.plein_trafic

    # When
    result = get_period_name(test_date, df_calendrier_scolaire, periode_ete=TEST_PERIODE_ETE)

    # Then
    assert result == expected_result


def test_get_period_name_vacances():
    # Given
    test_date = date(2023, 9, 2)
    df_calendrier_scolaire = pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 3, tzinfo=IDF_TIMEZONE)]
    })

    expected_result = PeriodeName.vacances_scolaires

    # When
    result = get_period_name(test_date, df_calendrier_scolaire, periode_ete=TEST_PERIODE_ETE)

    # Then
    assert result == expected_result


def test_get_period_name_ete():
    # Given
    test_date = date(2023, 7, 4)
    df_calendrier_scolaire = pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 3, tzinfo=IDF_TIMEZONE)]
    })

    expected_result = PeriodeName.ete

    # When
    result = get_period_name(test_date, df_calendrier_scolaire, periode_ete=TEST_PERIODE_ETE)

    # Then
    assert result == expected_result
