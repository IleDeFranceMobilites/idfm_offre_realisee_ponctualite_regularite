from datetime import datetime, timedelta
import numpy as np

import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite, ComplianceType
from offre_realisee.domain.entities.regularite.compliance_score import (
    choose_best_score, select_closest_defined_time_result, select_best_score_if_equals, set_first_record_to_compliant
)


def test_choose_best_score():
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0), datetime(2023, 1, 1, 11, 0),
                                        datetime(2023, 1, 1, 11, 5), datetime(2023, 1, 1, 11, 7),
                                        datetime(2023, 1, 1, 11, 15), datetime(2023, 1, 1, 11, 24),
                                        datetime(2023, 1, 1, 11, 37), datetime(2023, 1, 1, 11, 51),
                                        datetime(2023, 1, 1, 11, 57), datetime(2023, 1, 1, 11, 59)],
        MesureRegularite.difference_reelle: [None, timedelta(minutes=60), timedelta(minutes=5),
                                             timedelta(minutes=2), timedelta(minutes=8), timedelta(minutes=9),
                                             timedelta(minutes=13), timedelta(minutes=14),
                                             timedelta(minutes=6), timedelta(minutes=2)],
        MesureRegularite.heure_theorique_inf: [datetime(2023, 1, 1, 9, 50), datetime(2023, 1, 1, 10, 54),
                                               datetime(2023, 1, 1, 11, 1), datetime(2023, 1, 1, 11, 6),
                                               datetime(2023, 1, 1, 11, 7), datetime(2023, 1, 1, 11, 16),
                                               datetime(2023, 1, 1, 11, 31), datetime(2023, 1, 1, 11, 50),
                                               datetime(2023, 1, 1, 11, 56), datetime(2023, 1, 1, 11, 58)],
        MesureRegularite.difference_theorique_inf: [None, timedelta(minutes=64), timedelta(minutes=7),
                                                    timedelta(minutes=5), timedelta(minutes=1),
                                                    timedelta(minutes=9), timedelta(minutes=15),
                                                    timedelta(minutes=19), timedelta(minutes=6),
                                                    timedelta(minutes=2)],
        MesureRegularite.heure_theorique_sup: [datetime(2023, 1, 1, 10, 3), datetime(2023, 1, 1, 11, 3),
                                               datetime(2023, 1, 1, 11, 7), datetime(2023, 1, 1, 11, 12),
                                               datetime(2023, 1, 1, 11, 19), datetime(2023, 1, 1, 11, 27),
                                               datetime(2023, 1, 1, 11, 38), datetime(2023, 1, 1, 11, 55),
                                               datetime(2023, 1, 1, 12, 1), None],
        MesureRegularite.difference_theorique_sup: [timedelta(minutes=7), timedelta(minutes=20),
                                                    timedelta(minutes=5), timedelta(minutes=7),
                                                    timedelta(minutes=3), timedelta(minutes=6),
                                                    timedelta(minutes=10), timedelta(minutes=21),
                                                    timedelta(minutes=7), None],
        MesureRegularite.resultat_inf: [
            None, ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant,
            ComplianceType.situation_inacceptable_faible_frequence, ComplianceType.compliant,
            ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant
        ],
        MesureRegularite.resultat_sup: [
            None, ComplianceType.situation_inacceptable_faible_frequence, ComplianceType.compliant,
            ComplianceType.compliant, ComplianceType.situation_inacceptable_faible_frequence,
            ComplianceType.semi_compliant, ComplianceType.semi_compliant, ComplianceType.compliant,
            ComplianceType.compliant, None]
    })

    expected_result = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime(2023, 1, 1, 10, 0), datetime(2023, 1, 1, 11, 0),
                datetime(2023, 1, 1, 11, 5), datetime(2023, 1, 1, 11, 7),
                datetime(2023, 1, 1, 11, 15), datetime(2023, 1, 1, 11, 24),
                datetime(2023, 1, 1, 11, 37), datetime(2023, 1, 1, 11, 51),
                datetime(2023, 1, 1, 11, 57), datetime(2023, 1, 1, 11, 59)],
            MesureRegularite.resultat: [
                ComplianceType.compliant, ComplianceType.situation_inacceptable_faible_frequence,
                ComplianceType.compliant, ComplianceType.compliant,
                ComplianceType.situation_inacceptable_faible_frequence, ComplianceType.semi_compliant,
                ComplianceType.semi_compliant, ComplianceType.compliant, ComplianceType.compliant,
                ComplianceType.compliant
            ]
        }
    )

    # When
    result = choose_best_score(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_select_closest_defined_time_result_closer_to_sup():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.heure_theorique_inf: [datetime(2023, 1, 1, 9, 50)],
        MesureRegularite.heure_theorique_sup: [datetime(2023, 1, 1, 10, 3)],
        MesureRegularite.resultat_inf: [ComplianceType.compliant],
        MesureRegularite.resultat_sup: [ComplianceType.semi_compliant]
    })
    df[MesureRegularite.resultat] = np.NaN

    expected_result = ComplianceType.semi_compliant

    # When
    result = select_closest_defined_time_result(df)

    # Then
    assert result.loc[0, MesureRegularite.resultat] == expected_result


