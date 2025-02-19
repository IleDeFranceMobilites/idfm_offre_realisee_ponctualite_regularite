import os
import shutil
from datetime import datetime
from typing import Optional

import pandas as pd
import pytest

from offre_realisee import AggregationLevel, MesureType, DEFAULT_PERIODE_ETE, LocalFileSystemHandler, \
    aggregate_mesure_qs, FileExtensions
from tests.test_data import TEST_DATA_PATH


TEST_DATA_PATH_CONFIG = {
    'input_path': 'input',
    'output_path': 'aggregate_output',
    'input_file_name': f'offre_realisee{FileExtensions.parquet}',
    'duplicated_input_file_name': f'offre_realisee_dupliquee{FileExtensions.parquet}',
    'calendrier_scolaire_file_name': f'calendrier_scolaire{FileExtensions.parquet}'
}

RESULT_PATH = os.path.join(TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'])


@pytest.fixture
def file_system_fixture_by_year():
    yield
    shutil.rmtree(os.path.join(RESULT_PATH, AggregationLevel.by_year))


def test_def_aggregate_mesure_qs_ponctualite_by_year(file_system_fixture_by_year):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name']
    )
    date_range: tuple[datetime, datetime] = (datetime(2023, 9, 30), datetime(2023, 10, 1))
    dsp: str = ''
    aggregation_level: AggregationLevel = AggregationLevel.by_year
    mesure_type: MesureType = MesureType.ponctualite
    periode_ete: tuple[str] = DEFAULT_PERIODE_ETE
    list_journees_exceptionnelles: Optional[list[datetime]] = None
    window_name: str = ""

    # When
    aggregate_mesure_qs(local_file_system_handler, date_range, dsp, aggregation_level, mesure_type, periode_ete,
                        list_journees_exceptionnelles, window_name)

    # Assert
    result = pd.read_csv(os.path.join(RESULT_PATH, aggregation_level, mesure_type,
                                      f"mesure_{mesure_type}_2023" + FileExtensions.csv))

    expected_result = pd.read_csv(os.path.join(TEST_DATA_PATH, 'expected_data',
                                               f"mesure_{mesure_type}_2023" + FileExtensions.csv))

    pd.testing.assert_frame_equal(result, expected_result)


def test_def_aggregate_mesure_qs_ponctualite_journees_exceptionnelles(file_system_fixture_by_year):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name']
    )
    date_range: tuple[datetime, datetime] = (datetime(2023, 9, 30), datetime(2023, 10, 1))
    dsp: str = ''
    aggregation_level: AggregationLevel = AggregationLevel.by_year
    mesure_type: MesureType = MesureType.ponctualite
    periode_ete: tuple[str] = DEFAULT_PERIODE_ETE
    list_journees_exceptionnelles: Optional[list[datetime]] = [datetime(2023, 9, 30)]
    window_name: str = ""

    # When
    aggregate_mesure_qs(local_file_system_handler, date_range, dsp, aggregation_level, mesure_type, periode_ete,
                        list_journees_exceptionnelles, window_name)

    # Assert
    result = pd.read_csv(os.path.join(RESULT_PATH, aggregation_level, mesure_type,
                                      f"mesure_{mesure_type}_2023" + FileExtensions.csv))

    expected_result = pd.read_csv(os.path.join(RESULT_PATH, AggregationLevel.by_day, mesure_type,
                                      f"mesure_{mesure_type}_2023_10_01" + FileExtensions.csv))

    pd.testing.assert_frame_equal(result, expected_result)


@pytest.fixture
def file_system_fixture_by_month():
    yield
    shutil.rmtree(os.path.join(RESULT_PATH, AggregationLevel.by_month))


def test_def_aggregate_mesure_qs_ponctualite_by_month(file_system_fixture_by_month):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name']
    )
    date_range: tuple[datetime, datetime] = (datetime(2023, 9, 30), datetime(2023, 10, 1))
    dsp: str = ''
    aggregation_level: AggregationLevel = AggregationLevel.by_month
    mesure_type: MesureType = MesureType.ponctualite
    periode_ete: tuple[str] = DEFAULT_PERIODE_ETE
    list_journees_exceptionnelles: Optional[list[datetime]] = None
    window_name: str = ""

    # When
    aggregate_mesure_qs(local_file_system_handler, date_range, dsp, aggregation_level, mesure_type, periode_ete,
                        list_journees_exceptionnelles, window_name)

    # Assert
    result_clean = os.listdir(os.path.join(RESULT_PATH, aggregation_level, mesure_type))

    assert f"mesure_{mesure_type}_2023_09" + FileExtensions.csv in result_clean
    assert f"mesure_{mesure_type}_2023_10" + FileExtensions.csv in result_clean


@pytest.fixture
def file_system_fixture_by_periode():
    yield
    shutil.rmtree(os.path.join(RESULT_PATH, AggregationLevel.by_period))


def test_def_aggregate_mesure_qs_regularite_by_periode(file_system_fixture_by_periode):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name']
    )
    date_range: tuple[datetime, datetime] = (datetime(2023, 8, 31), datetime(2023, 9, 1))
    dsp: str = ''
    aggregation_level: AggregationLevel = AggregationLevel.by_period
    mesure_type: MesureType = MesureType.regularite
    periode_ete: tuple[str] = DEFAULT_PERIODE_ETE
    list_journees_exceptionnelles: Optional[list[datetime]] = None
    window_name: str = ""

    # When
    aggregate_mesure_qs(local_file_system_handler, date_range, dsp, aggregation_level, mesure_type, periode_ete,
                        list_journees_exceptionnelles, window_name)

    # Assert
    result_clean = os.listdir(os.path.join(RESULT_PATH, aggregation_level, mesure_type))

    assert f"mesure_{mesure_type}_2023_ete" + FileExtensions.csv in result_clean
    assert f"mesure_{mesure_type}_2023_vacances_scolaires" + FileExtensions.csv in result_clean
