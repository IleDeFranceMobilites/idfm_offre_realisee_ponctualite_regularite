from datetime import timedelta
import numpy as np
import pandas as pd

from offre_realisee.config.offre_realisee_config import Borne, MesureRegularite, ComplianceType, MesureType


def calculate_compliance_score_for_each_borne(df_with_interval: pd.DataFrame) -> pd.DataFrame:
    """Calcule un score de conformité pour la régularité pour une heure de passage réel selon les 2 passages théoriques
    les plus proches qui lui sont attribués (= borne inférieure et borne supérieure).

    Les scores de conformité (régularité) pour chaque borne sont calculés ainsi :
        - ComplianceType.compliant (1).
        - ComplianceType.semi_compliant (0.65).
        - ComplianceType.situation_inacceptable_faible_frequence (-2): Intervalle entre 2 passages trop important.
        - ComplianceType.situation_inacceptable_train_de_bus (-1): Train de bus.

    Parameters
    ----------
    df_with_interval : DataFrame
        DataFrame qui contient, pour un arrêt, tous les intervalles (différence entre le passage p et le passage
        précédent p-1) de passages réels (=différence réelle) et théoriques (=différence théorique)

    Returns
    ----------
    df_with_score : DataFrame
        DataFrame qui contient les scores de conformité calculés en fonction de la différence réelle et théorique (cf.
        tableau des scores de conformité pour la régularité de la notice)
    """
    timedelta_train_de_bus = timedelta(seconds=90)
    timedelta_borne_haute_compliant = timedelta(minutes=2)

    for borne in [Borne.inf, Borne.sup]:
        diff_reelle = df_with_interval[MesureRegularite.difference_reelle]
        diff_theorique_borne = df_with_interval[MesureRegularite.difference_theorique + borne]

        conditions = [
            diff_reelle < timedelta_train_de_bus,
            diff_reelle <= (diff_theorique_borne + timedelta_borne_haute_compliant),
            diff_reelle <= diff_theorique_borne * 2,
            diff_reelle > diff_theorique_borne * 2
        ]
        choices = [
            ComplianceType.situation_inacceptable_train_de_bus,
            ComplianceType.compliant,
            ComplianceType.semi_compliant[MesureType.regularite],
            ComplianceType.situation_inacceptable_faible_frequence,
        ]
        df_with_interval[MesureRegularite.resultat + borne] = np.select(
            conditions, choices, default=np.nan
        )

    return df_with_interval


def select_closest_defined_time_result(df_score: pd.DataFrame) -> pd.DataFrame:
    """Sélectionne le score de conformité pour la régularité du plus petit intervalle de temps (inférieur et supérieur)
    afin d'optimiser ce score.

    Parameters
    ----------
    df_score : DataFrame
        DataFrame qui contient pour l'instant des valeurs nulles dans la colonne "Résultats"

    Returns
    ----------
    df_score : DataFrame
        DataFrame qui contient les scores de conformité dans les cas où les intervalles inférieurs et supérieurs sont
        différents pour un même passage
    """
    diff_with_inf = df_score[MesureRegularite.heure_reelle] - df_score[MesureRegularite.heure_theorique_inf]
    diff_with_sup = df_score[MesureRegularite.heure_theorique_sup] - df_score[MesureRegularite.heure_reelle]
    borne_inf_is_closer = diff_with_inf < diff_with_sup
    borne_sup_is_closer = diff_with_inf > diff_with_sup

    borne_inf_is_defined = df_score[MesureRegularite.heure_theorique_inf].notna()
    borne_sup_is_defined = df_score[MesureRegularite.heure_theorique_sup].notna()
    borne_inf_is_not_defined = ~borne_inf_is_defined
    borne_sup_is_not_defined = ~borne_sup_is_defined

    choose_borne_inf = borne_inf_is_closer | (borne_inf_is_defined & borne_sup_is_not_defined)
    choose_borne_sup = borne_sup_is_closer | (borne_sup_is_defined & borne_inf_is_not_defined)

    df_score.loc[choose_borne_inf, MesureRegularite.resultat] = df_score[MesureRegularite.resultat_inf]
    df_score.loc[choose_borne_sup, MesureRegularite.resultat] = df_score[MesureRegularite.resultat_sup]

    return df_score


def select_best_score_if_equals(df_score: pd.DataFrame) -> pd.DataFrame:
    """Sélectionne le meilleur score de conformité pour la régularité dans le cas où les 2 intervalles (inférieur et
    supérieur) sont équidistants à l'heure réelle.

    Parameters
    ----------
    df_score : DataFrame
        DataFrame qui contient les premiers scores de conformité

    Returns
    ----------
    df_score : DataFrame
        DataFrame qui contient les scores de conformité déjà présents ainsi que les scores de conformités pour les
        passages dont les 2 intervalles sont égaux
    """
    df_result_is_not_set = df_score[MesureRegularite.resultat].isna()
    df_score.loc[df_result_is_not_set, MesureRegularite.resultat] = np.maximum(
        df_score.loc[df_result_is_not_set, MesureRegularite.resultat_inf],
        df_score.loc[df_result_is_not_set, MesureRegularite.resultat_sup]
    )

    return df_score


def set_first_record_to_compliant(df_score: pd.DataFrame) -> pd.DataFrame:
    """Fixe un score de conformité pour la régularité "conforme" au premier passage de la période analysée.
    Le premier passage est toujours considéré comme "conforme" car il n'y a pas de passage précédent permettant de
    calculer un intervalle.

    Parameters
    ----------
    df_score : DataFrame
        DataFrame qui contient les scores de conformité

    Returns
    ----------
    df_score : DataFrame
        DataFrame qui contient les scores de conformité auxquels on a fixé le score de conformité du premier passage
    """
    df_score.loc[
        df_score[MesureRegularite.heure_reelle].idxmin(), MesureRegularite.resultat
    ] = ComplianceType.compliant

    return df_score


def choose_best_score(df: pd.DataFrame) -> pd.DataFrame:
    """Sélectionne le score de conformité pour la régularité le plus optimal pour chaque passage réel d'un arrêt.
    Trois situations sont possibles :
    1. les intervalles supérieurs et inférieurs ne sont pas identiques, alors on sélectionne le plus petit intervalle de
    temps
    2. les intervalles supérieurs et inférieurs sont identiques, alors on sélectionne celui qui donne le meilleur score
    3. le passage réel est le premier de la période analysée, alors on fixe son score à "conforme"

    Parameters
    ----------
    df : DataFrame
        Dataframe en entrée qui contient les scores de conformité de la borne inférieure er borne supérieure

    Returns
    ----------
    result_df : DataFrame
        DataFrame qui contient les scores de conformités finaux et optimisés
    """
    df_score = df.copy()
    df_score[MesureRegularite.resultat] = np.nan

    df_score = select_closest_defined_time_result(df_score)
    df_score = select_best_score_if_equals(df_score)
    df_score = set_first_record_to_compliant(df_score)

    result_df = df_score[[MesureRegularite.heure_reelle, MesureRegularite.resultat]]

    assert not any(result_df[MesureRegularite.resultat].isna())

    return result_df
