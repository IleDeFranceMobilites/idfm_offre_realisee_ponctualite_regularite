from datetime import timedelta

import numpy as np
from offre_realisee.config.offre_realisee_config import FrequenceType, ComplianceType, MesureType

_ThresholdType = dict[FrequenceType, timedelta]


class FrequencyThreshold:
    lower_si: _ThresholdType = {
        FrequenceType.basse_frequence: timedelta(minutes=-1).total_seconds(),
        FrequenceType.haute_frequence: timedelta(minutes=-1).total_seconds(),
    }
    compliance: _ThresholdType = {
        FrequenceType.basse_frequence: timedelta(minutes=5).total_seconds(),
        FrequenceType.haute_frequence: timedelta(minutes=3).total_seconds(),
    }
    semi_compliance: _ThresholdType = {
        FrequenceType.basse_frequence: timedelta(minutes=10).total_seconds(),
        FrequenceType.haute_frequence: timedelta(minutes=6).total_seconds(),
    }
    upper_si: _ThresholdType = {
        FrequenceType.basse_frequence: timedelta(minutes=15).total_seconds(),
        FrequenceType.haute_frequence: timedelta(minutes=12).total_seconds(),
    }
    late_train: _ThresholdType = {
        FrequenceType.basse_frequence: timedelta(minutes=60).total_seconds(),
        FrequenceType.haute_frequence: timedelta(minutes=60).total_seconds(),
    }
    early_train: _ThresholdType = {
        FrequenceType.basse_frequence: timedelta(minutes=-60).total_seconds(),
        FrequenceType.haute_frequence: timedelta(minutes=-60).total_seconds(),
    }


def score(freq: FrequenceType, matrix: np.ndarray, is_terminus: np.ndarray,
          next_theorique_interval: np.ndarray) -> np.ndarray:
    """Calcul des scores de conformité pour la ponctualité.

    Parameters
    ----------
    freq : FrequenceType
        La fréquence de notre ligne (HF: Haute Frequence, BF: Basse Frequence).
    matrix : ndarray
        Matrice d'entrée contenant les deltas de temps entre les valeurs réelles et théoriques.
    is_terminus : ndarray
        Tableau de booléen indiquant si un arrêt est un terminus d'arrivée ou non.
    next_theorique_interval : ndarray
        Tableau contenant les intervalles de temps avec le prochain passage théorique.

    Returns
    -------
    matrix_score : ndarray
        Matrice contenant les scores de conformité:
        - ComplianceType.compliant (1).
        - ComplianceType.semi_compliant (0.75 en haute frequence, 0.5 en basse frequence).
        - ComplianceType.not_compliant (0.25 en haute frequence, 0 en basse frequence).
        - ComplianceType.situation_inacceptable_retard (-1000000): En retard.
        - ComplianceType.situation_inacceptable_avance (-999900): En avance.
        - ComplianceType.situation_inacceptable_absence (-999000): Pas de données.
    """
    matrix_score = np.empty(matrix.shape)
    matrix_score[:] = np.nan

    # Calcul de la compliance des arrêts
    matrix_score[
        (matrix > FrequencyThreshold.lower_si[freq]) & (matrix <= FrequencyThreshold.compliance[freq])
    ] = ComplianceType.compliant
    matrix_score[
        (matrix > FrequencyThreshold.compliance[freq]) & (matrix <= FrequencyThreshold.semi_compliance[freq])
    ] = ComplianceType.semi_compliant[MesureType.ponctualite][freq]
    matrix_score[
        (matrix > FrequencyThreshold.semi_compliance[freq]) & (matrix < FrequencyThreshold.upper_si[freq])
    ] = ComplianceType.not_compliant[MesureType.ponctualite][freq]

    # Entre la borne haute de non compliance et une heure de retard: SI de retard
    matrix_score[(matrix >= FrequencyThreshold.upper_si[freq])] = ComplianceType.situation_inacceptable_retard

    # Entre la borne inférieur de non compliance et une heure d'avance: SI d'avance
    matrix_score[(matrix <= FrequencyThreshold.lower_si[freq])] = ComplianceType.situation_inacceptable_avance

    # Un passage à plus d'une heure de retard ou plus d'une heure d'avance n'est pas assigné
    matrix_score[(matrix > FrequencyThreshold.late_train[freq])] = ComplianceType.situation_inacceptable_absence
    matrix_score[(matrix < FrequencyThreshold.early_train[freq])] = ComplianceType.situation_inacceptable_absence

    # Exception - Le bus passe après l'arrêt suivant : il n'est pas assigné
    where_next_theorique_lower_than_reelle = np.where(matrix > next_theorique_interval)
    matrix_score[where_next_theorique_lower_than_reelle] = ComplianceType.situation_inacceptable_absence

    # Exception - Le bus passe avant l'arrêt précédent : il n'est pas assigné
    where_prev_theorique_greater_than_reelle = np.where(matrix < -np.roll(next_theorique_interval, 1))
    matrix_score[where_prev_theorique_greater_than_reelle] = ComplianceType.situation_inacceptable_absence

    # Exception - bus en avance au terminus : il est compliant
    where_is_terminus = np.where(is_terminus)
    matrix_score[where_is_terminus] = np.where(
        matrix[where_is_terminus] <= FrequencyThreshold.lower_si[freq],
        ComplianceType.compliant,
        matrix_score[where_is_terminus]
    )

    # Les heures réelles manquantes (pd.NaT) sont remplacées par des non assignments
    where_heure_reel_is_nan = np.where(matrix != matrix)
    matrix_score[where_heure_reel_is_nan] = ComplianceType.situation_inacceptable_absence

    return matrix_score
