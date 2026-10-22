import pandas as pd

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import MesurePonctualite


def compute_non_passage_arret(df_offre_realisee: pd.DataFrame) -> pd.DataFrame:
    """Calcule le nombre de passages prévus mais non réalisés par ligne.

    Pour chaque arrêt (ligne/sens/arrêt), le nombre de non passages est :
    max(0, [nombre de passages théoriques] - [nombre de passages réels]).
    Les nombres de passages sont des comptes bruts des heures théoriques et réelles renseignées, sans tenir compte de
    l'association théorique/réelle. Les résultats sont ensuite sommés par ligne.

    Parameters
    ----------
    df_offre_realisee : DataFrame
        DataFrame contenant les données d'offre réalisée.

    Returns
    -------
    df : DataFrame
        DataFrame contenant le nombre de non passages aux arrêts pour chaque ligne.
    """
    df_by_stop = df_offre_realisee.groupby(
        [InputColumns.ligne, InputColumns.sens, InputColumns.arret]
    )[[InputColumns.heure_theorique, InputColumns.heure_reelle]].count()

    df_by_stop[MesurePonctualite.non_passage_arret] = (
        df_by_stop[InputColumns.heure_theorique] - df_by_stop[InputColumns.heure_reelle]
    ).clip(lower=0)

    return df_by_stop.groupby(InputColumns.ligne)[MesurePonctualite.non_passage_arret].sum().reset_index()
