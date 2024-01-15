from datetime import datetime, timedelta
import logging

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.usecases.aggregate_mesure_qs import aggregate_mesure_qs
from offre_realisee.domain.usecases.create_mesure_qs import create_mesure_qs
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler
from config.config import data_path_config
from config.logger import logger
from data import DATA_PATH


def main(start_date: datetime, end_date: datetime) -> None:
    file_system_handler = LocalFileSystemHandler(
        data_path=DATA_PATH,
        input_path=data_path_config['input_path'],
        output_path=data_path_config['output_path'],
        input_file_name=data_path_config['input_file_name']
    )

    current_date = start_date
    while current_date <= end_date:
        create_mesure_qs(file_system_handler, current_date)
        current_date += timedelta(days=1)

    date_range = (start_date, end_date)

    for aggregation_level in [AggregationLevel.by_period, AggregationLevel.by_period_weekdays]:
        aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.ponctualite)
        aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.regularite)


if __name__ == '__main__':
    logger.setLevel(logging.INFO)

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 1)

    main(start_date=start_date, end_date=end_date)
