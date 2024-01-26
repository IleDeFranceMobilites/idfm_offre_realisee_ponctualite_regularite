import os
import shutil
from datetime import datetime

import pytest

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.aggregation_config import AggregationLevel, suffix_by_agg
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.usecases.create_mesure_qs_regularite import (create_mesure_qs_regularite,
                                                                        create_mesure_qs_regularite_date_range)
from tests.test_data import TEST_DATA_PATH
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler

TEST_DATA_PATH_CONFIG = {
    'input_path': 'input',
    'output_path': 'output',
    'input_file_name': f'offre_realisee{FileExtensions.parquet}'
}

START_DATE = datetime(2023, 9, 27)
END_DATE = datetime(2023, 9, 28)


@pytest.fixture
def file_system_fixture():
    yield
    shutil.rmtree(os.path.join(TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'],
                               AggregationLevel.by_day, MesureType.regularite))


def test_create_mesure_qs_regularite(file_system_fixture):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
    )

    date = START_DATE

    # When
    create_mesure_qs_regularite(local_file_system_handler, date)

    # Assert
    suffix = suffix_by_agg[AggregationLevel.by_day](date)

    result_clean = os.listdir(
        os.path.join(
            TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'], AggregationLevel.by_day, MesureType.regularite
        )
    )
    assert f"mesure_{MesureType.regularite}_{suffix}" + FileExtensions.csv in result_clean


def test_create_mesure_qs_regularite_date_range(file_system_fixture):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
    )

    start_date = START_DATE
    end_date = END_DATE

    date_range = (start_date, end_date)

    # When
    create_mesure_qs_regularite_date_range(local_file_system_handler, date_range, 2)

    # Assert
    start_date_suffix = suffix_by_agg[AggregationLevel.by_day](start_date)
    end_date_suffix = suffix_by_agg[AggregationLevel.by_day](end_date)

    result_clean = os.listdir(
        os.path.join(
            TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'], AggregationLevel.by_day, MesureType.regularite
        )
    )
    assert f"mesure_{MesureType.regularite}_{start_date_suffix}" + FileExtensions.csv in result_clean
    assert f"mesure_{MesureType.regularite}_{end_date_suffix}" + FileExtensions.csv in result_clean
