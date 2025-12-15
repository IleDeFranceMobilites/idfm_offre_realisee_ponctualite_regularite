from datetime import timedelta

import numpy as np

from offre_realisee.domain.entities.ponctualite.compliance_score import score
from offre_realisee.config.offre_realisee_config import FrequenceType, ComplianceType, MesureType


def test_score_bf():
    matrix_bf = np.array(
        [[timedelta(minutes=3).total_seconds(), timedelta(minutes=-1).total_seconds(),
          timedelta(minutes=-2).total_seconds(), timedelta(minutes=5).total_seconds(),
          timedelta(seconds=-30).total_seconds()],
         [timedelta(minutes=6).total_seconds(), timedelta(minutes=7).total_seconds(),
          timedelta(minutes=10).total_seconds(), timedelta(minutes=11).total_seconds(),
          timedelta(seconds=-30).total_seconds()]])
    is_terminus_bf = np.array([False, False])
    next_theorique_interval = [[timedelta(minutes=4).total_seconds()], [np.nan]]

    expected_result = np.array([
        [
            ComplianceType.compliant_delay,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_absence,
            ComplianceType.compliant_advance
        ],
        [
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.compliant_advance
        ],
    ])

    # When
    result = score(FrequenceType.basse_frequence, matrix_bf, is_terminus_bf, next_theorique_interval)

    # Then
    assert np.array_equal(result, expected_result, equal_nan=True)


def test_score_hf():
    matrix_hf = np.array(
        [[timedelta(minutes=3).total_seconds(), timedelta(minutes=-1).total_seconds(),
          timedelta(minutes=-2).total_seconds(), timedelta(minutes=5).total_seconds(),
          timedelta(seconds=-30).total_seconds()],
         [timedelta(minutes=6).total_seconds(), timedelta(minutes=7).total_seconds(),
          timedelta(minutes=10).total_seconds(), timedelta(minutes=11).total_seconds(),
          timedelta(seconds=-30).total_seconds()]])
    is_terminus_hf = np.array([False, False])
    next_theorique_interval = [[timedelta(minutes=4).total_seconds()], [np.nan]]

    expected_result = np.array([
        [
            ComplianceType.compliant_delay,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_absence,
            ComplianceType.compliant_advance
        ],
        [
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.compliant_advance
        ],
    ])

    # When
    result = score(FrequenceType.haute_frequence, matrix_hf, is_terminus_hf, next_theorique_interval)

    # Then
    assert np.array_equal(result, expected_result, equal_nan=True)
