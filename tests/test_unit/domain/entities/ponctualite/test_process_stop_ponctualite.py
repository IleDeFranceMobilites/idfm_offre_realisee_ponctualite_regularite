from datetime import datetime

import numpy as np
import pandas as pd

from offre_realisee.config.offre_realisee_config import MesurePonctualite, FrequenceType, ComplianceType
from offre_realisee.domain.entities.ponctualite.process_stop_ponctualite import process_stop_ponctualite


def test_process_stop_ponctualite():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [
                FrequenceType.haute_frequence, FrequenceType.haute_frequence, np.NaN, FrequenceType.basse_frequence,
                FrequenceType.haute_frequence, FrequenceType.basse_frequence, FrequenceType.haute_frequence,
                FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:20:00+00:00"),
                datetime.fromisoformat("2023-01-01 14:30:00+00:00"),
                datetime.fromisoformat("2023-01-01 18:30:00+00:00"),],
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 19:30:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:02:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:22:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:29:00+00:00"),
                datetime.fromisoformat("2023-01-01 14:00:00+00:00"),],
            MesurePonctualite.is_terminus: [False, False, False, False, False, False, False, True],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [
                FrequenceType.haute_frequence, FrequenceType.haute_frequence, FrequenceType.basse_frequence,
                FrequenceType.haute_frequence, FrequenceType.basse_frequence, FrequenceType.haute_frequence,
                FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:20:00+00:00"),
                datetime.fromisoformat("2023-01-01 14:30:00+00:00"),
                datetime.fromisoformat("2023-01-01 18:30:00+00:00"),],
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00"),
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:22:00+00:00"),
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:29:00+00:00"),],
            MesurePonctualite.is_terminus: [False, False, False, False, False, False, True],
            MesurePonctualite.resultat: [
                ComplianceType.compliant, ComplianceType.compliant, ComplianceType.compliant,
                ComplianceType.situation_inacceptable_absence, ComplianceType.compliant,
                ComplianceType.situation_inacceptable_absence, ComplianceType.compliant],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_small_set():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:54:00+00:00"),],
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 19:30:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:58:49+00:00"),],
            MesurePonctualite.is_terminus: [False, False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            # Les valeurs d'heure theorique sont triées
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:54:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),],
            # 09:58:49 est associé à 09:59 car il est compliant tandis qu'il serait semi_compliant avec 09:54
            # 19:30 génère de toute façon une SI, il est associé à 09:54 pour permettre d'avoir un "compliant" sur 09:59
            # 19:30 ayant plus d'une heure de retard, il n'est pas assigné
            MesurePonctualite.heure_reelle: [
                pd.NaT,
                datetime.fromisoformat("2023-01-01 09:58:49+00:00"),],
            MesurePonctualite.is_terminus: [False, False],
            MesurePonctualite.resultat: [ComplianceType.situation_inacceptable_absence,
                                         ComplianceType.compliant],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_small_set_less_reel():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:54:00+00:00")],
            MesurePonctualite.heure_reelle: [
                pd.NaT,
                datetime.fromisoformat("2023-01-01 09:58:49+00:00")],
            MesurePonctualite.is_terminus: [False, False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            # Les valeurs d'heure theorique sont triées
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:54:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:59:00+00:00")],
            # 09:58:49 est associé à 09:59 car il est compliant tandis qu'il serait semi_compliant avec 09:54
            MesurePonctualite.heure_reelle: [
                pd.NaT,
                datetime.fromisoformat("2023-01-01 09:58:49+00:00")],
            MesurePonctualite.is_terminus: [False, False],
            MesurePonctualite.resultat: [ComplianceType.situation_inacceptable_absence,
                                         ComplianceType.compliant],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_small_set_no_assignment_because_after_next_stop():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [
                FrequenceType.haute_frequence, FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:04:00+00:00")],
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 09:58:49+00:00"),
                datetime.fromisoformat("2023-01-01 10:04:10+00:00"),
                datetime.fromisoformat("2023-01-01 10:06:18+00:00")],
            MesurePonctualite.is_terminus: [False, False, False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [
                FrequenceType.haute_frequence, FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            # Les valeurs d'heure theorique sont triées
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:04:00+00:00")],
            # 09:58:49 est associé à 09:59 car il est compliant
            # il serait not_assigned avec 10:01 car il passe avant l'arrêt précédent
            # 10:04:10 et 10:06:18 passe tous les deux après 10:04, 10:01 n'a donc pas d'arrêt assigné
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 09:58:49+00:00"),
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:04:10+00:00")],
            MesurePonctualite.is_terminus: [False, False, False],
            MesurePonctualite.resultat: [
                ComplianceType.compliant, ComplianceType.situation_inacceptable_absence, ComplianceType.compliant],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_small_set_no_assignment_because_before_previous_stop():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [
                FrequenceType.haute_frequence, FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:04:00+00:00")],
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 09:58:10+00:00"),
                datetime.fromisoformat("2023-01-01 09:58:49+00:00"),
                datetime.fromisoformat("2023-01-01 10:06:18+00:00")],
            MesurePonctualite.is_terminus: [False, False, False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [
                FrequenceType.haute_frequence, FrequenceType.haute_frequence, FrequenceType.haute_frequence],
            # Les valeurs d'heure theorique sont triées
            MesurePonctualite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 09:59:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:01:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:04:00+00:00")],
            # 09:58:49 est associé à 09:59 car il est compliant
            # il serait not_assigned avec 10:01 car il passe avant l'arrêt précédent
            # 10:04:10 et 10:06:18 passe tous les deux après 10:04, 10:01 n'a donc pas d'arrêt assigné
            MesurePonctualite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 09:58:10+00:00"),
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:06:18+00:00")],
            MesurePonctualite.is_terminus: [False, False, False],
            MesurePonctualite.resultat: [
                ComplianceType.compliant, ComplianceType.situation_inacceptable_absence, ComplianceType.compliant],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_early():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            MesurePonctualite.heure_reelle: [datetime.fromisoformat("2023-01-01 09:38:49+00:00")],
            MesurePonctualite.is_terminus: [False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            # 09:38:49 passe entre une heure et une minute avant 10:00, il est assigné (en SI d'avance)
            MesurePonctualite.heure_reelle: [datetime.fromisoformat("2023-01-01 09:38:49+00:00")],
            MesurePonctualite.is_terminus: [False],
            MesurePonctualite.resultat: [ComplianceType.situation_inacceptable_avance],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_one_hour_early():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            MesurePonctualite.heure_reelle: [datetime.fromisoformat("2023-01-01 08:58:49+00:00")],
            MesurePonctualite.is_terminus: [False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            # 08:58:49 passe plus d'une heure avant 10:00, il n'est pas assigné
            MesurePonctualite.heure_reelle: [pd.NaT],
            MesurePonctualite.is_terminus: [False],
            MesurePonctualite.resultat: [ComplianceType.situation_inacceptable_absence],
        }
    )
    expected_result[MesurePonctualite.heure_reelle] = expected_result[
        MesurePonctualite.heure_reelle].dt.tz_localize('UTC')

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_late():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            MesurePonctualite.heure_reelle: [datetime.fromisoformat("2023-01-01 10:38:49+00:00")],
            MesurePonctualite.is_terminus: [False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            # 10:38:49 passe entre une la borne haute SI_hf et une heure après 10:00, il est assigné (en SI de retard)
            MesurePonctualite.heure_reelle: [datetime.fromisoformat("2023-01-01 10:38:49+00:00")],
            MesurePonctualite.is_terminus: [False],
            MesurePonctualite.resultat: [ComplianceType.situation_inacceptable_retard],
        }
    )

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_process_stop_ponctualite_one_hour_late():
    df_by_stop = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            MesurePonctualite.heure_reelle: [datetime.fromisoformat("2023-01-01 11:08:49+00:00")],
            MesurePonctualite.is_terminus: [False],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesurePonctualite.frequence: [FrequenceType.haute_frequence],
            MesurePonctualite.heure_theorique: [datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
            # 11:08:49 passe plus d'une heure après 10:00, il n'est pas assigné
            MesurePonctualite.heure_reelle: [pd.NaT],
            MesurePonctualite.is_terminus: [False],
            MesurePonctualite.resultat: [ComplianceType.situation_inacceptable_absence],
        }
    )
    expected_result[MesurePonctualite.heure_reelle] = expected_result[
        MesurePonctualite.heure_reelle].dt.tz_localize('UTC')

    # When
    result = process_stop_ponctualite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)
