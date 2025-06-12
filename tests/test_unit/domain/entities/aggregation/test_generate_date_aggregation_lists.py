from datetime import datetime, date

import pandas as pd

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.domain.entities.aggregation.generate_date_aggregation_lists import generate_date_aggregation_lists
from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import (
    IDF_TIMEZONE, generate_suffix_by_aggregation)

TEST_PERIODE_ETE = (date(2023, 7, 1), date(2023, 8, 31))


def test_generate_date_aggregation_lists():
    # Given
    date_range = (date(2023, 1, 1), date(2023, 1, 3))
    aggregation_level = AggregationLevel.by_month
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result = {"2023_01": [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]}

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_keys_by_month():
    # Given
    date_range = (date(2023, 1, 1), date(2023, 3, 1))
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
    date_range = (date(2023, 1, 1), date(2024, 9, 1))
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
    date_range = (date(2023, 1, 1), date(2024, 9, 1))
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
    date_range = (date(2023, 1, 1), date(2023, 1, 7))
    aggregation_level = AggregationLevel.by_year_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))

    expected_result = {
        "2023_weekend": [date(2023, 1, 1), date(2023, 1, 7)],
        "2023_week": [date(2023, 1, 2), date(2023, 1, 3), date(2023, 1, 4),
                      date(2023, 1, 5), date(2023, 1, 6)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period():
    # Given
    date_range = (date(2023, 8, 31), date(2023, 9, 4))
    aggregation_level = AggregationLevel.by_period
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 4, tzinfo=IDF_TIMEZONE)]
    }), periode_ete=TEST_PERIODE_ETE)

    expected_result = {
        "2023_ete": [date(2023, 8, 31)],
        "2023_vacances_scolaires": [date(2023, 9, 1), date(2023, 9, 2), date(2023, 9, 3)],
        "2023_plein_trafic": [date(2023, 9, 4)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_weekdays():
    # Given
    date_range = (date(2023, 8, 20), date(2023, 9, 12))
    aggregation_level = AggregationLevel.by_period_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 4, tzinfo=IDF_TIMEZONE)]
    }), periode_ete=TEST_PERIODE_ETE)

    expected_result = {
        '2023_sunday_or_holiday_ete': [date(2023, 8, 20), date(2023, 8, 27)],
        '2023_week_ete': [date(2023, 8, 21), date(2023, 8, 22), date(2023, 8, 23),
                          date(2023, 8, 24), date(2023, 8, 25), date(2023, 8, 28),
                          date(2023, 8, 29), date(2023, 8, 30), date(2023, 8, 31)],
        '2023_saturday_ete': [date(2023, 8, 26)],
        '2023_week_vacances_scolaires': [date(2023, 9, 1)],
        '2023_saturday_vacances_scolaires': [date(2023, 9, 2)],
        '2023_sunday_or_holiday_vacances_scolaires': [date(2023, 9, 3)],
        '2023_week_plein_trafic': [date(2023, 9, 4), date(2023, 9, 5), date(2023, 9, 6),
                                   date(2023, 9, 7), date(2023, 9, 8), date(2023, 9, 11),
                                   date(2023, 9, 12)],
        '2023_saturday_plein_trafic': [date(2023, 9, 9)],
        '2023_sunday_or_holiday_plein_trafic': [date(2023, 9, 10)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_weekdays_window():
    # Given
    date_range = (date(2023, 8, 20), date(2023, 9, 12))
    aggregation_level = AggregationLevel.by_period_weekdays_window
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 4, tzinfo=IDF_TIMEZONE)]
    }), periode_ete=TEST_PERIODE_ETE)

    expected_result = {
        'sunday_or_holiday_ete': [date(2023, 8, 20), date(2023, 8, 27)],
        'week_ete': [date(2023, 8, 21), date(2023, 8, 22), date(2023, 8, 23),
                     date(2023, 8, 24), date(2023, 8, 25), date(2023, 8, 28),
                     date(2023, 8, 29), date(2023, 8, 30), date(2023, 8, 31)],
        'saturday_ete': [date(2023, 8, 26)],
        'week_vacances_scolaires': [date(2023, 9, 1)],
        'saturday_vacances_scolaires': [date(2023, 9, 2)],
        'sunday_or_holiday_vacances_scolaires': [date(2023, 9, 3)],
        'week_plein_trafic': [date(2023, 9, 4), date(2023, 9, 5), date(2023, 9, 6),
                              date(2023, 9, 7), date(2023, 9, 8), date(2023, 9, 11),
                              date(2023, 9, 12)],
        'saturday_plein_trafic': [date(2023, 9, 9)],
        'sunday_or_holiday_plein_trafic': [date(2023, 9, 10)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_weekdays_window_w_name():
    # Given
    date_range = (date(2023, 8, 20), date(2023, 9, 12))
    aggregation_level = AggregationLevel.by_period_weekdays_window
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 9, 1, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 9, 4, tzinfo=IDF_TIMEZONE)]
    }), periode_ete=TEST_PERIODE_ETE, window_name="test_window_")

    expected_result = {
        'test_window_sunday_or_holiday_ete': [date(2023, 8, 20), date(2023, 8, 27)],
        'test_window_week_ete': [
            date(2023, 8, 21), date(2023, 8, 22), date(2023, 8, 23), date(2023, 8, 24), date(2023, 8, 25),
            date(2023, 8, 28), date(2023, 8, 29), date(2023, 8, 30), date(2023, 8, 31)],
        'test_window_saturday_ete': [date(2023, 8, 26)],
        'test_window_week_vacances_scolaires': [date(2023, 9, 1)],
        'test_window_saturday_vacances_scolaires': [date(2023, 9, 2)],
        'test_window_sunday_or_holiday_vacances_scolaires': [date(2023, 9, 3)],
        'test_window_week_plein_trafic': [
            date(2023, 9, 4), date(2023, 9, 5), date(2023, 9, 6),
            date(2023, 9, 7), date(2023, 9, 8), date(2023, 9, 11),
            date(2023, 9, 12)],
        'test_window_saturday_plein_trafic': [date(2023, 9, 9)],
        'test_window_sunday_or_holiday_plein_trafic': [date(2023, 9, 10)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_by_period_ferie():
    # Given
    date_range = (date(2023, 5, 1), date(2023, 5, 18))
    aggregation_level = AggregationLevel.by_period_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': ['Vacances'],
        'start_date': [datetime(2023, 4, 23, tzinfo=IDF_TIMEZONE)],
        'end_date': [datetime(2023, 5, 9, tzinfo=IDF_TIMEZONE)]
    }), periode_ete=TEST_PERIODE_ETE)
    list_journees_exceptionnelles = []

    expected_result = {
        '2023_sunday_or_holiday_vacances_scolaires': [
            date(2023, 5, 1), date(2023, 5, 7), date(2023, 5, 8)
        ],
        '2023_week_vacances_scolaires': [
            date(2023, 5, 2), date(2023, 5, 3), date(2023, 5, 4), date(2023, 5, 5)
        ],
        '2023_saturday_vacances_scolaires': [date(2023, 5, 6)],
        '2023_week_plein_trafic': [
            date(2023, 5, 9), date(2023, 5, 10), date(2023, 5, 11), date(2023, 5, 12),
            date(2023, 5, 15), date(2023, 5, 16), date(2023, 5, 17)
        ],
        '2023_saturday_plein_trafic': [date(2023, 5, 13)],
        '2023_sunday_or_holiday_plein_trafic': [date(2023, 5, 14), date(2023, 5, 18)]}

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg,
                                             list_journees_exceptionnelles)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_test_values_except_journees_exceptionnelles():
    # Given
    date_range = (date(2023, 1, 1), date(2023, 1, 7))
    aggregation_level = AggregationLevel.by_year_weekdays
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }))
    list_journees_exceptionnelles = [date(2023, 1, 5)]

    expected_result = {
        "2023_weekend": [date(2023, 1, 1), date(2023, 1, 7)],
        "2023_week": [date(2023, 1, 2), date(2023, 1, 3), date(2023, 1, 4),
                      date(2023, 1, 6)]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg,
                                             list_journees_exceptionnelles)

    # Then
    assert result.items() == expected_result.items()


def test_generate_date_aggregation_lists_by_window():
    # Given
    date_range = (date(2023, 1, 1), date(2023, 1, 7))
    aggregation_level = AggregationLevel.by_window
    suffix_by_agg = generate_suffix_by_aggregation(pd.DataFrame({
        'description': [],
        'start_date': [],
        'end_date': []
    }), window_name='test_window')
    list_journees_exceptionnelles = [date(2023, 1, 5)]

    expected_result = {
        "test_window": [
            date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3),
            date(2023, 1, 4), date(2023, 1, 6), date(2023, 1, 7)
        ]
    }

    # When
    result = generate_date_aggregation_lists(date_range, aggregation_level, suffix_by_agg,
                                             list_journees_exceptionnelles)

    # Then
    assert result.items() == expected_result.items()
