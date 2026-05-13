from datetime import datetime

import pandas as pd

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MesurePonctualite
from offre_realisee.domain.entities.ponctualite.compute_ponctualite_stat_from_dataframe import (
    compute_ponctualite_stat_from_dataframe,
)


def test_nb_courses_theoriques_all_have_theorique():
    # Given - 2 courses, toutes avec heure_theorique
    df = pd.DataFrame({
        InputColumns.ligne: ['L1', 'L1'],
        InputColumns.sens: [1, 1],
        InputColumns.arret: ['A1', 'A1'],
        InputColumns.heure_theorique: [
            datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
        ],
        InputColumns.heure_reelle: [
            datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
        ],
        InputColumns.is_terminus: [False, False],
        InputColumns.course_id: ['C1', 'C2'],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.nb_courses_theoriques: [2],
    })

    # When
    result = compute_ponctualite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesurePonctualite.ligne, MesurePonctualite.nb_courses_theoriques]].reset_index(drop=True),
        expected,
    )


def test_nb_courses_theoriques_excludes_courses_without_theorique():
    # Given - 3 courses, 1 sans heure_theorique
    df = pd.DataFrame({
        InputColumns.ligne: ['L1', 'L1', 'L1'],
        InputColumns.sens: [1, 1, 1],
        InputColumns.arret: ['A1', 'A1', 'A1'],
        InputColumns.heure_theorique: [
            datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
            None,
        ],
        InputColumns.heure_reelle: [
            datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
        ],
        InputColumns.is_terminus: [False, False, False],
        InputColumns.course_id: ['C1', 'C2', 'C3'],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.nb_courses_theoriques: [2],
    })

    # When
    result = compute_ponctualite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesurePonctualite.ligne, MesurePonctualite.nb_courses_theoriques]].reset_index(drop=True),
        expected,
    )


def test_nb_courses_theoriques_counts_course_once_across_multiple_stops():
    # Given - 1 course (C1) présente à 2 arrets différents
    df = pd.DataFrame({
        InputColumns.ligne: ['L1', 'L1'],
        InputColumns.sens: [1, 1],
        InputColumns.arret: ['A1', 'A2'],
        InputColumns.heure_theorique: [
            datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
        ],
        InputColumns.heure_reelle: [
            datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
        ],
        InputColumns.is_terminus: [False, False],
        InputColumns.course_id: ['C1', 'C1'],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.nb_courses_theoriques: [1],
    })

    # When
    result = compute_ponctualite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesurePonctualite.ligne, MesurePonctualite.nb_courses_theoriques]].reset_index(drop=True),
        expected,
    )