import os
from datetime import datetime

import pytest

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.aggregation_config import AggregationLevel, suffix_by_agg
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.usecases.create_mesure_qs_regularite import create_mesure_qs_regularite
from tests.test_data import TEST_DATA_PATH
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler

TEST_DATA_PATH_CONFIG = {
    'input_path': 'input',
    'output_path': 'output',
    'input_file_name': f'offre_realisee{FileExtensions.parquet}'
}

DATE = datetime(2023, 9, 27)


@pytest.fixture
def file_system_fixture():
    yield
    suffix = suffix_by_agg[AggregationLevel.by_day](DATE)
    os.remove(os.path.join(TEST_DATA_PATH, TEST_DATA_PATH_CONFIG['output_path'],
                           AggregationLevel.by_day, MesureType.regularite,
                           f"mesure_{MesureType.regularite}_{suffix}" + FileExtensions.csv))


def test_create_mesure_qs(file_system_fixture):
    # Given
    local_file_system_handler = LocalFileSystemHandler(
        data_path=TEST_DATA_PATH,
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
    )

    date = DATE

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
