import pandas as pd

from offre_realisee.config.calendrier_scolaire_config import CalendrierScolaireColumns
from offre_realisee.domain.port.calendrier_scolaire_source_handler import CalendrierScolaireSourceHandler

API_SEP = ";"

API_ROUTE = ("https://data.education.gouv.fr/api/explore/v2.0/catalog/datasets/fr-en-calendrier-scolaire/exports/csv?"
             "delimiter=%3B&list_separator=%2C&quote_all=false&with_bom=false")


class CalendrierScolaireApiHandler(CalendrierScolaireSourceHandler):
    def get_calendrier_scolaire(self) -> pd.DataFrame:
        """Téléchargement des données de calendrier scolaire.

        Returns
        -------
        df : DataFrame
            DataFrame du calendrier scolaire.
        """
        return pd.read_csv(API_ROUTE, sep=API_SEP,
                           usecols=[CalendrierScolaireColumns.zones, CalendrierScolaireColumns.start_date,
                                    CalendrierScolaireColumns.end_date, CalendrierScolaireColumns.population,
                                    CalendrierScolaireColumns.description])
