import os
import shutil
from datetime import datetime

import pandas as pd
import pytest

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.entities.aggregation.generate_suffix_by_aggregation import generate_suffix_by_aggregation
from offre_realisee.domain.usecases.create_mesure_qs_ponctualite import (create_mesure_qs_ponctualite,
                                                                         create_mesure_qs_ponctualite_date_range)
from tests.test_data import TEST_DATA_PATH
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler

TEST_DATA_PATH_CONFIG = {
    'input_path': 'input',
    'output_path': 'output',
    'input_file_name': f'offre_realisee{FileExtensions.parquet}',
    'duplicated_input_file_name': f'offre_realisee_dupliquee{FileExtensions.parquet}',
    'calendrier_scolaire_file_name': f'calendrier_scolaire{FileExtensions.parquet}'
}

START_DATE = datetime(2023, 9, 27)
END_DATE = datetime(2023, 9, 28)

EXPECTED_FILE = os.path.join(
    TEST_DATA_PATH, 'expected_data',
    f"mesure_{MesureType.ponctualite}_{START_DATE.strftime('%Y_%m_%d')}{FileExtensions.csv}"
)

RESULT_PATH = os.path.join(
    TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'],
    AggregationLevel.by_day, MesureType.ponctualite
)


@pytest.fixture
def file_system_fixture():
    yield
    shutil.rmtree(os.path.join(TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path']))


def test_create_mesure_qs(file_system_fixture):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name'],
    )

    date = START_DATE

    # When
    create_mesure_qs_ponctualite(local_file_system_handler, date)

    # Assert
    df_calendrier_scolaire = local_file_system_handler.get_calendrier_scolaire()
    suffix = generate_suffix_by_aggregation(df_calendrier_scolaire)[AggregationLevel.by_day](date)

    expected_result = pd.read_csv(EXPECTED_FILE)
    result = pd.read_csv(os.path.join(RESULT_PATH, f"mesure_{MesureType.ponctualite}_{suffix}" + FileExtensions.csv))

    pd.testing.assert_frame_equal(result, expected_result)


def test_create_mesure_qs_donnees_dupliquees(file_system_fixture):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['duplicated_input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name'],
    )

    date = START_DATE

    # When
    create_mesure_qs_ponctualite(local_file_system_handler, date)

    # Assert
    df_calendrier_scolaire = local_file_system_handler.get_calendrier_scolaire()
    suffix = generate_suffix_by_aggregation(df_calendrier_scolaire)[AggregationLevel.by_day](date)

    expected_result = pd.read_csv(EXPECTED_FILE)
    result = pd.read_csv(os.path.join(RESULT_PATH, f"mesure_{MesureType.ponctualite}_{suffix}" + FileExtensions.csv))

    pd.testing.assert_frame_equal(result, expected_result)


def test_create_mesure_qs_ponctualite_date_range(file_system_fixture):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name'],
    )

    start_date = START_DATE
    end_date = END_DATE

    date_range = (start_date, end_date)

    # When
    create_mesure_qs_ponctualite_date_range(local_file_system_handler, date_range, 2)

    # Assert
    df_calendrier_scolaire = local_file_system_handler.get_calendrier_scolaire()
    suffix_by_agg = generate_suffix_by_aggregation(df_calendrier_scolaire)
    start_date_suffix = suffix_by_agg[AggregationLevel.by_day](start_date)
    end_date_suffix = suffix_by_agg[AggregationLevel.by_day](end_date)

    result_clean = os.listdir(RESULT_PATH)

    assert f"mesure_{MesureType.ponctualite}_{start_date_suffix}" + FileExtensions.csv in result_clean
    assert f"mesure_{MesureType.ponctualite}_{end_date_suffix}" + FileExtensions.csv in result_clean
