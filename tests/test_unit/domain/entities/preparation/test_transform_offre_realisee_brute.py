import pandas as pd
import pytest

from offre_realisee.config.input_brute_config import InputBruteColumns
from offre_realisee.config.input_config import InputColumns
from offre_realisee.domain.entities.preparation.transform_offre_realisee_brute import (COLONNES_OFFRE_REALISEE,
                                                                                      transform_offre_realisee_brute)


def offre_realisee_brute(**kwargs) -> pd.DataFrame:
    """Construit un DataFrame brut d'une ligne, dont chaque colonne peut être surchargée."""
    ligne_brute = {
        InputBruteColumns.jour: '2023-09-27',
        InputBruteColumns.ligne: '150',
        InputBruteColumns.sens: 'GP->VIL',
        InputBruteColumns.arret: '4CH',
        InputBruteColumns.course_id: 1,
        InputBruteColumns.is_terminus: False,
        InputBruteColumns.heure_theorique_depart: pd.Timestamp('2023-09-27 06:00:00'),
        InputBruteColumns.heure_theorique_arrivee: pd.Timestamp('2023-09-27 05:59:00'),
        InputBruteColumns.heure_reelle_depart: pd.Timestamp('2023-09-27 06:02:00'),
        InputBruteColumns.heure_reelle_arrivee: pd.Timestamp('2023-09-27 06:01:00'),
        InputBruteColumns.passage_evaluable: True,
    }
    ligne_brute.update(kwargs)

    return pd.DataFrame([ligne_brute])


def test_transform_offre_realisee_brute_heure_de_depart_prioritaire():
    # Given
    df = offre_realisee_brute()

    # When
    result = transform_offre_realisee_brute(df)

    # Assert
    assert list(result.columns) == COLONNES_OFFRE_REALISEE
    assert result[InputColumns.heure_theorique].iloc[0] == pd.Timestamp('2023-09-27 06:00:00', tz='UTC')
    assert result[InputColumns.heure_reelle].iloc[0] == pd.Timestamp('2023-09-27 06:02:00', tz='UTC')
    assert str(result[InputColumns.heure_theorique].dtype) == 'datetime64[ns, UTC]'
    assert str(result[InputColumns.heure_reelle].dtype) == 'datetime64[ns, UTC]'


def test_transform_offre_realisee_brute_heure_arrivee_si_pas_de_depart():
    # Given - cas du terminus d'arrivée, qui n'a pas d'heure de départ
    df = offre_realisee_brute(**{
        InputBruteColumns.is_terminus: True,
        InputBruteColumns.heure_theorique_depart: pd.NaT,
        InputBruteColumns.heure_reelle_depart: pd.NaT,
    })

    # When
    result = transform_offre_realisee_brute(df)

    # Assert
    assert result[InputColumns.heure_theorique].iloc[0] == pd.Timestamp('2023-09-27 05:59:00', tz='UTC')
    assert result[InputColumns.heure_reelle].iloc[0] == pd.Timestamp('2023-09-27 06:01:00', tz='UTC')


def test_transform_offre_realisee_brute_filtre_les_passages_non_evaluables():
    # Given
    df = pd.concat([
        offre_realisee_brute(**{InputBruteColumns.arret: 'EVALUABLE'}),
        offre_realisee_brute(**{InputBruteColumns.arret: 'NON_EVALUABLE',
                                InputBruteColumns.passage_evaluable: False}),
        offre_realisee_brute(**{InputBruteColumns.arret: 'NON_RENSEIGNE',
                                InputBruteColumns.passage_evaluable: None}),
    ], ignore_index=True)

    # When
    result = transform_offre_realisee_brute(df)

    # Assert
    assert result[InputColumns.arret].tolist() == ['EVALUABLE']


def test_transform_offre_realisee_brute_conserve_les_heures_nulles():
    # Given - un passage réel non prévu (sans heure théorique) et un passage théorique sans heure réelle
    df = pd.concat([
        offre_realisee_brute(**{InputBruteColumns.arret: 'PASSAGE_NON_PREVU',
                                InputBruteColumns.heure_theorique_depart: pd.NaT,
                                InputBruteColumns.heure_theorique_arrivee: pd.NaT}),
        offre_realisee_brute(**{InputBruteColumns.arret: 'ABSENCE_DE_DONNEES',
                                InputBruteColumns.heure_reelle_depart: pd.NaT,
                                InputBruteColumns.heure_reelle_arrivee: pd.NaT}),
    ], ignore_index=True)

    # When
    result = transform_offre_realisee_brute(df)

    # Assert
    assert result[InputColumns.arret].tolist() == ['PASSAGE_NON_PREVU', 'ABSENCE_DE_DONNEES']
    assert pd.isna(result[InputColumns.heure_theorique].iloc[0])
    assert pd.isna(result[InputColumns.heure_reelle].iloc[1])


def test_transform_offre_realisee_brute_heures_deja_localisees():
    # Given
    df = offre_realisee_brute(**{
        InputBruteColumns.heure_theorique_depart: pd.Timestamp('2023-09-27 08:00:00', tz='Europe/Paris'),
        InputBruteColumns.heure_reelle_depart: pd.Timestamp('2023-09-27 08:02:00', tz='Europe/Paris'),
    })

    # When
    result = transform_offre_realisee_brute(df)

    # Assert
    assert result[InputColumns.heure_theorique].iloc[0] == pd.Timestamp('2023-09-27 06:00:00', tz='UTC')
    assert result[InputColumns.heure_reelle].iloc[0] == pd.Timestamp('2023-09-27 06:02:00', tz='UTC')


def test_transform_offre_realisee_brute_colonne_manquante():
    # Given
    df = offre_realisee_brute().drop(columns=[InputBruteColumns.course_id, InputBruteColumns.passage_evaluable])

    # When / Assert
    with pytest.raises(ValueError, match=InputBruteColumns.passage_evaluable):
        transform_offre_realisee_brute(df)


def test_transform_offre_realisee_brute_passage_evaluable_non_booleen():
    # Given
    df = offre_realisee_brute(**{InputBruteColumns.passage_evaluable: 'false'})

    # When / Assert
    with pytest.raises(ValueError, match=InputBruteColumns.passage_evaluable):
        transform_offre_realisee_brute(df)
