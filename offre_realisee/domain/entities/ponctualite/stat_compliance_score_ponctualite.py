import pandas as pd

from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.offre_realisee_config import FrequenceType, MesurePonctualite, ComplianceType, MesureType

_SI_VALUES_SET = {
    ComplianceType.situation_inacceptable_avance,
    ComplianceType.situation_inacceptable_retard,
    ComplianceType.situation_inacceptable_absence
}

_SEMI_COMPLIANT_HF = ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.haute_frequence]
_SEMI_COMPLIANT_BF = ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence]
_NOT_COMPLIANT_HF = ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence]
_NOT_COMPLIANT_BF = ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.basse_frequence]

_ASSIGNED_VALUES_SET = {
    ComplianceType.compliant_delay,
    ComplianceType.compliant_advance,
    _SEMI_COMPLIANT_HF,
    _SEMI_COMPLIANT_BF,
    _NOT_COMPLIANT_HF,
    _NOT_COMPLIANT_BF,
    ComplianceType.situation_inacceptable_avance,
    ComplianceType.situation_inacceptable_retard,
}


def stat_situation_inacceptable(df: pd.DataFrame) -> pd.DataFrame:
    """Génère les statistiques des Situations Inacceptables (SI) par ligne.

    Cette fonction prend un DataFrame avec des données de ponctualité et calcule les statistiques liées aux SI.
    Elle compte le nombre de SI pour différents types (avance, retard) pour chaque arrêt, et garde les valeurs
    de l'arrêt ayant le plus de SI par ligne et sens pour les retards uniquement.
    Les SI d'absence (passage théorique sans horaire réel attribué) sont plafonnées à 1 par course : une course
    génère une SI dès son premier arrêt manquant.

    Parameters
    ----------
    df : DataFrame
        DataFrame contenant les données par arrêt, leur score de conformité et le nombre de SI.

    Returns
    -------
    df_si :  DataFrame
        DataFrame contenant les statistiques sur les SI pour chaque ligne.
    """
    # Compte le nombre de SI par arrêts
    df_si_grouped = df.groupby([MesurePonctualite.ligne, MesurePonctualite.sens, MesurePonctualite.arret])
    df_si = df_si_grouped[MesurePonctualite.resultat].agg([
        (
            MesurePonctualite.situation_inacceptable_avance,
            lambda x: x.isin({ComplianceType.situation_inacceptable_avance}).sum()
        ),
        (
            MesurePonctualite.situation_inacceptable_retard,
            lambda x: x.isin({ComplianceType.situation_inacceptable_retard}).sum()
        ),
    ]).reset_index()

    df_si_grouped_by_sens = df_si.groupby([MesurePonctualite.ligne, MesurePonctualite.sens])

    # SI absence plafonnée à 1 par course : une course générant au moins un passage théorique sans horaire réel
    # attribué compte pour une seule SI. Un passage sans course renseignée compte pour une SI.
    df_absence = df[df[MesurePonctualite.resultat] == ComplianceType.situation_inacceptable_absence]
    df_absence = df_absence.groupby([MesurePonctualite.ligne, MesurePonctualite.sens])[InputColumns.course_id].agg(
        lambda x: x.nunique() + x.isna().sum()
    ).rename(MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue).reset_index()

    # Conserve le plus grand nombre de SI de retard pour chaque ligne et sens
    df_retard_max = df_si.loc[df_si_grouped_by_sens[MesurePonctualite.situation_inacceptable_retard].idxmax().values]
    df_retard_max = df_retard_max[
        [MesurePonctualite.ligne, MesurePonctualite.sens, MesurePonctualite.situation_inacceptable_retard]
    ]

    # Somme globale par ligne/sens pour les autres SI
    df_avance = df_si_grouped_by_sens[[MesurePonctualite.situation_inacceptable_avance]].sum().reset_index()

    df_final = pd.merge(df_avance, df_retard_max, on=[MesurePonctualite.ligne, MesurePonctualite.sens], how='left')
    df_final = pd.merge(df_final, df_absence, on=[MesurePonctualite.ligne, MesurePonctualite.sens], how='left')
    df_final[MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue] = (
        df_final[MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue].fillna(0).astype(int)
    )

    # Somme les SI
    df_final[MesurePonctualite.situation_inacceptable_total] = (
            df_final[MesurePonctualite.situation_inacceptable_avance] +
            df_final[MesurePonctualite.situation_inacceptable_retard] +
            df_final[MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue]
    )

    df_final = df_final.drop(columns=[MesurePonctualite.sens])
    df_final = df_final[MesurePonctualite.si_column_order]
    return df_final.groupby(MesurePonctualite.ligne).sum(numeric_only=True).reset_index()


