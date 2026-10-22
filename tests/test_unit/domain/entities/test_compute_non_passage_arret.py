from datetime import datetime

import pandas as pd

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MesurePonctualite
from offre_realisee.domain.entities.compute_non_passage_arret import compute_non_passage_arret

_T1 = datetime.fromisoformat("2023-01-01 10:00:00+00:00")
_T2 = datetime.fromisoformat("2023-01-01 10:30:00+00:00")
_T3 = datetime.fromisoformat("2023-01-01 11:00:00+00:00")


def test_compute_non_passage_arret_theorique_superieur_reel():
    # Given - 3 passages théoriques, 1 seul passage réel
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 3,
        InputColumns.sens: [1] * 3,
        InputColumns.arret: ['A1'] * 3,
        InputColumns.heure_theorique: [_T1, _T2, _T3],
        InputColumns.heure_reelle: [_T1, None, None],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.non_passage_arret: [2],
    })

    # When
    result = compute_non_passage_arret(df)

    # Then
    pd.testing.assert_frame_equal(result, expected)


def test_compute_non_passage_arret_reel_superieur_theorique():
    # Given - 1 passage théorique, 3 passages réels
    df = pd.DataFrame({
        InputColumns.ligne: ['L1'] * 3,
        InputColumns.sens: [1] * 3,
        InputColumns.arret: ['A1'] * 3,
        InputColumns.heure_theorique: [_T1, None, None],
        InputColumns.heure_reelle: [_T1, _T2, _T3],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1'],
        MesurePonctualite.non_passage_arret: [0],
    })

    # When
    result = compute_non_passage_arret(df)

    # Then
    pd.testing.assert_frame_equal(result, expected)


def test_compute_non_passage_arret_somme_par_ligne():
    # Given
    # L1 sens 1 A1 : 2 théoriques, 1 réel -> 1
    # L1 sens 2 A1 : 1 théorique, 0 réel -> 1
    # L1 sens 1 A2 : 1 théorique, 2 réels -> 0 (pas de compensation entre arrêts)
    # L2 sens 1 A1 : 1 théorique, 1 réel -> 0
    df = pd.DataFrame({
        InputColumns.ligne: ['L1', 'L1', 'L1', 'L1', 'L1', 'L2'],
        InputColumns.sens: [1, 1, 2, 1, 1, 1],
        InputColumns.arret: ['A1', 'A1', 'A1', 'A2', 'A2', 'A1'],
        InputColumns.heure_theorique: [_T1, _T2, _T1, _T1, None, _T1],
        InputColumns.heure_reelle: [_T1, None, None, _T1, _T2, _T1],
    })

    expected = pd.DataFrame({
        MesurePonctualite.ligne: ['L1', 'L2'],
        MesurePonctualite.non_passage_arret: [2, 0],
    })

    # When
    result = compute_non_passage_arret(df)

    # Then
    pd.testing.assert_frame_equal(result, expected)
