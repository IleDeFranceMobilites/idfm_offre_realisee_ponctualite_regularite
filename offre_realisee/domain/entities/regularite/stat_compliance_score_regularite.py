import pandas as pd
from offre_realisee.config.offre_realisee_config import MesureRegularite, ComplianceType

_SI_VALUES_SET = {
    ComplianceType.situation_inacceptable_train_de_bus,
    ComplianceType.situation_inacceptable_faible_frequence,
}


def stat_compliance_score_regularite(
    df: pd.DataFrame,
    n_theorique_by_lignes: dict[str, int], any_high_frequency_on_lignes: dict[str, bool], metadata_cols: list[str] = []
) -> pd.DataFrame:
    """Calcule le taux de conformité pour la régularité pour les lignes hautes fréquences (= les lignes qui contiennent
    au moins un arrêt haute fréquence sur la période analysée).
    La formule de calcul du taux de conformité est :
    [somme des score de conformité] / [nombre de passages théoriques] * 100.
    Le nombre de situations inacceptables par typologie et total sont sommées par ligne.
    Le taux d'absence des données est également calculé :
    [nombre de passages théoriques - nombre de passages réels] / [nombre de passages théoriques] * 100

    Parameters
    ----------
    df : DataFrame
        DataFrame qui contient les scores de conformité pour la régularité pour tous les arrêts par ligne
    n_theorique_by_lignes : dict
        Dictionnaire qui contient les lignes en clé et le nombre de passages théoriques en valeur
    any_high_frequency_on_lignes : dict
        Dictionnaire qui contient les lignes en clé et True en valeur si la ligne contient au moins un arrêt haute
        fréquence sur la période analysée, False sinon
    metadata_cols: list[str]
        Colonnes contenant des méta informations invariables par lignes qui doivent être conservées, par défaut à [].

    Returns
    ----------
    df : DataFrame
        DataFrame qui contient le nombre de passages théoriques, réels, le nombre de situations inacceptables par
        typologie et total, le taux de conformité pour la régularité, le taux d'absence des données (réelles)
    """

    # Filter lignes with at least one high frequency measure
    df = df[df[MesureRegularite.ligne].apply(lambda x: any_high_frequency_on_lignes[x])]

    # Aggregate stops results by lignes
    df = df.groupby([MesureRegularite.ligne] + metadata_cols)[MesureRegularite.resultat].agg([
        (MesureRegularite.nombre_reel, 'count'),
        (MesureRegularite.score_de_conformite, lambda x: x[~x.isin(_SI_VALUES_SET)].sum()),
        (
            MesureRegularite.situation_inacceptable_train_de_bus,
            lambda x: x.isin({ComplianceType.situation_inacceptable_train_de_bus}).sum()
        ),
        (
            MesureRegularite.situation_inacceptable_ecart_important,
            lambda x: x.isin({ComplianceType.situation_inacceptable_faible_frequence}).sum()
        ),
        (MesureRegularite.situation_inacceptable_total, lambda x: x.isin(_SI_VALUES_SET).sum()),
    ]).reset_index()

    df[MesureRegularite.nombre_theorique] = df[MesureRegularite.ligne].apply(lambda x: int(n_theorique_by_lignes[x]))

    df[MesureRegularite.taux_de_conformite] = round(
            df[MesureRegularite.score_de_conformite] / df[MesureRegularite.nombre_theorique] * 100, 2
    )

    df[MesureRegularite.taux_absence_de_donnees] = round(
            (df[MesureRegularite.nombre_theorique] - df[MesureRegularite.nombre_reel]) /
            df[MesureRegularite.nombre_theorique] * 100, 2
    )

    return df