def stat_compliance_score_ponctualite(df: pd.DataFrame, metadata_cols: list[str] = []) -> pd.DataFrame:
    """Génère les statistiques de conformité pour les données de ponctualité.

    Cette fonction prend un DataFrame avec les scores de conformité et calcule les statistiques liées à ces données.
    Elle renvoie un DataFrame contenant :
    - Le nombre de passage théoriques.
    - Le nombre de passages réelles assignées à une valeur théorique.
    - La somme des scores de conformité.
    - Les statistiques sur la conformité (semi-conforme, non-conforme, avance conforme et retard conforme), ainsi que
      le détail des paliers de retard selon la fréquence de la ligne (retard 75% et 25% en haute fréquence,
      retard 50% et non conforme en basse fréquence).
    - Les statistiques sur les SI (SI avance, SI retard, SI absence, SI total)
    - Le pourcentage de conformité.
    - Le pourcentage de données remontée
    - Le pourcentage de données manquantes.

    Parameters
    ----------
    df : DataFrame
        DataFrame contenant les données par arrêt, leur score de conformité et le nombre de SI.
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].

    Returns
    -------
    df : DataFrame
        DataFrame contenant les statistiques de conformité pour chaque ligne.
    """
    df_si = stat_situation_inacceptable(df)

    df = df.groupby([MesurePonctualite.ligne] + metadata_cols)[MesurePonctualite.resultat].agg([
        (MesurePonctualite.nombre_theorique, 'count'),
        (MesurePonctualite.nombre_reel, lambda x: x.isin(_ASSIGNED_VALUES_SET).sum()),
        (MesurePonctualite.score_de_conformite, lambda x: x[~x.isin(_SI_VALUES_SET)].sum()),
        (MesurePonctualite.avance_conforme, lambda x: x.isin([ComplianceType.compliant_advance]).sum()),
        (MesurePonctualite.retard_conforme, lambda x: x.isin([ComplianceType.compliant_delay]).sum()),
        (MesurePonctualite.retard_75_conforme, lambda x: x.isin([_SEMI_COMPLIANT_HF]).sum()),
        (MesurePonctualite.retard_50_conforme, lambda x: x.isin([_SEMI_COMPLIANT_BF]).sum()),
        (MesurePonctualite.retard_25_conforme, lambda x: x.isin([_NOT_COMPLIANT_HF]).sum()),
        (MesurePonctualite.retard_non_conforme, lambda x: x.isin([_NOT_COMPLIANT_BF]).sum())
    ]).reset_index()

    # Les paliers de retard se cumulent en semi-conforme et non-conforme
    df[MesurePonctualite.semi_conforme] = (
        df[MesurePonctualite.retard_75_conforme] + df[MesurePonctualite.retard_50_conforme]
    )
    df[MesurePonctualite.non_conforme] = (
        df[MesurePonctualite.retard_25_conforme] + df[MesurePonctualite.retard_non_conforme]
    )

    df = df.merge(df_si, on=[MesurePonctualite.ligne])

    df[MesurePonctualite.taux_de_conformite] = round(
        df[MesurePonctualite.score_de_conformite] / df[MesurePonctualite.nombre_theorique] * 100, 2
    )

    df[MesurePonctualite.taux_de_situation_innaceptable] = round(
        df[MesurePonctualite.situation_inacceptable_total] / df[MesurePonctualite.nombre_theorique] * 100, 2
    )

    df[MesurePonctualite.taux_absence_de_donnees] = round(
        (df[MesurePonctualite.nombre_theorique] - df[MesurePonctualite.nombre_reel]) /
        df[MesurePonctualite.nombre_theorique] * 100, 2
    )

    df[MesurePonctualite.taux_de_remontee_sae] = round(
        df[MesurePonctualite.nombre_reel] / df[MesurePonctualite.nombre_theorique] * 100, 2
    )

    return df
