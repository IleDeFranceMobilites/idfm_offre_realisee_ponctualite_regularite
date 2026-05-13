from datetime import datetime

import pandas as pd

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MesureRegularite
from offre_realisee.domain.entities.regularite.compute_regularite_stat_from_dataframe import (
    compute_regularite_stat_from_dataframe,
)

# 6 passages espacés de 10 min dans la même heure → haute fréquence
# diff(5) = 10:50 - 10:00 = 50min < 1h
_HF_THEORIQUE = [datetime.fromisoformat(f"2023-01-01 10:{i * 10:02d}:00+00:00") for i in range(6)]
_HF_REELLE = [datetime.fromisoformat(f"2023-01-01 10:{i * 10:02d}:01+00:00") for i in range(6)]


def test_nb_courses_theoriques_regularite_all_have_theorique():
    # Given - 6 courses haute fréquence, toutes avec heure_theorique
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 6,
        InputColumns.sens: [1] * 6,
        InputColumns.arret: ['A1'] * 6,
        InputColumns.heure_theorique: _HF_THEORIQUE,
        InputColumns.heure_reelle: _HF_REELLE,
        InputColumns.is_terminus: [False] * 6,
        InputColumns.course_id: [f'C{i + 1}' for i in range(6)],
    })

    expected = pd.DataFrame({
        MesureRegularite.ligne: ['L1'],
        MesureRegularite.nb_courses_theoriques: [6],
    })

    # When
    result = compute_regularite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesureRegularite.ligne, MesureRegularite.nb_courses_theoriques]].reset_index(drop=True),
        expected,
    )


def test_nb_courses_theoriques_regularite_excludes_courses_without_theorique():
    # Given - 6 courses HF + 1 course sans heure_theorique
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 6 + ['L1'],
        InputColumns.sens: [1] * 6 + [1],
        InputColumns.arret: ['A1'] * 6 + ['A1'],
        InputColumns.heure_theorique: _HF_THEORIQUE + [None],
        InputColumns.heure_reelle: _HF_REELLE + [datetime.fromisoformat("2023-01-01 10:03:00+00:00")],
        InputColumns.is_terminus: [False] * 7,
        InputColumns.course_id: [f'C{i + 1}' for i in range(6)] + ['C_extra'],
    })

    expected = pd.DataFrame({
        MesureRegularite.ligne: ['L1'],
        MesureRegularite.nb_courses_theoriques: [6],
    })

    # When
    result = compute_regularite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesureRegularite.ligne, MesureRegularite.nb_courses_theoriques]].reset_index(drop=True),
        expected,
    )


def test_nb_courses_theoriques_regularite_counts_course_once_across_multiple_stops():
    # Given - les mêmes 6 courses présentes à 2 arrets (A1 et A2)
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 12,
        InputColumns.sens: [1] * 12,
        InputColumns.arret: ['A1'] * 6 + ['A2'] * 6,
        InputColumns.heure_theorique: _HF_THEORIQUE * 2,
        InputColumns.heure_reelle: _HF_REELLE * 2,
        InputColumns.is_terminus: [False] * 12,
        InputColumns.course_id: [f'C{i + 1}' for i in range(6)] * 2,
    })

    expected = pd.DataFrame({
        MesureRegularite.ligne: ['L1'],
        MesureRegularite.nb_courses_theoriques: [6],
    })

    # When
    result = compute_regularite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesureRegularite.ligne, MesureRegularite.nb_courses_theoriques]].reset_index(drop=True),
        expected,
    )