from abc import ABC, abstractmethod

import pandas as pd


class CalendrierScolaireSourceHandler(ABC):
    @abstractmethod
    def get_calendrier_scolaire(self) -> pd.DataFrame:
        pass
