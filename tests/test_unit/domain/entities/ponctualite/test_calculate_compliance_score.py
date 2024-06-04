from datetime import timedelta

import numpy as np
import pandas as pd

from offre_realisee.domain.entities.ponctualite.compliance_score import score
from offre_realisee.config.offre_realisee_config import FrequenceType, ComplianceType, MesureType


def test_score_bf():
    matrix_bf = np.array([[timedelta(minutes=3), timedelta(minutes=-1), timedelta(minutes=-2), timedelta(minutes=5)],
                          [timedelta(minutes=6), timedelta(minutes=7), timedelta(minutes=10), timedelta(minutes=11)]])
    is_terminus_bf = np.array([False, False])
    next_theorique_interval = [[timedelta(minutes=4)], [pd.NaT]]

    expected_result = np.array([
        [
            ComplianceType.compliant,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_absence
        ],
        [
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.basse_frequence]
        ],
    ])

    # When
    result = score(FrequenceType.basse_frequence, matrix_bf, is_terminus_bf, next_theorique_interval)

    # Then
    assert np.array_equal(result, expected_result, equal_nan=True)


def test_score_hf():
    matrix_hf = np.array([[timedelta(minutes=3), timedelta(minutes=-1), timedelta(minutes=-2), timedelta(minutes=5)],
                          [timedelta(minutes=6), timedelta(minutes=7), timedelta(minutes=10), timedelta(minutes=11)]])
    is_terminus_hf = np.array([False, False])
    next_theorique_interval = [[timedelta(minutes=4)], [pd.NaT]]

    expected_result = np.array([
        [
            ComplianceType.compliant,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_avance,
            ComplianceType.situation_inacceptable_absence
        ],
        [
            ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
            ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
        ],
    ])

    # When
    result = score(FrequenceType.haute_frequence, matrix_hf, is_terminus_hf, next_theorique_interval)

    # Then
    assert np.array_equal(result, expected_result, equal_nan=True)
