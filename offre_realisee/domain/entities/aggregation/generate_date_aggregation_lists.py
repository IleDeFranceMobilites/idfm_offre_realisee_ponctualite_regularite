from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from offre_realisee.config.aggregation_config import AggregationLevel, suffix_by_agg


def generate_date_aggregation_lists(
        date_range: Tuple[datetime, datetime], aggregation_level: AggregationLevel) -> Dict[str, List[datetime]]:
    """Liste toutes les dates de la plage de date donnée avec leur suffix d'aggégation.

    Parameters
    ----------
    date_range : Tuple[datetime, datetime]
        Tuple de deux dates, une date de début et une de fin.
    aggregation_level : AggregationLevel
        Niveau de l'aggrégation (by_day, by_month, by_year, ...)

    Returns
    -------
    dict_date_lists : Dict[str, List[datetime]]
        Dictionnaire avec en clé le suffix de l'aggrégation (%Y pour by_year, %Y_%M pour by_month, ...) et en valeur
        une liste de date en datetime.
    """
    dict_date_lists: Dict[str, List[datetime]] = defaultdict(list)
    suffix_generator = suffix_by_agg[aggregation_level]

    date_i = date_range[0]
    while date_i <= date_range[1]:
        suffix = suffix_generator(date_i)
        dict_date_lists[suffix].append(date_i)
        date_i = date_i + timedelta(days=1)
    return dict_date_lists
