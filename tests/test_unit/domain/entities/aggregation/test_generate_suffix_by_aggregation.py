from datetime import datetime

import pandas as pd

from offre_realisee.config.aggregation_config import PeriodeName
from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import IDF_TIMEZONE, get_period_name


TEST_PERIODE_ETE = ('07_01', '08_31')


def test_get_period_name_plein_trafic():
    # Given
    date = datetime(2023, 9, 4)
    df_calendrier_scolaire = pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 1))],
        'end_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 3))]
    })

    expected_result = PeriodeName.plein_trafic

    # When
    result = get_period_name(date, df_calendrier_scolaire, periode_ete=TEST_PERIODE_ETE)

    # Then
    assert result == expected_result


def test_get_period_name_vacances():
    # Given
    date = datetime(2023, 9, 2)
    df_calendrier_scolaire = pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 1))],
        'end_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 3))]
    })

    expected_result = PeriodeName.vacances_scolaires

    # When
    result = get_period_name(date, df_calendrier_scolaire, periode_ete=TEST_PERIODE_ETE)

    # Then
    assert result == expected_result


def test_get_period_name_ete():
    # Given
    date = datetime(2023, 7, 4)
    df_calendrier_scolaire = pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 1))],
        'end_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 3))]
    })

    expected_result = PeriodeName.ete

    # When
    result = get_period_name(date, df_calendrier_scolaire, periode_ete=TEST_PERIODE_ETE)

    # Then
    assert result == expected_result
