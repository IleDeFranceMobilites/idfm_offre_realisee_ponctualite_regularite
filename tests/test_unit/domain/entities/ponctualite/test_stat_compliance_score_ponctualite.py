import pandas as pd

from offre_realisee.config.offre_realisee_config import FrequenceType, MesurePonctualite, ComplianceType, MesureType
from offre_realisee.domain.entities.ponctualite.stat_compliance_score_ponctualite import (
    stat_compliance_score_ponctualite, stat_situation_inacceptable
)


def test_stat_compliance_score_ponctualite():
    # Given
    df = pd.DataFrame({
        MesurePonctualite.ligne: [1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
        MesurePonctualite.arret: [1, 1, 1, 1, 1, 2, 2, 2, 2, 1],
        MesurePonctualite.sens: [1, 1, 2, 2, 2, 1, 1, 2, 2, 1],
        MesurePonctualite.resultat: [
            ComplianceType.compliant,
            ComplianceType.situation_inacceptable_retard,
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.situation_inacceptable_absence,
            ComplianceType.compliant,
            ComplianceType.compliant,
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.compliant,
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence]]
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.ligne: [1, 2],
        MesurePonctualite.nombre_theorique: [9, 1],
        MesurePonctualite.nombre_reel: [8, 1],
        MesurePonctualite.score_de_conformite: [5.0, 0.5],
        MesurePonctualite.situation_inacceptable_avance: [0, 0],
        MesurePonctualite.situation_inacceptable_retard: [1, 0],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [1, 0],
        MesurePonctualite.situation_inacceptable_total: [2, 0],
        MesurePonctualite.taux_de_conformite: [55.56, 50.0],
        MesurePonctualite.taux_absence_de_donnees: [11.11, 0.0]
    })

    # When
    result = stat_compliance_score_ponctualite(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_stat_situation_inacceptable():
    # Given
    df = pd.DataFrame({
        MesurePonctualite.ligne: [1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
        MesurePonctualite.arret: [1, 1, 1, 1, 1, 2, 2, 2, 2, 1],
        MesurePonctualite.sens: [1, 1, 2, 2, 2, 1, 1, 2, 2, 1],
        MesurePonctualite.resultat: [
            ComplianceType.situation_inacceptable_absence,
            ComplianceType.situation_inacceptable_retard,
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.situation_inacceptable_absence,
            ComplianceType.compliant,
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.compliant,
            ComplianceType.situation_inacceptable_avance
        ]
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.ligne: [1, 2],
        MesurePonctualite.situation_inacceptable_avance: [0, 1],
        MesurePonctualite.situation_inacceptable_retard: [1, 0],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [2, 0],
        MesurePonctualite.situation_inacceptable_total: [3, 1],
    })

    # When
    result = stat_situation_inacceptable(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_stat_situation_inacceptable_keep_max():
    # Given
    df = pd.DataFrame({
        MesurePonctualite.ligne: [1, 1],
        MesurePonctualite.arret: [1, 2],
        MesurePonctualite.sens: [1, 1],
        MesurePonctualite.resultat: [ComplianceType.compliant, ComplianceType.situation_inacceptable_absence]
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.ligne: [1],
        MesurePonctualite.situation_inacceptable_avance: [0],
        MesurePonctualite.situation_inacceptable_retard: [0],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [1],
        MesurePonctualite.situation_inacceptable_total: [1],
    })

    # When
    result = stat_situation_inacceptable(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_stat_situation_inacceptable_keep_max_on_multiple_si():
    # Given
    df = pd.DataFrame({
        MesurePonctualite.ligne: [1, 1, 1, 1],
        MesurePonctualite.arret: [1, 1, 2, 2],
        MesurePonctualite.sens: [1, 1, 1, 1],
        MesurePonctualite.resultat: [
            ComplianceType.compliant, ComplianceType.situation_inacceptable_absence,
            ComplianceType.situation_inacceptable_avance, ComplianceType.situation_inacceptable_avance,
        ]
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.ligne: [1],
        MesurePonctualite.situation_inacceptable_avance: [2],
        MesurePonctualite.situation_inacceptable_retard: [0],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [0],
        MesurePonctualite.situation_inacceptable_total: [2],
    })

    # When
    result = stat_situation_inacceptable(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_stat_situation_inacceptable_add_si_sens():
    # Given
    df = pd.DataFrame({
        MesurePonctualite.ligne: [1, 1],
        MesurePonctualite.arret: [1, 1],
        MesurePonctualite.sens: [1, 2],
        MesurePonctualite.resultat: [
            ComplianceType.situation_inacceptable_absence, ComplianceType.situation_inacceptable_avance
        ]
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.ligne: [1],
        MesurePonctualite.situation_inacceptable_avance: [1],
        MesurePonctualite.situation_inacceptable_retard: [0],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [1],
        MesurePonctualite.situation_inacceptable_total: [2],
    })

    # When
    result = stat_situation_inacceptable(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)
