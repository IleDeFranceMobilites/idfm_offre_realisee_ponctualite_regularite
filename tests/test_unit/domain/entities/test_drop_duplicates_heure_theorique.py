from datetime import datetime

import pandas as pd

from offre_realisee.config.input_config import InputColumns
from offre_realisee.domain.entities.drop_duplicates_heure_theorique import drop_duplicates_heure_theorique


def test_drop_duplicates_heure_theorique():
    # Given
    df = pd.DataFrame({
        InputColumns.ligne: ['A', 'A', 'A', 'A', 'A'],
        InputColumns.sens: [1, 1, 0, 0, 1],
        InputColumns.arret: [1, 1, 2, 2, 3],
        InputColumns.is_terminus: [True, True, False, False, True],
        InputColumns.heure_theorique: [
            datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 20),
            datetime(2024, 1, 1, 10, 20), datetime(2024, 1, 1, 10, 30)
        ],
        InputColumns.heure_reelle: [
            datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 22),
            datetime(2024, 1, 1, 10, 19), datetime(2024, 1, 1, 10, 30)
        ]
    })

    expected_result = pd.DataFrame({
        InputColumns.ligne: ['A', 'A', 'A'],
        InputColumns.sens: [1, 0, 1],
        InputColumns.arret: [1, 2, 3],
        InputColumns.is_terminus: [True, False, True],
        InputColumns.heure_theorique: [
            datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 20), datetime(2024, 1, 1, 10, 30)
        ],
        InputColumns.heure_reelle: [
            datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 19), datetime(2024, 1, 1, 10, 30)
        ]
    })

    # When
    result = drop_duplicates_heure_theorique(df)

    # Then
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)


def test_drop_duplicates_heure_theorique_with_null():
    # Given
    df = pd.DataFrame({
        InputColumns.ligne: ['A', 'A', 'A', 'A', 'A'],
        InputColumns.sens: [1, 1, 0, 0, 1],
        InputColumns.arret: [1, 1, 2, 2, 3],
        InputColumns.is_terminus: [True, True, False, False, True],
        InputColumns.heure_theorique: [
            None, None, datetime(2024, 1, 1, 10, 20), datetime(2024, 1, 1, 10, 20), None
        ],
        InputColumns.heure_reelle: [
            datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 12), datetime(2024, 1, 1, 10, 22),
            datetime(2024, 1, 1, 10, 19), datetime(2024, 1, 1, 10, 30)
        ]
    })

    expected_result = pd.DataFrame({
        InputColumns.ligne: ['A', 'A', 'A', 'A'],
        InputColumns.sens: [0, 1, 1, 1],
        InputColumns.arret: [2, 1, 1, 3],
        InputColumns.is_terminus: [False, True, True, True],
        InputColumns.heure_theorique: [
            datetime(2024, 1, 1, 10, 20), None, None, None
        ],
        InputColumns.heure_reelle: [
            datetime(2024, 1, 1, 10, 19), datetime(2024, 1, 1, 10, 10), datetime(2024, 1, 1, 10, 12),
            datetime(2024, 1, 1, 10, 30)
        ]
    })

    # When
    result = drop_duplicates_heure_theorique(df)

    # Then
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)
