import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from offre_realisee.config.offre_realisee_config import MesurePonctualite, FrequenceType, ComplianceType
from offre_realisee.domain.entities.ponctualite.compliance_score import score
from numpy import set_printoptions

set_printoptions(suppress=True)


def process_stop_ponctualite(df_by_stop: pd.DataFrame) -> pd.DataFrame:
    """Traitement des données par arrêt et ajout des scores de conformité.

    Cette fonction prend un DataFrame avec des données de ponctualité par arrêt et optimise les attributions de temps
    réelle/théorique pour minimiser les pénalités. Elle retourne un DataFrame incluant les scores de conformité, le
    lien théorique réelle et gère les passages aberrants en les marquant comme non attribués.

    Parameters
    ----------
    df_by_stop : DataFrame
        DataFrame contenant les données par arrêt.

    Returns
    -------
    df_by_stop :  DataFrame
        DataFrame contenant l'assignement optimal des valeurs théoriques/réelles ainsi que le score de conformité
        associé.
    """
    # On extrait la colonne d'heures réelles, en conservant les valeurs NaN pour pouvoir les associer de manière
    # optimale aux heures théoriques dans la matrice de coût.

    heure_reelle_col_copy = df_by_stop[MesurePonctualite.heure_reelle].to_numpy()

    df_by_stop = (
        df_by_stop.dropna(subset=[MesurePonctualite.heure_theorique])
        .sort_values(by=[MesurePonctualite.heure_theorique]).reset_index(drop=True)
    )
    df_by_stop[MesurePonctualite.difference_theorique] = (
        df_by_stop[MesurePonctualite.heure_theorique].diff(1).shift(-1).astype('object'))

    # Calcul de la pénalité associée à chaque paires théorique/réelle possible
    cost_matrix = compute_cost_matrix(df_by_stop, heure_reelle_col_copy)

    # Calcul de la meilleur combinaison possible minimisant les pénalités reçues
    reelle_indices, theorique_indices = linear_sum_assignment(cost_matrix, maximize=True)

    # Associe les scores de compliance
    df_by_stop.loc[theorique_indices, MesurePonctualite.resultat] = cost_matrix[reelle_indices, theorique_indices]

    # Associe toutes les heures réelles aux meilleurs heures théoriques possible
    df_by_stop.loc[theorique_indices, MesurePonctualite.heure_reelle] = heure_reelle_col_copy[reelle_indices]

    # Remplace les passages aberrants par des passages non assignés
    df_by_stop.loc[
        df_by_stop[MesurePonctualite.resultat] == ComplianceType.situation_inacceptable_absence,
        MesurePonctualite.heure_reelle
    ] = pd.NaT
    df_by_stop = df_by_stop.fillna({
        MesurePonctualite.heure_theorique: pd.NaT,
        MesurePonctualite.heure_reelle: pd.NaT,
    })

    return df_by_stop.drop([MesurePonctualite.difference_theorique], axis=1)


def compute_cost_matrix(df_by_stop: pd.DataFrame, heure_reelle_col: np.ndarray) -> np.ndarray:
    """Traite les données de ponctualité par arrêts et génère le scores de conformité.

    Parameters
    ----------
    df_by_stop : DataFrame
        DataFrame contenant les données de ponctualité par arrêt.
    heure_reelle_col : ndarray
        Le type de franquence de la ligne (HF: Haute Fréquence, BF: Basse Fréquence).

    Returns
    -------
    matrix : ndarray
        Matrice contenant les scores de conformité:
        - ComplianceType.compliant (1).
        - ComplianceType.semi_compliant (0.5).
        - ComplianceType.not_compliant (0).
        - ComplianceType.situation_inacceptable_retard (-1000000): En retard.
        - ComplianceType.situation_inacceptable_avance (-999900): En avance.
        - ComplianceType.situation_inacceptable_absence (-999000): Pas de données.
    """
    matrix_timedelta = np.subtract.outer(
        heure_reelle_col,
        df_by_stop[MesurePonctualite.heure_theorique].to_numpy()
    ).T

    next_theorique_interval = df_by_stop[MesurePonctualite.difference_theorique].to_numpy()
    is_terminus = df_by_stop[MesurePonctualite.is_terminus].to_numpy()

    matrix = np.full(matrix_timedelta.shape, np.NaN)

    mask_hf = df_by_stop[MesurePonctualite.frequence] == FrequenceType.haute_frequence
    matrix[mask_hf] = score(
        freq=FrequenceType.haute_frequence,
        matrix=matrix_timedelta[mask_hf],
        is_terminus=is_terminus[mask_hf],
        next_theorique_interval=next_theorique_interval[mask_hf, None]
    )

    mask_bf = ~mask_hf
    matrix[mask_bf] = score(
        freq=FrequenceType.basse_frequence,
        matrix=matrix_timedelta[mask_bf],
        is_terminus=is_terminus[mask_bf],
        next_theorique_interval=next_theorique_interval[mask_bf, None]
    )

    return matrix.T
