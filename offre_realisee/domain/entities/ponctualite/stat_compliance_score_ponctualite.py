import pandas as pd

from offre_realisee.config.offre_realisee_config import MesurePonctualite, ComplianceType

_SI_VALUES_SET = {
    ComplianceType.situation_inacceptable_avance,
    ComplianceType.situation_inacceptable_retard,
    ComplianceType.situation_inacceptable_absence
}

_ASSIGNED_VALUES_SET = {
    ComplianceType.compliant,
    ComplianceType.semi_compliant,
    ComplianceType.not_compliant,
    ComplianceType.situation_inacceptable_avance,
    ComplianceType.situation_inacceptable_retard,
}


def stat_situation_inacceptable(df: pd.DataFrame) -> pd.DataFrame:
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
        ),
        (
            MesurePonctualite.situation_inacceptable_total,
            lambda x: x.isin(_SI_VALUES_SET).sum()
        )
    ]).reset_index()

    # Conserve pour chaque ligne et sens l'arrêt avec le plus grand nombre de SI
    df_si_grouped_by_sens = df_si.groupby([MesurePonctualite.ligne, MesurePonctualite.sens])
    df_si = df_si.loc[df_si_grouped_by_sens[MesurePonctualite.situation_inacceptable_total].idxmax().values]

    df_si = df_si.drop([MesurePonctualite.arret, MesurePonctualite.sens], axis=1)

    # Somme les SI par sens
    df_si = df_si.groupby([MesurePonctualite.ligne]).agg('sum').reset_index()

    return df_si


def stat_compliance_score_ponctualite(df: pd.DataFrame) -> pd.DataFrame:
    df_si = stat_situation_inacceptable(df)

    df = df.groupby([MesurePonctualite.ligne])[MesurePonctualite.resultat].agg([
        (MesurePonctualite.nombre_theorique, 'count'),
        (MesurePonctualite.nombre_reel, lambda x: x.isin(_ASSIGNED_VALUES_SET).sum()),
        (MesurePonctualite.score_de_conformite, lambda x: x[~x.isin(_SI_VALUES_SET)].sum())
    ]).reset_index()

    df = df.merge(df_si, on=[MesurePonctualite.ligne])

    df[MesurePonctualite.taux_de_conformite] = (
            df[MesurePonctualite.score_de_conformite] / df[MesurePonctualite.nombre_theorique] * 100
    )

    df[MesurePonctualite.taux_absence_de_donnees] = (
            (df[MesurePonctualite.nombre_theorique] - df[MesurePonctualite.nombre_reel]) /
            df[MesurePonctualite.nombre_theorique] * 100
    )

    return df
