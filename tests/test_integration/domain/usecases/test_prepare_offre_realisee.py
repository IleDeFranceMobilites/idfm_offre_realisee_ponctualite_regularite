import os
from datetime import datetime

import pandas as pd
import pytest

from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.input_brute_config import (DEFAULT_INPUT_BRUTE_FILE_NAME_PATTERN, DEFAULT_INPUT_BRUTE_PATH,
                                                      InputBruteColumns)
from offre_realisee.config.input_config import InputColumns
from offre_realisee.domain.usecases.prepare_offre_realisee import (prepare_offre_realisee,
                                                                   prepare_offre_realisee_date_range)
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler

TEST_DATA_PATH_CONFIG = {
    'input_path': 'input',
    'output_path': 'output',
    'input_file_name': f'offre_realisee{FileExtensions.parquet}',
    'calendrier_scolaire_file_name': f'calendrier_scolaire{FileExtensions.parquet}'
}

START_DATE = datetime(2023, 9, 27)
END_DATE = datetime(2023, 9, 28)


def offre_realisee_brute(jour: str) -> pd.DataFrame:
    """Données brutes d'une course à deux arrêts : un arrêt courant et un terminus d'arrivée."""
    return pd.DataFrame({
        InputBruteColumns.jour: [jour, jour, jour],
        InputBruteColumns.ligne: ['150', '150', '150'],
        InputBruteColumns.sens_id: [0, 0, 0],
        InputBruteColumns.arret: ['4CH', 'VIL', 'NON_EVALUABLE'],
        InputBruteColumns.course_id: [1, 1, 2],
        InputBruteColumns.is_terminus: [False, True, False],
        InputBruteColumns.heure_depart_theorique: [
            pd.Timestamp(f'{jour} 06:00:00'), pd.NaT, pd.Timestamp(f'{jour} 07:00:00')],
        InputBruteColumns.heure_arrivee_theorique: [
            pd.Timestamp(f'{jour} 05:59:00'), pd.Timestamp(f'{jour} 06:30:00'), pd.NaT],
        InputBruteColumns.heure_depart_reelle: [
            pd.Timestamp(f'{jour} 06:02:00'), pd.NaT, pd.Timestamp(f'{jour} 07:01:00')],
        InputBruteColumns.heure_arrivee_reelle: [
            pd.NaT, pd.Timestamp(f'{jour} 06:33:00'), pd.NaT],
        InputBruteColumns.passage_evaluable: [True, True, False],
    })


@pytest.fixture
def local_file_system_handler(tmp_path):
    input_brute_path = os.path.join(tmp_path, DEFAULT_INPUT_BRUTE_PATH)
    os.makedirs(input_brute_path)

    for date in [START_DATE, END_DATE]:
        offre_realisee_brute(jour=date.strftime('%Y-%m-%d')).to_parquet(
            os.path.join(input_brute_path, date.strftime(DEFAULT_INPUT_BRUTE_FILE_NAME_PATTERN)), index=False)

    return LocalFileSystemHandler(
        data_path=str(tmp_path),
        input_path=TEST_DATA_PATH_CONFIG['input_path'],
        output_path=TEST_DATA_PATH_CONFIG['output_path'],
        input_file_name=TEST_DATA_PATH_CONFIG['input_file_name'],
        calendrier_scolaire_file_name=TEST_DATA_PATH_CONFIG['calendrier_scolaire_file_name'],
    )


def test_prepare_offre_realisee(local_file_system_handler):
    # Given
    date = START_DATE
    jour = date.strftime('%Y-%m-%d')

    # When
    prepare_offre_realisee(file_system_handler=local_file_system_handler, date=date)

    # Assert - les données préparées sont relues par le calcul des mesures, partition et colonnes comprises
    result = local_file_system_handler.get_daily_offre_realisee(date=date)

    expected_result = pd.DataFrame({
        InputColumns.ligne: ['150', '150'],
        InputColumns.arret: ['4CH', 'VIL'],
        # SENS est construit par la préparation à partir de SENS_ID, d'où le dtype "string"
        InputColumns.sens: pd.array(['0', '0'], dtype='string'),
        InputColumns.heure_theorique: [
            pd.Timestamp(f'{jour} 06:00:00', tz='UTC'), pd.Timestamp(f'{jour} 06:30:00', tz='UTC')],
        InputColumns.heure_reelle: [
            pd.Timestamp(f'{jour} 06:02:00', tz='UTC'), pd.Timestamp(f'{jour} 06:33:00', tz='UTC')],
        InputColumns.is_terminus: [False, True],
        InputColumns.course_id: [1, 1],
    })

    pd.testing.assert_frame_equal(result, expected_result)


def test_prepare_offre_realisee_jour_sans_donnees_brutes(local_file_system_handler):
    # Given
    date = datetime(2023, 9, 29)

    # When
    prepare_offre_realisee(file_system_handler=local_file_system_handler, date=date)

    # Assert - un jour sans fichier brut ne fait pas échouer la préparation et n'écrit rien
    assert not os.path.exists(os.path.join(
        local_file_system_handler.data_path, TEST_DATA_PATH_CONFIG['input_path'],
        TEST_DATA_PATH_CONFIG['input_file_name']))


def test_prepare_offre_realisee_date_range(local_file_system_handler):
    # Given
    date_range = (START_DATE, END_DATE)

    # When
    prepare_offre_realisee_date_range(
        file_system_handler=local_file_system_handler, date_range=date_range, n_thread=2)

    # Assert
    dataset_path = os.path.join(local_file_system_handler.data_path, TEST_DATA_PATH_CONFIG['input_path'],
                                TEST_DATA_PATH_CONFIG['input_file_name'])

    assert sorted(os.listdir(dataset_path)) == [
        f"{InputColumns.jour}={START_DATE.strftime('%Y-%m-%d')}",
        f"{InputColumns.jour}={END_DATE.strftime('%Y-%m-%d')}",
    ]
    assert os.listdir(os.path.join(dataset_path, f"{InputColumns.jour}={START_DATE.strftime('%Y-%m-%d')}")) == [
        f"part-{START_DATE.strftime('%Y%m%d')}{FileExtensions.parquet}"]
