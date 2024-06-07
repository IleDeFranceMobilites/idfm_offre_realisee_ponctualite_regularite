import pandas as pd

from offre_realisee.config.calendrier_scolaire_config import CalendrierScolaireColumns
from offre_realisee.domain.entities.calendrier_scolaire.filter_calendrier_scolaire import filter_calendrier_scolaire


def test_filter_calendrier_scolaire():
    # Given
    df = pd.DataFrame({CalendrierScolaireColumns.description: ['Vacances de Printemps',
                                                               "Vacances d'Été",
                                                               'Vacances de la Toussaint',
                                                               'Vacances de Printemps',
                                                               "Vacances d'Été"],
                       CalendrierScolaireColumns.population: ['-', '-', 'Enseignants', '-', 'Élèves'],
                       CalendrierScolaireColumns.start_date: ['2010-04-25T22:00:00+00:00',
                                                              '2010-07-07T22:00:00+00:00',
                                                              '2010-10-24T22:00:00+00:00',
                                                              '2012-04-22T22:00:00+00:00',
                                                              '2012-07-08T22:00:00+00:00'],
                       CalendrierScolaireColumns.end_date: ['2010-05-09T22:00:00+00:00',
                                                            '2010-09-07T22:00:00+00:00',
                                                            '2010-11-01T23:00:00+00:00',
                                                            '2012-05-06T22:00:00+00:00',
                                                            '2012-09-09T22:00:00+00:00'],
                       CalendrierScolaireColumns.zones: ['Zone C', 'Corse', 'Zone C', 'Zone C', 'Zone C'],
                       })
    expected_df = df.iloc[[0, 3, 4]].drop(columns=[CalendrierScolaireColumns.population])

    # When
    result_df = filter_calendrier_scolaire(df)

    # Then
    pd.testing.assert_frame_equal(result_df, expected_df)
