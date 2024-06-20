from datetime import datetime

import pandas as pd

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.domain.entities.aggregation.generate_date_aggregation_lists import generate_date_aggregation_lists
from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import (
    IDF_TIMEZONE, generate_suffix_by_aggregation)


def test_generate_date_aggregation_lists():
    # Given
    date_range = (datetime(2023, 1, 1), datetime(2023, 1, 3))
    aggregation_level = AggregationLevel.by_month
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result = {"2023_01": [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3)]}

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_keys_by_month():
    # Given
    date_range = (datetime(2023, 1, 1), datetime(2023, 3, 1))
    aggregation_level = AggregationLevel.by_month
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result_keys = ["2023_01", "2023_02", "2023_03"]

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert list(result.keys()) == expected_result_keys


def test_generate_date_aggregation_lists_test_keys_by_year():
    # Given
    date_range = (datetime(2023, 1, 1), datetime(2024, 9, 1))
    aggregation_level = AggregationLevel.by_year
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result_keys = ["2023", "2024"]

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert list(result.keys()) == expected_result_keys


def test_generate_date_aggregation_lists_test_keys_by_year_weekdays():
    # Given
    date_range = (datetime(2023, 1, 1), datetime(2024, 9, 1))
    aggregation_level = AggregationLevel.by_year_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result_keys = ["2023_weekend", "2023_week", "2024_weekend", "2024_week"]

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert sorted(list(result.keys())) == sorted(expected_result_keys)


