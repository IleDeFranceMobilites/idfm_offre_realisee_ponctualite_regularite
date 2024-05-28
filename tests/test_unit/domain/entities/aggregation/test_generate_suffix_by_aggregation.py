from datetime import datetime

import pandas as pd

from offre_realisee.config.aggregation_config import PeriodeName
from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import get_period_name


def test_get_period_name_plein_trafic():
    # Given
    date = datetime(2023, 9, 4)
    df_calendrier_scolaire = pd.DataFrame({
        'descritpion': ['Vacances d\'Été', 'Vacances'],
        'start_date': [datetime(2023, 7, 1), datetime(2023, 9, 1)],
        'end_date': [datetime(2023, 8, 31), datetime(2023, 9, 3)]
    })

    expected_result = PeriodeName.plein_trafic

    # When
    result = get_period_name(date, df_calendrier_scolaire)

    # Then
    assert result == expected_result


def test_get_period_name_vacances():
    # Given
    date = datetime(2023, 9, 2)
    df_calendrier_scolaire = pd.DataFrame({
        'descritpion': ['Vacances d\'Été', 'Vacances'],
        'start_date': [datetime(2023, 7, 1), datetime(2023, 9, 1)],
        'end_date': [datetime(2023, 8, 31), datetime(2023, 9, 3)]
    })

    expected_result = PeriodeName.vacances_scolaires

    # When
    result = get_period_name(date, df_calendrier_scolaire)

    # Then
    assert result == expected_result


def test_get_period_name_ete():
    # Given
    date = datetime(2023, 7, 4)
    df_calendrier_scolaire = pd.DataFrame({
        'descritpion': ['Vacances d\'Été', 'Vacances'],
        'start_date': [datetime(2023, 7, 1), datetime(2023, 9, 1)],
        'end_date': [datetime(2023, 8, 31), datetime(2023, 9, 3)]
    })

    expected_result = PeriodeName.ete

    # When
    result = get_period_name(date, df_calendrier_scolaire)

    # Then
    assert result == expected_result
