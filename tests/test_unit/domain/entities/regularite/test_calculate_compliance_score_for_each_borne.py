from datetime import timedelta

import numpy as np
import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite, ComplianceType, MesureType
from offre_realisee.domain.entities.regularite.compliance_score import \
    calculate_compliance_score_for_each_borne


def test_calculate_compliance_score_for_each_borne():
    # Given
    df = pd.DataFrame({
        MesureRegularite.difference_reelle: [None, timedelta(minutes=60), timedelta(minutes=5),
                                             timedelta(minutes=2), timedelta(minutes=8), timedelta(minutes=9),
                                             timedelta(minutes=13), timedelta(minutes=14),
                                             timedelta(minutes=6), timedelta(minutes=2)],
        MesureRegularite.difference_theorique_inf: [None, timedelta(minutes=64), timedelta(minutes=7),
                                                    timedelta(minutes=5), timedelta(minutes=1),
                                                    timedelta(minutes=9), timedelta(minutes=15),
                                                    timedelta(minutes=19), timedelta(minutes=6),
                                                    timedelta(minutes=2)],
        MesureRegularite.difference_theorique_sup: [timedelta(minutes=7), timedelta(minutes=20),
                                                    timedelta(minutes=5), timedelta(minutes=7),
                                                    timedelta(minutes=3), timedelta(minutes=6),
                                                    timedelta(minutes=10), timedelta(minutes=21),
                                                    timedelta(minutes=7), None]
    })

    expected_result = pd.DataFrame({
        MesureRegularite.resultat_inf: [
            None, ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant,
            ComplianceType.situation_inacceptable_faible_frequence, ComplianceType.compliant,
            ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant],
        MesureRegularite.resultat_sup: [
            None, ComplianceType.situation_inacceptable_faible_frequence, ComplianceType.compliant,
            ComplianceType.compliant, ComplianceType.situation_inacceptable_faible_frequence,
            ComplianceType.semi_compliant[MesureType.regularite],
            ComplianceType.semi_compliant[MesureType.regularite],
            ComplianceType.compliant, ComplianceType.compliant, None]
    })

    # When
    result = calculate_compliance_score_for_each_borne(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesureRegularite.resultat_inf, MesureRegularite.resultat_sup]], expected_result)


def test_calculate_compliance_score_for_each_borne_train_de_bus():
    # Given
    df = pd.DataFrame({
        MesureRegularite.difference_reelle: [None, timedelta(minutes=1)],
        MesureRegularite.difference_theorique_inf: [None, timedelta(minutes=5)],
        MesureRegularite.difference_theorique_sup: [timedelta(minutes=5), None]
    })

    expected_result = pd.DataFrame({
        MesureRegularite.resultat_inf: [np.nan, ComplianceType.situation_inacceptable_train_de_bus],
        MesureRegularite.resultat_sup: [np.nan, ComplianceType.situation_inacceptable_train_de_bus]
    })

    # When
    result = calculate_compliance_score_for_each_borne(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesureRegularite.resultat_inf, MesureRegularite.resultat_sup]], expected_result)


def test_calculate_compliance_score_for_each_borne_too_large_interval():
    # Given
    df = pd.DataFrame({
        MesureRegularite.difference_reelle: [None, timedelta(minutes=25)],
        MesureRegularite.difference_theorique_inf: [None, timedelta(minutes=5)],
        MesureRegularite.difference_theorique_sup: [timedelta(minutes=5), None]
    })

    expected_result = pd.DataFrame({
        MesureRegularite.resultat_inf: [np.nan, ComplianceType.situation_inacceptable_faible_frequence],
        MesureRegularite.resultat_sup: [np.nan, np.nan]
    })

    # When
    result = calculate_compliance_score_for_each_borne(df)

    # Then
    pd.testing.assert_frame_equal(
        result[[MesureRegularite.resultat_inf, MesureRegularite.resultat_sup]], expected_result)
