import os
import shutil
from datetime import datetime

import pandas as pd
import pytest

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.usecases.create_mesure_qs_regularite import (create_mesure_qs_regularite,
                                                                        create_mesure_qs_regularite_date_range)
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
    f"mesure_{MesureType.regularite}_{START_DATE.strftime('%Y_%m_%d')}{FileExtensions.csv}"
)

RESULT_PATH = os.path.join(
    TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'], MesureType.regularite
)


@pytest.fixture
def file_system_fixture():
    yield
    shutil.rmtree(RESULT_PATH)


def test_create_mesure_qs_regularite(file_system_fixture):
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
    create_mesure_qs_regularite(file_system_handler=local_file_system_handler, date=date)

    # Assert
    expected_result = pd.read_csv(EXPECTED_FILE)
    result = pd.read_csv(
        os.path.join(RESULT_PATH, f"mesure_{MesureType.regularite}_{date.strftime('%Y_%m_%d')}" + FileExtensions.csv))

    pd.testing.assert_frame_equal(result, expected_result)


def test_create_mesure_qs_regularite_donnees_dupliquees(file_system_fixture):
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
    create_mesure_qs_regularite(local_file_system_handler, date)

    # Assert
    expected_result = pd.read_csv(EXPECTED_FILE)
    result = pd.read_csv(
        os.path.join(RESULT_PATH, f"mesure_{MesureType.regularite}_{date.strftime('%Y_%m_%d')}" + FileExtensions.csv))

    pd.testing.assert_frame_equal(result, expected_result)


def test_create_mesure_qs_regularite_date_range(file_system_fixture):
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
    create_mesure_qs_regularite_date_range(
        file_system_handler=local_file_system_handler, date_range=date_range, n_thread=2)

    # Assert
    result_clean = os.listdir(
        os.path.join(
            TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'], MesureType.regularite
        )
    )
    assert f"mesure_{MesureType.regularite}_{start_date.strftime('%Y_%m_%d')}" + FileExtensions.csv in result_clean
    assert f"mesure_{MesureType.regularite}_{end_date.strftime('%Y_%m_%d')}" + FileExtensions.csv in result_clean
