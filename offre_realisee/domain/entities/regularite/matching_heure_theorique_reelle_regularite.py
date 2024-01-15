import numpy as np
import pandas as pd

from offre_realisee.config.offre_realisee_config import MesureRegularite


def _formate_to_dataframe(matching_array: np.ndarray) -> pd.DataFrame:
    matching_array_df = pd.DataFrame(matching_array, columns=[MesureRegularite.heure_reelle,
                                                              MesureRegularite.difference_reelle,
                                                              MesureRegularite.heure_theorique_inf,
                                                              MesureRegularite.difference_theorique_inf,
                                                              MesureRegularite.heure_theorique_sup,
                                                              MesureRegularite.difference_theorique_sup])

    for col in [MesureRegularite.difference_reelle, MesureRegularite.difference_theorique_inf,
                MesureRegularite.difference_theorique_sup]:
        matching_array_df[col] = pd.to_timedelta(matching_array_df[col])

    for col in [MesureRegularite.heure_reelle, MesureRegularite.heure_theorique_inf,
                MesureRegularite.heure_theorique_sup]:
        matching_array_df[col] = pd.to_datetime(matching_array_df[col], utc=True)

    return matching_array_df


def matching_heure_theorique_reelle_regularite(df_by_stop: pd.DataFrame) -> pd.DataFrame:
    heure_theorique_sorted = np.sort(df_by_stop[MesureRegularite.heure_theorique].dropna().to_numpy())
    heure_reelle_sorted = np.sort(df_by_stop[MesureRegularite.heure_reelle].dropna().to_numpy())

    indices_superieur = np.searchsorted(heure_theorique_sorted, heure_reelle_sorted)
    indices_inferieur = indices_superieur - 1

    # If there are several real values lower than the first theoretical value,
    # compare the difference with the second theoretical time
    indices_superieur[1:][indices_superieur[1:] == 0] = 1

    diff_theorique = np.concatenate([[np.timedelta64('NaT')], heure_theorique_sorted[1:] - heure_theorique_sorted[:-1]])
    diff_reelle = np.concatenate([[np.timedelta64('NaT')], heure_reelle_sorted[1:] - heure_reelle_sorted[:-1]])

    # La première heure n'est pas assignable pour une comparaison, elle ne possède pas de valeur d'interval
    heure_theorique_sorted[0] = np.datetime64('NaT')

    heure_theorique_with_diff = np.column_stack([heure_theorique_sorted, diff_theorique])
    heure_reelle_with_diff = np.column_stack([heure_reelle_sorted, diff_reelle])

    heure_theorique_with_diff_and_padding = np.concatenate(
        [heure_theorique_with_diff, [[np.datetime64('NaT'), np.timedelta64('NaT')]]]
    )

    matching_array = np.column_stack((
        heure_reelle_with_diff,
        heure_theorique_with_diff_and_padding[indices_inferieur],
        heure_theorique_with_diff_and_padding[indices_superieur]
    ))

    return _formate_to_dataframe(matching_array)
