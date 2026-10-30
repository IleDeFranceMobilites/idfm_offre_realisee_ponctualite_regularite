import abc
from datetime import date

import pandas as pd


class OffreRealiseeBruteFileSystemHandler(abc.ABC):
    @abc.abstractmethod
    def get_daily_offre_realisee_brute(self, date: date) -> pd.DataFrame:
        """Récupération des données brutes d'offre réalisée pour une date.

        Parameters
        ----------
        date : date
            Date pour laquelle nous voulons les données brutes d'offre réalisée.

        Returns
        -------
        df : DataFrame
            DataFrame brut d'offre réalisée.
        """
        pass

    @abc.abstractmethod
    def save_daily_offre_realisee(self, df_offre_realisee: pd.DataFrame, date: date) -> None:
        """Sauvegarde des données d'offre réalisée dans le dossier input, partitionnées par jour.

        Parameters
        ----------
        df_offre_realisee : DataFrame
            DataFrame d'offre réalisée que nous voulons sauvegarder.
        date : date
            Date du fichier brut à l'origine des données.
        """
        pass
