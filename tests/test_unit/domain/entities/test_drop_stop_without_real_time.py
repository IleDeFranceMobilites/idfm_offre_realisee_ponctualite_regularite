from datetime import datetime

import pandas as pd

from offre_realisee.config.offre_realisee_config import MesurePonctualite
from offre_realisee.domain.entities.drop_stop_without_real_time import drop_stop_without_real_time


def test_drop_stop_without_real_time():
    # Given
    df = pd.DataFrame({
        MesurePonctualite.arret: [1, 1, 2, 2, 3, 3],
        MesurePonctualite.heure_reelle: [
            datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 9, 10, 0), datetime(2023, 1, 1, 9, 15, 0),
            pd.NaT, pd.NaT, pd.NaT
        ]
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.arret: [1, 1, 2, 2],
        MesurePonctualite.heure_reelle: [
            datetime(2023, 1, 1, 9, 0, 0), datetime(2023, 1, 1, 9, 10, 0), datetime(2023, 1, 1, 9, 15, 0), pd.NaT
        ]
    })

    # When
    result = drop_stop_without_real_time(df)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)
