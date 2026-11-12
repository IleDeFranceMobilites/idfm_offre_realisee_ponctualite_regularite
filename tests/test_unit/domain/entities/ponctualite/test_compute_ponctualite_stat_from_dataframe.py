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


def test_nombre_mesures_reelles_ponctualite_one_stop():
    # Given - 1 arrêt, 4 passages réels tous assignés : le premier passage réel de l'arrêt ne compte pas comme
    # mesure réelle (par cohérence avec la régularité), bien que son score de ponctualité reste valide.
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 4,
        InputColumns.sens: [1] * 4,
        InputColumns.arret: ['A1'] * 4,
        InputColumns.heure_theorique: [
            datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
        ],
        InputColumns.heure_reelle: [
            datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:11:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:16:00+00:00"),
        ],
        InputColumns.is_terminus: [False] * 4,
        InputColumns.course_id: [f'C{i + 1}' for i in range(4)],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.nombre_reel: [4],
        MesurePonctualite.nombre_mesures_reelles: [3],
    })

    # When
    result = compute_ponctualite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[
            MesurePonctualite.ligne, MesurePonctualite.nombre_reel, MesurePonctualite.nombre_mesures_reelles
        ]].reset_index(drop=True),
        expected,
    )


def test_nombre_mesures_reelles_ponctualite_excludes_first_passage_per_arret():
    # Given - 2 arrêts distincts (A1, A2), 4 passages réels assignés chacun : chaque arrêt exclut son propre
    # premier passage réel.
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 8,
        InputColumns.sens: [1] * 8,
        InputColumns.arret: ['A1'] * 4 + ['A2'] * 4,
        InputColumns.heure_theorique: [
            datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
        ] * 2,
        InputColumns.heure_reelle: [
            datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:11:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:16:00+00:00"),
        ] * 2,
        InputColumns.is_terminus: [False] * 8,
        InputColumns.course_id: [f'C{i + 1}' for i in range(4)] * 2,
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.nombre_reel: [8],
        MesurePonctualite.nombre_mesures_reelles: [6],
    })

    # When
    result = compute_ponctualite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[
            MesurePonctualite.ligne, MesurePonctualite.nombre_reel, MesurePonctualite.nombre_mesures_reelles
        ]].reset_index(drop=True),
        expected,
    )


def test_non_passage_arret_et_si_absence_par_course():
    # Given - C1 passe aux 3 arrets, C2 ne passe pas aux arrets A1 et A2, un passage réel en surplus à A3
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 7,
        InputColumns.sens: [1] * 7,
        InputColumns.arret: ['A1', 'A2', 'A3', 'A1', 'A2', 'A3', 'A3'],
        InputColumns.heure_theorique: [
            datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:30:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:35:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:40:00+00:00"),
            None,
        ],
        InputColumns.heure_reelle: [
            datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
            datetime.fromisoformat("2023-01-01 10:11:00+00:00"),
            None,
            None,
            datetime.fromisoformat("2023-01-01 10:41:00+00:00"),
            datetime.fromisoformat("2023-01-01 12:00:00+00:00"),
        ],
        InputColumns.is_terminus: [False] * 7,
        InputColumns.course_id: ['C1', 'C1', 'C1', 'C2', 'C2', 'C2', None],
    })

    # 6 passages théoriques - 4 passages réels attribués = 2
    # C2 manque 2 arrets mais ne génère qu'une SI absence
    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.non_passage_arret: [2],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [1],
    })

    # When
    result = compute_ponctualite_stat_from_dataframe(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[
            MesurePonctualite.ligne, MesurePonctualite.non_passage_arret,
            MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue
        ]].reset_index(drop=True),
        expected,
    )
