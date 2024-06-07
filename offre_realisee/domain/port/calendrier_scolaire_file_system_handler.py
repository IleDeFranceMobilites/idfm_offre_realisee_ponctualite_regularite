import abc

import pandas as pd


class CalendrierScolaireFileSystemHandler(abc.ABC):
    @abc.abstractmethod
    def save_calendrier_scolaire(self, filtered_calendrier_scolaire: pd.DataFrame) -> None:
        """Sauvegarde les données du calendrier scolaire dans le dossier input.

        Parameters
        ----------
        filtered_calendrier_scolaire :
            DataFrame du calendrier scolaire.
        """
        pass
