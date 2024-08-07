from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from offre_realisee.config.aggregation_config import AggregationLevel


def generate_date_aggregation_lists(
        date_range: tuple[datetime, datetime], aggregation_level: AggregationLevel,
        suffix_by_agg: dict[AggregationLevel, callable], list_journees_exceptionnelles: Optional[list[datetime]] = None
) -> dict[str, list[datetime]]:
    """Liste toutes les dates de la plage de date donnée avec leur suffix d'agrégation.

    Parameters
    ----------
    date_range : Tuple[datetime, datetime]
        Tuple de deux dates, une date de début et une de fin.
    aggregation_level : AggregationLevel
        Niveau de l'aggrégation (by_day, by_month, by_year, ...)
    suffix_by_agg: Dict[AggregationLevel, Callable]
        Dictionnaire de fonction de génération de suffix basé sur la date et le calendrier scolaire.
    list_journees_exceptionnelles : Optional[List[datetime]]
        Liste des journées exceptionnelles à exclures des calculs agrégés.

    Returns
    -------
    dict_date_lists : Dict[str, List[datetime]]
        Dictionnaire avec en clé le suffix de l'aggrégation (%Y pour by_year, %Y_%M pour by_month, ...) et en valeur
        une liste de date en datetime.
    """
    dict_date_lists: dict[str, list[datetime]] = defaultdict(list)
    suffix_generator = suffix_by_agg[aggregation_level]

    if list_journees_exceptionnelles is None:
        list_journees_exceptionnelles = []

    date_i = date_range[0]
    while date_i <= date_range[1]:
        if date_i not in list_journees_exceptionnelles:
            suffix = suffix_generator(date_i)
            dict_date_lists[suffix].append(date_i)
        date_i = date_i + timedelta(days=1)
    return dict_date_lists
