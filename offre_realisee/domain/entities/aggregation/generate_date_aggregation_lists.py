from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from offre_realisee.config.aggregation_config import AggregationLevel, suffix_by_agg


def generate_date_aggregation_lists(
        date_range: Tuple[datetime, datetime], aggregation_level: AggregationLevel) -> Dict[str, List[datetime]]:

    dict_date_lists: Dict[str, List[datetime]] = defaultdict(list)
    suffix_generator = suffix_by_agg[aggregation_level]

    date_i = date_range[0]
    while date_i <= date_range[1]:
        suffix = suffix_generator(date_i)
        dict_date_lists[suffix].append(date_i)
        date_i = date_i + timedelta(days=1)
    return dict_date_lists
