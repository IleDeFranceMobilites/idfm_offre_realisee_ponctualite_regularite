from datetime import timedelta
import numpy as np
import pandas as pd

from offre_realisee.config.offre_realisee_config import Borne, MesureRegularite, ComplianceType


def calculate_compliance_score_for_each_borne(df_with_interval: pd.DataFrame) -> pd.DataFrame:
    df_with_score = df_with_interval.copy()

    for borne in [Borne.inf, Borne.sup]:
        df_with_score.loc[
            (df_with_score[MesureRegularite.difference_reelle] < timedelta(minutes=2)),
            MesureRegularite.resultat + borne] = ComplianceType.situation_inacceptable_train_de_bus

        df_with_score.loc[
            (df_with_score[MesureRegularite.difference_reelle] >= timedelta(minutes=2)) &
            (df_with_score[MesureRegularite.difference_reelle] <= (
                    df_with_score[MesureRegularite.difference_theorique + borne] + timedelta(minutes=2))),
            MesureRegularite.resultat + borne] = ComplianceType.compliant

        df_with_score.loc[
            (df_with_score[MesureRegularite.difference_reelle] > (
                    df_with_score[MesureRegularite.difference_theorique + borne] + timedelta(minutes=2))) &
            (df_with_score[MesureRegularite.difference_reelle] <= df_with_score[
                MesureRegularite.difference_theorique + borne] * 2), MesureRegularite.resultat + borne
        ] = ComplianceType.semi_compliant

        df_with_score.loc[
            (df_with_score[MesureRegularite.difference_reelle] > df_with_score[
                MesureRegularite.difference_theorique + borne] * 2), MesureRegularite.resultat + borne
        ] = ComplianceType.situation_inacceptable_faible_frequence

    return df_with_score


def select_closest_defined_time_result(df_score: pd.DataFrame) -> pd.DataFrame:
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
    df_result_is_not_set = df_score[MesureRegularite.resultat].isna()
    df_score.loc[df_result_is_not_set, MesureRegularite.resultat] = df_score.loc[df_result_is_not_set].apply(
        lambda row: max(row[MesureRegularite.resultat_inf], row[MesureRegularite.resultat_sup]),
        axis=1
    )

    return df_score


def set_first_record_to_compliant(df_score: pd.DataFrame) -> pd.DataFrame:
    df_score.loc[
        df_score[MesureRegularite.heure_reelle].idxmin(), MesureRegularite.resultat
    ] = ComplianceType.compliant

    return df_score


def choose_best_score(df: pd.DataFrame) -> pd.DataFrame:
    df_score = df.copy()
    df_score[MesureRegularite.resultat] = np.NaN

    df_score = select_closest_defined_time_result(df_score)
    df_score = select_best_score_if_equals(df_score)
    df_score = set_first_record_to_compliant(df_score)

    result_df = df_score[[MesureRegularite.heure_reelle, MesureRegularite.resultat]]

    assert not any(result_df[MesureRegularite.resultat].isna())

    return result_df