def test_select_closest_defined_time_result_closer_to_inf():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.heure_theorique_inf: [datetime(2023, 1, 1, 9, 58)],
        MesureRegularite.heure_theorique_sup: [datetime(2023, 1, 1, 10, 23)],
        MesureRegularite.resultat_inf: [ComplianceType.compliant],
        MesureRegularite.resultat_sup: [ComplianceType.semi_compliant]
    })
    df[MesureRegularite.resultat] = np.NaN

    expected_result = ComplianceType.compliant

    # When
    result = select_closest_defined_time_result(df)

    # Then
    assert result.loc[0, MesureRegularite.resultat] == expected_result


def test_select_closest_defined_time_result_inf_undefined():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.heure_theorique_inf: [pd.NaT],
        MesureRegularite.heure_theorique_sup: [datetime(2023, 1, 1, 10, 23)],
        MesureRegularite.resultat_inf: [ComplianceType.compliant],
        MesureRegularite.resultat_sup: [ComplianceType.semi_compliant]
    })
    df[MesureRegularite.resultat] = np.NaN

    expected_result = ComplianceType.semi_compliant

    # When
    result = select_closest_defined_time_result(df)

    # Then
    assert result.loc[0, MesureRegularite.resultat] == expected_result


def test_select_closest_defined_time_result_sup_undefined():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.heure_theorique_inf: [datetime(2023, 1, 1, 9, 58)],
        MesureRegularite.heure_theorique_sup: [pd.NaT],
        MesureRegularite.resultat_inf: [ComplianceType.compliant],
        MesureRegularite.resultat_sup: [ComplianceType.semi_compliant]
    })
    df[MesureRegularite.resultat] = np.NaN

    expected_result = ComplianceType.compliant

    # When
    result = select_closest_defined_time_result(df)

    # Then
    assert result.loc[0, MesureRegularite.resultat] == expected_result


def test_select_closest_defined_time_result_both_undefined():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.heure_theorique_inf: [pd.NaT],
        MesureRegularite.heure_theorique_sup: [pd.NaT],
        MesureRegularite.resultat_inf: [ComplianceType.compliant],
        MesureRegularite.resultat_sup: [ComplianceType.semi_compliant]
    })
    df[MesureRegularite.resultat] = np.NaN

    # When
    result = select_closest_defined_time_result(df)

    # Then
    assert np.isnan(result.loc[0, MesureRegularite.resultat])


def test_select_closest_defined_time_result_both_as_close():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.heure_theorique_inf: [datetime(2023, 1, 1, 9, 58)],
        MesureRegularite.heure_theorique_sup: [datetime(2023, 1, 1, 10, 2)],
        MesureRegularite.resultat_inf: [ComplianceType.compliant],
        MesureRegularite.resultat_sup: [ComplianceType.semi_compliant]
    })
    df[MesureRegularite.resultat] = np.NaN

    # When
    result = select_closest_defined_time_result(df)

    # Then
    assert np.isnan(result.loc[0, MesureRegularite.resultat])


def test_select_best_score_if_equals():
    # Given
    df = pd.DataFrame({
        MesureRegularite.resultat_inf: [ComplianceType.compliant, ComplianceType.not_compliant],
        MesureRegularite.resultat_sup: [
            ComplianceType.semi_compliant, ComplianceType.situation_inacceptable_faible_frequence],
        MesureRegularite.resultat: [ComplianceType.semi_compliant, np.NaN]
    })

    expected_result = pd.DataFrame({
        MesureRegularite.resultat: [ComplianceType.semi_compliant, ComplianceType.not_compliant]
    })

    # When
    result = select_best_score_if_equals(df)

    # Then
    pd.testing.assert_frame_equal(result[[MesureRegularite.resultat]], expected_result)


def test_set_first_record_to_compliant():
    # Given
    df = pd.DataFrame({
        MesureRegularite.heure_reelle: [datetime(2023, 1, 1, 11, 0), datetime(2023, 1, 1, 10, 0)],
        MesureRegularite.resultat: [ComplianceType.situation_inacceptable_train_de_bus, np.NaN]
    })

    expected_result = pd.DataFrame({
        MesureRegularite.resultat: [ComplianceType.situation_inacceptable_train_de_bus, ComplianceType.compliant]
    })

    # When
    result = set_first_record_to_compliant(df)

    # Then
    pd.testing.assert_frame_equal(result[[MesureRegularite.resultat]], expected_result)