def test_generate_date_aggregation_lists_test_values_by_year_weekdays():
    # Given
    date_range = (datetime(2023, 1, 1), datetime(2023, 1, 7))
    aggregation_level = AggregationLevel.by_year_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result = {
        "2023_weekend": [datetime(2023, 1, 1), datetime(2023, 1, 7)],
        "2023_week": [datetime(2023, 1, 2), datetime(2023, 1, 3), datetime(2023, 1, 4),
                      datetime(2023, 1, 5), datetime(2023, 1, 6)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period():
    # Given
    date_range = (datetime(2023, 8, 31), datetime(2023, 9, 4))
    aggregation_level = AggregationLevel.by_period
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 1))],
        'end_date': [IDF_TIMEZONE.localize(datetime(2023, 9, 4))]
    }))

    expected_result = {
        "2023_ete": [datetime(2023, 8, 31)],
        "2023_vacances_scolaires": [datetime(2023, 9, 1), datetime(2023, 9, 2), datetime(2023, 9, 3)],
        "2023_plein_trafic": [datetime(2023, 9, 4)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_weekdays():
    # Given
    date_range = (datetime(2023, 8, 20), datetime(2023, 9, 12))
    aggregation_level = AggregationLevel.by_period_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [
            IDF_TIMEZONE.localize(datetime(2023, 9, 1))
        ],
        'end_date': [
            IDF_TIMEZONE.localize(datetime(2023, 9, 4))
        ]
    }))

    expected_result = {
        '2023_sunday_or_holiday_ete': [datetime(2023, 8, 20, 0, 0), datetime(2023, 8, 27, 0, 0)],
        '2023_week_ete': [datetime(2023, 8, 21, 0, 0), datetime(2023, 8, 22, 0, 0), datetime(2023, 8, 23, 0, 0),
                          datetime(2023, 8, 24, 0, 0), datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 28, 0, 0),
                          datetime(2023, 8, 29, 0, 0), datetime(2023, 8, 30, 0, 0), datetime(2023, 8, 31, 0, 0)],
        '2023_saturday_ete': [datetime(2023, 8, 26, 0, 0)],
        '2023_week_vacances_scolaires': [datetime(2023, 9, 1, 0, 0)],
        '2023_saturday_vacances_scolaires': [datetime(2023, 9, 2, 0, 0)],
        '2023_sunday_or_holiday_vacances_scolaires': [datetime(2023, 9, 3, 0, 0)],
        '2023_week_plein_trafic': [datetime(2023, 9, 4, 0, 0), datetime(2023, 9, 5, 0, 0), datetime(2023, 9, 6, 0, 0),
                                   datetime(2023, 9, 7, 0, 0), datetime(2023, 9, 8, 0, 0), datetime(2023, 9, 11, 0, 0),
                                   datetime(2023, 9, 12, 0, 0)],
        '2023_saturday_plein_trafic': [datetime(2023, 9, 9, 0, 0)],
        '2023_sunday_or_holiday_plein_trafic': [datetime(2023, 9, 10, 0, 0)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_weekdays_window():
    # Given
    date_range = (datetime(2023, 8, 20), datetime(2023, 9, 12))
    aggregation_level = AggregationLevel.by_period_weekdays_window
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [
            IDF_TIMEZONE.localize(datetime(2023, 9, 1))
        ],
        'end_date': [
            IDF_TIMEZONE.localize(datetime(2023, 9, 4))
        ]
    }))

    expected_result = {
        'sunday_or_holiday_ete': [datetime(2023, 8, 20, 0, 0), datetime(2023, 8, 27, 0, 0)],
        'week_ete': [datetime(2023, 8, 21, 0, 0), datetime(2023, 8, 22, 0, 0), datetime(2023, 8, 23, 0, 0),
                     datetime(2023, 8, 24, 0, 0), datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 28, 0, 0),
                     datetime(2023, 8, 29, 0, 0), datetime(2023, 8, 30, 0, 0), datetime(2023, 8, 31, 0, 0)],
        'saturday_ete': [datetime(2023, 8, 26, 0, 0)],
        'week_vacances_scolaires': [datetime(2023, 9, 1, 0, 0)],
        'saturday_vacances_scolaires': [datetime(2023, 9, 2, 0, 0)],
        'sunday_or_holiday_vacances_scolaires': [datetime(2023, 9, 3, 0, 0)],
        'week_plein_trafic': [datetime(2023, 9, 4, 0, 0), datetime(2023, 9, 5, 0, 0), datetime(2023, 9, 6, 0, 0),
                              datetime(2023, 9, 7, 0, 0), datetime(2023, 9, 8, 0, 0), datetime(2023, 9, 11, 0, 0),
                              datetime(2023, 9, 12, 0, 0)],
        'saturday_plein_trafic': [datetime(2023, 9, 9, 0, 0)],
        'sunday_or_holiday_plein_trafic': [datetime(2023, 9, 10, 0, 0)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_ferie():
    # Given
    date_range = (datetime(2023, 5, 1), datetime(2023, 5, 18))
    aggregation_level = AggregationLevel.by_period_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [IDF_TIMEZONE.localize(datetime(2023, 4, 23))],
        'end_date': [IDF_TIMEZONE.localize(datetime(2023, 5, 9))]
    }))
    list_journees_exceptionnelles = []

    expected_result = {
        '2023_sunday_or_holiday_vacances_scolaires': [
            datetime(2023, 5, 1, 0, 0), datetime(2023, 5, 7, 0, 0), datetime(2023, 5, 8, 0, 0)
        ],
        '2023_week_vacances_scolaires': [
            datetime(2023, 5, 2, 0, 0), datetime(2023, 5, 3, 0, 0), datetime(2023, 5, 4, 0, 0),
            datetime(2023, 5, 5, 0, 0)
        ],
        '2023_saturday_vacances_scolaires': [datetime(2023, 5, 6, 0, 0)],
        '2023_week_plein_trafic': [
            datetime(2023, 5, 9, 0, 0), datetime(2023, 5, 10, 0, 0), datetime(2023, 5, 11, 0, 0),
            datetime(2023, 5, 12, 0, 0), datetime(2023, 5, 15, 0, 0), datetime(2023, 5, 16, 0, 0),
            datetime(2023, 5, 17, 0, 0)
        ],
        '2023_saturday_plein_trafic': [datetime(2023, 5, 13, 0, 0)],
        '2023_sunday_or_holiday_plein_trafic': [datetime(2023, 5, 14, 0, 0), datetime(2023, 5, 18, 0, 0)]}

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg,
                                             list_journees_exceptionnelles)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_except_journees_exceptionnelles():
    # Given
    date_range = (datetime(2023, 1, 1), datetime(2023, 1, 7))
    aggregation_level = AggregationLevel.by_year_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))
    list_journees_exceptionnelles = [datetime(2023, 1, 5)]

    expected_result = {
        "2023_weekend": [datetime(2023, 1, 1), datetime(2023, 1, 7)],
        "2023_week": [datetime(2023, 1, 2), datetime(2023, 1, 3), datetime(2023, 1, 4),
                      datetime(2023, 1, 6)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg,
                                             list_journees_exceptionnelles)

    # Then
    assert result.items() == expected_result.items()
