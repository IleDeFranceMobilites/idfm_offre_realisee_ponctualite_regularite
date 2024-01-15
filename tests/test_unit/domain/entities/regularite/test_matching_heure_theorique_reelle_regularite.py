from datetime import datetime, timedelta

import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite
from offre_realisee.domain.entities.regularite.matching_heure_theorique_reelle_regularite import \
    matching_heure_theorique_reelle_regularite


def test_matching_heure_theorique_reelle():
    df_by_stop = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 09:55:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:58:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:20:00+00:00"),
                datetime.fromisoformat("2023-01-01 14:30:00+00:00"),
                pd.NaT],
            MesureRegularite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:02:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:22:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:29:00+00:00"),
                datetime.fromisoformat("2023-01-01 12:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 12:30:00+00:00"),
                datetime.fromisoformat("2023-01-01 13:00:00+00:00")]
        }
    )

    expected_result = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 09:55:00+00:00"),
                datetime.fromisoformat("2023-01-01 09:58:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:10:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:20:00+00:00"),
                datetime.fromisoformat("2023-01-01 14:30:00+00:00")],
            MesureRegularite.difference_reelle: [
                pd.NaT,
                timedelta(minutes=3),
                timedelta(minutes=2),
                timedelta(minutes=5),
                timedelta(minutes=5),
                timedelta(minutes=5),
                timedelta(minutes=5),
                timedelta(hours=4, minutes=10)],
            MesureRegularite.heure_theorique_inf: [
                pd.NaT,
                pd.NaT,
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:02:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00"),
                datetime.fromisoformat("2023-01-01 13:00:00+00:00")],
            MesureRegularite.difference_theorique_inf: [
                pd.NaT,
                pd.NaT,
                pd.NaT,
                timedelta(minutes=2),
                timedelta(minutes=4),
                timedelta(minutes=6),
                timedelta(minutes=6),
                timedelta(minutes=30)],
            MesureRegularite.heure_theorique_sup: [
                pd.NaT,
                datetime.fromisoformat("2023-01-01 10:02:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:02:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:22:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:22:00+00:00"),
                pd.NaT],
            MesureRegularite.difference_theorique_sup: [
                pd.NaT,
                timedelta(minutes=2),
                timedelta(minutes=2),
                timedelta(minutes=4),
                timedelta(minutes=6),
                timedelta(minutes=10),
                timedelta(minutes=10),
                pd.NaT]
        }
    )

    # When
    result = matching_heure_theorique_reelle_regularite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_matching_heure_theorique_reelle_reorder():
    df_by_stop = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00")],
            MesureRegularite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 10:02:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:00:00+00:00")],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
            ],
            MesureRegularite.difference_reelle: [pd.Timedelta("NaT"), timedelta(minutes=5)],
            MesureRegularite.heure_theorique_inf: [pd.NaT, datetime.fromisoformat("2023-01-01 10:02:00+00:00")],
            MesureRegularite.difference_theorique_inf: pd.to_timedelta(
                [pd.Timedelta("NaT"), timedelta(minutes=2)]
            ),
            MesureRegularite.heure_theorique_sup: pd.to_datetime(
                [pd.NaT, pd.NaT], utc=True
            ),
            MesureRegularite.difference_theorique_sup: pd.to_timedelta(
                [pd.Timedelta("NaT"), pd.Timedelta("NaT")]
            )
        }
    )

    # When
    result = matching_heure_theorique_reelle_regularite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_matching_heure_theorique_reelle_first_two_reel_before_theorique():
    df_by_stop = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:15:00+00:00")],
            MesureRegularite.heure_theorique: [
                datetime.fromisoformat("2023-01-01 10:06:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:09:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:12:00+00:00")],
        }
    )

    expected_result = pd.DataFrame(
        {
            MesureRegularite.heure_reelle: [
                datetime.fromisoformat("2023-01-01 10:00:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:05:00+00:00"),
                datetime.fromisoformat("2023-01-01 10:15:00+00:00"),
            ],
            MesureRegularite.difference_reelle: [
                pd.Timedelta("NaT"), timedelta(minutes=5), timedelta(minutes=10)],
            MesureRegularite.heure_theorique_inf: [
                pd.NaT, pd.NaT, datetime.fromisoformat("2023-01-01 10:12:00+00:00")],
            MesureRegularite.difference_theorique_inf: [
                pd.Timedelta("NaT"), pd.Timedelta("NaT"), timedelta(minutes=3)],
            MesureRegularite.heure_theorique_sup: [
                pd.NaT, datetime.fromisoformat("2023-01-01 10:09:00+00:00"), pd.NaT],
            MesureRegularite.difference_theorique_sup: [
                pd.Timedelta("NaT"), timedelta(minutes=3), pd.Timedelta("NaT")]
        }
    )

    # When
    result = matching_heure_theorique_reelle_regularite(df_by_stop)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)
