import numpy as np
import pandas as pd

from offre_realisee.config.input_brute_config import (COLONNES_BRUTES_REQUISES, InputBruteColumns,
                                                      TIMEZONE_OFFRE_REALISEE)
from offre_realisee.config.input_config import InputColumns
from offre_realisee.config.logger import logger


COLONNES_OFFRE_REALISEE = [
    InputColumns.jour,
    InputColumns.ligne,
    InputColumns.sens,
    InputColumns.arret,
    InputColumns.course_id,
    InputColumns.is_terminus,
    InputColumns.heure_theorique,
    InputColumns.heure_reelle,
]


def transform_offre_realisee_brute(df_offre_realisee_brute: pd.DataFrame) -> pd.DataFrame:
    """Transforme les données brutes d'offre réalisée livrées par le transporteur au format attendu en entrée.

    La transformation consiste à :
      - ne conserver que les passages évaluables (`PASSAGE_EVALUABLE`) ;
      - fusionner les heures de départ et d'arrivée en une seule heure de passage : l'heure de départ si elle est
        renseignée, sinon l'heure d'arrivée (cas du terminus d'arrivée, qui n'a pas d'heure de départ) ;
      - localiser les heures en UTC, les heures brutes étant naïves et déjà exprimées en UTC ;
      - reprendre `SENS_ID` comme `SENS` ;
      - ne conserver que les colonnes nécessaires au calcul de la qualité de service. Les autres colonnes du format de
        livraison sont ignorées.

    Les lignes dont l'heure théorique est nulle (passage réel non prévu) ou dont l'heure réelle est nulle (absence de
    données) sont conservées : elles portent une information métier utilisée par le calcul des mesures.

    Parameters
    ----------
    df_offre_realisee_brute : DataFrame
        DataFrame contenant les données brutes d'offre réalisée.

    Returns
    -------
    df_offre_realisee : DataFrame
        DataFrame d'offre réalisée au format attendu en entrée du calcul des mesures.

    Raises
    ------
    ValueError
        Si une colonne brute requise est absente, ou si la colonne `PASSAGE_EVALUABLE` n'est pas booléenne.
    """
    colonnes_manquantes = [col for col in COLONNES_BRUTES_REQUISES if col not in df_offre_realisee_brute.columns]
    if colonnes_manquantes:
        raise ValueError(f"Colonnes absentes des données brutes d'offre réalisée : {colonnes_manquantes}")

    nombre_lignes_brutes = len(df_offre_realisee_brute)
    masque_evaluable = _masque_passage_evaluable(df_offre_realisee_brute[InputBruteColumns.passage_evaluable])
    df_offre_realisee = df_offre_realisee_brute[masque_evaluable]

    logger.info(f"Passages évaluables : {len(df_offre_realisee)} sur {nombre_lignes_brutes} lignes brutes "
                f"({nombre_lignes_brutes - len(df_offre_realisee)} passages non évaluables écartés)")

    df_offre_realisee = df_offre_realisee.assign(**{
        InputColumns.sens: _sens(df_offre_realisee[InputBruteColumns.sens_id]),
        InputColumns.heure_theorique: _heure_de_passage(
            df_offre_realisee, InputBruteColumns.heure_depart_theorique, InputBruteColumns.heure_arrivee_theorique),
        InputColumns.heure_reelle: _heure_de_passage(
            df_offre_realisee, InputBruteColumns.heure_depart_reelle, InputBruteColumns.heure_arrivee_reelle),
    })

    return df_offre_realisee[COLONNES_OFFRE_REALISEE]


def _masque_passage_evaluable(serie_passage_evaluable: pd.Series) -> pd.Series:
    """Construit le masque des passages évaluables. Un passage non renseigné n'est pas évaluable.

    Parameters
    ----------
    serie_passage_evaluable : Series
        Colonne brute `PASSAGE_EVALUABLE`.

    Returns
    -------
    masque : Series
        Masque booléen des passages à conserver.

    Raises
    ------
    ValueError
        Si la colonne contient des valeurs non booléennes : les convertir sans les interpréter rendrait vrai toute
        valeur non vide, y compris "false".
    """
    valeurs_inattendues = {
        valeur for valeur in serie_passage_evaluable.dropna().unique()
        if not isinstance(valeur, (bool, np.bool_))
    }
    if valeurs_inattendues:
        raise ValueError(f"La colonne {InputBruteColumns.passage_evaluable} doit être booléenne, "
                         f"valeurs inattendues : {sorted(map(str, valeurs_inattendues))}")

    return serie_passage_evaluable.eq(True).fillna(False).astype(bool)


def _sens(serie_sens_id: pd.Series) -> pd.Series:
    """Construit le sens à partir de l'identifiant de sens livré par le transporteur.

    `SENS_ID` ne vaut que 0 ou 1 et n'est utilisé que comme clé de regroupement : il est repris tel quel, converti en
    chaîne de caractères. Le passage par `Int64` évite qu'un identifiant livré en décimal devienne "0.0".

    Parameters
    ----------
    serie_sens_id : Series
        Colonne brute `SENS_ID`.

    Returns
    -------
    sens : Series
        Sens du déplacement sur la ligne, sous forme de chaîne de caractères.
    """
    if pd.api.types.is_numeric_dtype(serie_sens_id):
        serie_sens_id = serie_sens_id.astype('Int64')

    return serie_sens_id.astype('string')


def _heure_de_passage(df_offre_realisee_brute: pd.DataFrame, colonne_depart: str, colonne_arrivee: str) -> pd.Series:
    """Fusionne une heure de départ et une heure d'arrivée en une heure de passage en UTC.

    Parameters
    ----------
    df_offre_realisee_brute : DataFrame
        DataFrame contenant les données brutes d'offre réalisée.
    colonne_depart : str
        Nom de la colonne brute contenant l'heure de départ.
    colonne_arrivee : str
        Nom de la colonne brute contenant l'heure d'arrivée.

    Returns
    -------
    heure_de_passage : Series
        Heure de départ si elle est renseignée, sinon heure d'arrivée, sous la timezone UTC.
    """
    return _en_utc(df_offre_realisee_brute[colonne_depart]).fillna(_en_utc(df_offre_realisee_brute[colonne_arrivee]))


def _en_utc(serie_heure: pd.Series) -> pd.Series:
    """Exprime une colonne d'heures sous la timezone UTC.

    Les heures brutes sont naïves et déjà exprimées en UTC : elles sont donc localisées sans conversion. Une colonne
    déjà localisée est convertie en UTC.

    Parameters
    ----------
    serie_heure : Series
        Colonne d'heures brutes.

    Returns
    -------
    serie_heure : Series
        Colonne d'heures sous la timezone UTC.
    """
    serie_heure = pd.to_datetime(serie_heure)

    if serie_heure.dt.tz is None:
        return serie_heure.dt.tz_localize(TIMEZONE_OFFRE_REALISEE)
    return serie_heure.dt.tz_convert(TIMEZONE_OFFRE_REALISEE)
