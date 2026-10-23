import pandas as pd

from offre_realisee.config.offre_realisee_config import MesurePonctualite, MesureRegularite
from offre_realisee.domain.usecases.aggregate_mesure_qs import aggregate_df


def test_aggregate_df_ponctualite_sums_conformite_counters():
    # Given - deux journées pour la même ligne
    df_all_mesure = pd.DataFrame({
        MesurePonctualite.ligne: [150, 150],
        MesurePonctualite.nb_courses_theoriques: [10, 12],
        MesurePonctualite.nombre_theorique: [100, 100],
        MesurePonctualite.nombre_reel: [90, 100],
        MesurePonctualite.score_de_conformite: [80.0, 95.0],
        MesurePonctualite.avance_conforme: [10, 5],
        MesurePonctualite.retard_conforme: [60, 80],
        MesurePonctualite.retard_75_conforme: [4, 6],
        MesurePonctualite.retard_50_conforme: [6, 4],
        MesurePonctualite.semi_conforme: [10, 10],
        MesurePonctualite.retard_25_conforme: [5, 3],
        MesurePonctualite.retard_non_conforme: [5, 2],
        MesurePonctualite.non_conforme: [10, 5],
        MesurePonctualite.situation_inacceptable_retard: [1, 0],
        MesurePonctualite.situation_inacceptable_avance: [2, 0],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [10, 0],
        MesurePonctualite.situation_inacceptable_total: [13, 0],
    })

    expected_result = pd.DataFrame({
        MesurePonctualite.ligne: [150],
        MesurePonctualite.nb_courses_theoriques: [22],
        MesurePonctualite.nombre_theorique: [200],
        MesurePonctualite.nombre_reel: [190],
        MesurePonctualite.score_de_conformite: [175.0],
        MesurePonctualite.avance_conforme: [15],
        MesurePonctualite.retard_conforme: [140],
        MesurePonctualite.retard_75_conforme: [10],
        MesurePonctualite.retard_50_conforme: [10],
        MesurePonctualite.semi_conforme: [20],
        MesurePonctualite.retard_25_conforme: [8],
        MesurePonctualite.retard_non_conforme: [7],
        MesurePonctualite.non_conforme: [15],
        MesurePonctualite.situation_inacceptable_retard: [1],
        MesurePonctualite.situation_inacceptable_avance: [2],
        MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue: [10],
        MesurePonctualite.situation_inacceptable_total: [13],
        MesurePonctualite.taux_de_conformite: [87.5],
        MesurePonctualite.taux_absence_de_donnees: [5.0],
    })

    # When
    result = aggregate_df(df_all_mesure, MesurePonctualite)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)


def test_aggregate_df_regularite_sums_conformite_counters():
    # Given
    df_all_mesure = pd.DataFrame({
        MesureRegularite.ligne: [150, 150],
        MesureRegularite.nb_courses_theoriques: [10, 12],
        MesureRegularite.nombre_theorique: [100, 100],
        MesureRegularite.nombre_reel: [90, 100],
        MesureRegularite.score_de_conformite: [80.0, 95.0],
        MesureRegularite.semi_conforme: [10, 4],
        MesureRegularite.non_conforme: [5, 1],
        MesureRegularite.situation_inacceptable_train_de_bus: [2, 0],
        MesureRegularite.situation_inacceptable_ecart_important: [3, 0],
        MesureRegularite.situation_inacceptable_total: [5, 0],
    })

    expected_result = pd.DataFrame({
        MesureRegularite.ligne: [150],
        MesureRegularite.nb_courses_theoriques: [22],
        MesureRegularite.nombre_theorique: [200],
        MesureRegularite.nombre_reel: [190],
        MesureRegularite.score_de_conformite: [175.0],
        MesureRegularite.semi_conforme: [14],
        MesureRegularite.non_conforme: [6],
        MesureRegularite.situation_inacceptable_train_de_bus: [2],
        MesureRegularite.situation_inacceptable_ecart_important: [3],
        MesureRegularite.situation_inacceptable_total: [5],
        MesureRegularite.taux_de_conformite: [87.5],
        MesureRegularite.taux_absence_de_donnees: [5.0],
    })

    # When
    result = aggregate_df(df_all_mesure, MesureRegularite)

    # Then
    pd.testing.assert_frame_equal(result, expected_result)
