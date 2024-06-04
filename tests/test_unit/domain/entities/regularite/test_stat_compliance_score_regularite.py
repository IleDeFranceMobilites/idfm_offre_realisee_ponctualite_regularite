import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite, ComplianceType, MesureType
from offre_realisee.domain.entities.regularite.stat_compliance_score_regularite import (
    stat_compliance_score_regularite
)


def test_stat_regularite_compliance_score():
    # Given
    df = pd.DataFrame({
        MesureRegularite.ligne: ["1", "1", "1", "1", "2", "2", "2", "2", "2", "3"],
        MesureRegularite.arret: [1, 1, 1, 2, 3, 3, 3, 4, 4, 5],
        MesureRegularite.sens: [1, 1, 1, 2, 3, 3, 3, 4, 4, 5],
        MesureRegularite.resultat: [
            ComplianceType.compliant, ComplianceType.situation_inacceptable_faible_frequence,
            ComplianceType.semi_compliant[MesureType.regularite], ComplianceType.situation_inacceptable_train_de_bus,
            ComplianceType.situation_inacceptable_train_de_bus, ComplianceType.compliant, ComplianceType.compliant,
            ComplianceType.semi_compliant[MesureType.regularite], ComplianceType.compliant,
            ComplianceType.semi_compliant[MesureType.regularite]
        ]
    })
    n_theorique_by_lignes = {"1": 5, "2": 7, "3": 1}
    any_high_frequency_on_lignes = {"1": True, "2": True, "3": True}

    expected_result = pd.DataFrame({
        MesureRegularite.ligne: ["1", "2", "3"],
        MesureRegularite.score_de_conformite: [1.5, 3.5, 0.5],
        MesureRegularite.situation_inacceptable_train_de_bus: [1, 1, 0],
        MesureRegularite.situation_inacceptable_ecart_important: [1, 0, 0],
        MesureRegularite.situation_inacceptable_total: [2, 1, 0],
        MesureRegularite.nombre_theorique: [5, 7, 1],
        MesureRegularite.nombre_reel: [4, 5, 1],
        MesureRegularite.taux_de_conformite: [30.0, 50.0, 50.0],
        MesureRegularite.taux_absence_de_donnees: [20.0, 28.57, 0.0]
    })

    # When
    result = stat_compliance_score_regularite(df=df, n_theorique_by_lignes=n_theorique_by_lignes,
                                              any_high_frequency_on_lignes=any_high_frequency_on_lignes)

    # Then
    pd.testing.assert_frame_equal(result.sort_index(axis=1), expected_result.sort_index(axis=1))


def test_stat_regularite_compliance_score_no_high_frequency():
    # Given
    df = pd.DataFrame({
        MesureRegularite.ligne: ["1", "2"],
        MesureRegularite.arret: [1, 1],
        MesureRegularite.sens: [1, 1],
        MesureRegularite.resultat: [ComplianceType.compliant, ComplianceType.compliant],
    })
    n_theorique_by_lignes = {"1": 1, "2": 1}
    any_high_frequency_on_lignes = {"1": False, "2": True}

    expected_result = pd.DataFrame({
        MesureRegularite.ligne: ["2"],
        MesureRegularite.score_de_conformite: [1.],
        MesureRegularite.situation_inacceptable_train_de_bus: [0],
        MesureRegularite.situation_inacceptable_ecart_important: [0],
        MesureRegularite.situation_inacceptable_total: [0],
        MesureRegularite.nombre_theorique: [1],
        MesureRegularite.nombre_reel: [1],
        MesureRegularite.taux_de_conformite: [100.],
        MesureRegularite.taux_absence_de_donnees: [0.],
    })

    # When
    result = stat_compliance_score_regularite(df=df, n_theorique_by_lignes=n_theorique_by_lignes,
                                              any_high_frequency_on_lignes=any_high_frequency_on_lignes)

    # Then
    pd.testing.assert_frame_equal(result.sort_index(axis=1), expected_result.sort_index(axis=1))
