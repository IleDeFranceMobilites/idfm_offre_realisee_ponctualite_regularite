import pandas as pd

from offre_realisee.config.offre_realisee_config import FrequenceType, MesurePonctualite, ComplianceType, MesureType

_SI_VALUES_SET = {
    ComplianceType.situation_inacceptable_avance,
    ComplianceType.situation_inacceptable_retard,
    ComplianceType.situation_inacceptable_absence
}

_ASSIGNED_VALUES_SET = {
    ComplianceType.compliant,
    ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
    ComplianceType.semi_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
    ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.haute_frequence],
    ComplianceType.not_compliant[MesureType.ponctualite][FrequenceType.basse_frequence],
    ComplianceType.situation_inacceptable_avance,
    ComplianceType.situation_inacceptable_retard,
}


def stat_situation_inacceptable(df: pd.DataFrame) -> pd.DataFrame:
    """Génère les statistiques des Situations Inacceptables (SI) par ligne.

    Cette fonction prend un DataFrame avec des données de ponctualité et calcule les statistiques liées aux SI.
    Elle compte le nombre de SI pour différents types (avance, retard, absence) pour chaque arrêt, et garde les valeurs
    de l'arrêt ayant le plus de SI par ligne et sens pour les retards uniquement.

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
        (
            MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue,
            lambda x: x.isin({ComplianceType.situation_inacceptable_absence}).sum()
        )
    ]).reset_index()

    df_si_grouped_by_sens = df_si.groupby([MesurePonctualite.ligne, MesurePonctualite.sens])

    # Conserve le plus grand nombre de SI de retard pour chaque ligne et sens
    df_retard_max = df_si.loc[df_si_grouped_by_sens[MesurePonctualite.situation_inacceptable_retard].idxmax().values]
    df_retard_max = df_retard_max[
        [MesurePonctualite.ligne, MesurePonctualite.sens, MesurePonctualite.situation_inacceptable_retard]
    ]

    # Somme globale par ligne/sens pour les autres SI
    df_avance = df_si_grouped_by_sens[
        [MesurePonctualite.situation_inacceptable_avance,
         MesurePonctualite.situation_inacceptable_sans_horaire_reel_attribue]
    ].sum().reset_index()

    df_final = pd.merge(df_avance, df_retard_max, on=[MesurePonctualite.ligne, MesurePonctualite.sens], how='left')

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
    - Les statistiques sur les SI (SI avance, SI retard, SI absence, SI total)
    - Le pourcentage de conformité.
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
        (MesurePonctualite.score_de_conformite, lambda x: x[~x.isin(_SI_VALUES_SET)].sum())
    ]).reset_index()

    df = df.merge(df_si, on=[MesurePonctualite.ligne])

    df[MesurePonctualite.taux_de_conformite] = round(
        df[MesurePonctualite.score_de_conformite] / df[MesurePonctualite.nombre_theorique] * 100, 2
    )

    df[MesurePonctualite.taux_absence_de_donnees] = round(
        (df[MesurePonctualite.nombre_theorique] - df[MesurePonctualite.nombre_reel]) /
        df[MesurePonctualite.nombre_theorique] * 100, 2
    )

    return df
