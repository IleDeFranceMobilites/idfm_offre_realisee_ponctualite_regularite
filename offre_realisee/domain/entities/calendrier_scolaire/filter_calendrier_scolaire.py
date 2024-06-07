import pandas as pd

from offre_realisee.config.calendrier_scolaire_config import (CalendrierScolaireColumns, IDF_CALENDRIER_SCOLAIRE_ZONE,
                                                              CALENDRIER_SCOLAIRE_POPULATION)


def filter_calendrier_scolaire(df_calendrier_scolaire: pd.DataFrame) -> pd.DataFrame:
    return df_calendrier_scolaire.loc[
        (df_calendrier_scolaire[CalendrierScolaireColumns.zones] == IDF_CALENDRIER_SCOLAIRE_ZONE) & (
         df_calendrier_scolaire[CalendrierScolaireColumns.population].isin(CALENDRIER_SCOLAIRE_POPULATION))
    ].drop_duplicates().sort_values(by=CalendrierScolaireColumns.start_date).drop(
        columns=CalendrierScolaireColumns.population)
