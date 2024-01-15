from typing import Dict
import pandas as pd
from offre_realisee.config.offre_realisee_config import MesureRegularite, ComplianceType

_SI_VALUES_SET = {
    ComplianceType.situation_inacceptable_train_de_bus,
    ComplianceType.situation_inacceptable_faible_frequence,
}


def stat_compliance_score_regularite(df: pd.DataFrame, n_theorique_by_lignes: Dict[str, int],
                                     any_high_frequency_on_lignes: Dict[str, bool]) -> pd.DataFrame:

    # Filter lignes with at least one high frequency measure
    df = df[df[MesureRegularite.ligne].apply(lambda x: any_high_frequency_on_lignes[x])]

    # Aggregate stops results by lignes
    df = df.groupby([MesureRegularite.ligne])[MesureRegularite.resultat].agg([
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

    df[MesureRegularite.taux_de_conformite] = (
            df[MesureRegularite.score_de_conformite] / df[MesureRegularite.nombre_theorique] * 100
    )

    df[MesureRegularite.taux_absence_de_donnees] = (
            (df[MesureRegularite.nombre_theorique] - df[MesureRegularite.nombre_reel]) /
            df[MesureRegularite.nombre_theorique] * 100
    )

    return df
