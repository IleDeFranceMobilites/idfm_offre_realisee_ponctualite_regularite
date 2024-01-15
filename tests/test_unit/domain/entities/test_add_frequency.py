from datetime import datetime
import numpy as np

import pandas as pd

from offre_realisee.config.offre_realisee_config import MesurePonctualite, FrequenceType
from offre_realisee.domain.entities.add_frequency import add_frequency


def test_add_frequency():
    # Given
    heure_theorique_column = pd.DataFrame({
        MesurePonctualite.heure_theorique: [datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 10, 51, 0),
                                            datetime(2023, 1, 1, 10, 5, 0), datetime(2023, 1, 1, 11, 20, 0),
                                            pd.NaT,
                                            datetime(2023, 1, 1, 10, 15, 0), datetime(2023, 1, 1, 10, 24, 0),
                                            datetime(2023, 1, 1, 10, 37, 0), datetime(2023, 1, 1, 10, 0, 0),
                                            pd.NaT, pd.NaT, pd.NaT,
                                            datetime(2023, 1, 1, 12, 10, 0), datetime(2023, 1, 1, 10, 7, 0)]})
    heure_theorique_column_2 = pd.DataFrame({
        MesurePonctualite.heure_theorique: [datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 10, 51, 0),
                                            datetime(2023, 1, 1, 10, 5, 0), datetime(2023, 1, 1, 11, 20, 0)]})

    expected_result = pd.DataFrame({
        MesurePonctualite.heure_theorique: [datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 10, 51, 0),
                                            datetime(2023, 1, 1, 10, 5, 0), datetime(2023, 1, 1, 11, 20, 0),
                                            pd.NaT,
                                            datetime(2023, 1, 1, 10, 15, 0), datetime(2023, 1, 1, 10, 24, 0),
                                            datetime(2023, 1, 1, 10, 37, 0), datetime(2023, 1, 1, 10, 0, 0),
                                            pd.NaT, pd.NaT, pd.NaT,
                                            datetime(2023, 1, 1, 12, 10, 0), datetime(2023, 1, 1, 10, 7, 0)],
        MesurePonctualite.frequence: [FrequenceType.basse_frequence, FrequenceType.basse_frequence,
                                      FrequenceType.haute_frequence, FrequenceType.basse_frequence,
                                      np.NaN,
                                      FrequenceType.basse_frequence, FrequenceType.basse_frequence,
                                      FrequenceType.basse_frequence, FrequenceType.haute_frequence,
                                      np.NaN, np.NaN, np.NaN,
                                      FrequenceType.basse_frequence, FrequenceType.basse_frequence],
        MesurePonctualite.tag_frequence: [FrequenceType.haute_frequence, FrequenceType.haute_frequence,
                                          FrequenceType.haute_frequence, FrequenceType.haute_frequence,
                                          FrequenceType.haute_frequence, FrequenceType.haute_frequence,
                                          FrequenceType.haute_frequence, FrequenceType.haute_frequence,
                                          FrequenceType.haute_frequence, FrequenceType.haute_frequence,
                                          FrequenceType.haute_frequence, FrequenceType.haute_frequence,
                                          FrequenceType.haute_frequence, FrequenceType.haute_frequence]
    }).sort_values(MesurePonctualite.heure_theorique)
    expected_result_2 = pd.DataFrame({
        MesurePonctualite.heure_theorique: [datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 10, 51, 0),
                                            datetime(2023, 1, 1, 10, 5, 0), datetime(2023, 1, 1, 11, 20, 0)],
        MesurePonctualite.frequence: [FrequenceType.basse_frequence, FrequenceType.basse_frequence,
                                      FrequenceType.basse_frequence, FrequenceType.basse_frequence],
        MesurePonctualite.tag_frequence: [FrequenceType.basse_frequence, FrequenceType.basse_frequence,
                                          FrequenceType.basse_frequence, FrequenceType.basse_frequence]
    }).sort_values(MesurePonctualite.heure_theorique)

    # When
    result = add_frequency(heure_theorique_column)
    result_2 = add_frequency(heure_theorique_column_2)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)
    pd.testing.assert_frame_equal(result_2, expected_result_2)
