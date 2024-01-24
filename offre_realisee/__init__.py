import argparse
from datetime import datetime, timedelta
import logging

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.usecases.aggregate_mesure_qs import aggregate_mesure_qs
from offre_realisee.domain.usecases.create_mesure_qs_regularite import create_mesure_qs_regularite
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler
from offre_realisee.config.logger import logger


default_data_path_config = {
    'input-path': 'input',
    'output-path': 'output',
    'input-file-name': f'offre_realisee{FileExtensions.parquet}'
}


def compute_qs(
    mesure: bool,
    aggregation: bool,
    ponctualite: bool,
    regularite: bool,
    data_path: str,
    start_date: datetime,
    end_date: datetime,
    input_path: str,
    output_path: str,
    input_file_name: str,
) -> None:

    file_system_handler = LocalFileSystemHandler(
        data_path=data_path,
        input_path=input_path,
        output_path=output_path,
        input_file_name=input_file_name,
    )

    current_date = start_date
    if mesure:
        while current_date <= end_date:
            create_mesure_qs_regularite(file_system_handler, current_date)
            current_date += timedelta(days=1)

    if aggregation:
        date_range = (start_date, end_date)
        for aggregation_level in [AggregationLevel.by_period, AggregationLevel.by_period_weekdays]:
            if ponctualite:
                aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.ponctualite)
            if regularite:
                aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.regularite)


def main():  # noqa

    parser = argparse.ArgumentParser(
        description='Calcul de la qualite de service.\n'
                    'Compute qs',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--mesure', default=True, action=argparse.BooleanOptionalAction,
                        help="Calcule la mesure par jour.\n"
                        " (Valeur par défaut: %(default)s)\n"
                        "Compute mesure by day.")
    parser.add_argument('--aggregation', default=True, action=argparse.BooleanOptionalAction,
                        help="Calcule l'agrégation des données journalières.\n"
                        " (Valeur par défaut: %(default)s)\n"
                        "Compute aggregation of daily mesures.")

    parser.add_argument('--ponctualite', default=True, action=argparse.BooleanOptionalAction,
                        help="Calcule les statistiques (mesure ou aggregation) sur la ponctualité.\n"
                        " (Valeur par défaut: %(default)s)\n"
                        "Compute stats on ponctualite.")
    parser.add_argument('--regularite', default=True, action=argparse.BooleanOptionalAction,
                        help="Calcule les statistiques (mesure ou aggregation) sur la régularité.\n"
                        " (Valeur par défaut: %(default)s)\n"
                        "Compute stats on regularite.")

    parser.add_argument('--data-path', required=True, type=str,
                        help="Chemin vers le dossier racine des données.\n"
                        "Path to the root folder of your data.")

    parser.add_argument('--start-date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="Première date à traiter. Doit être au format : YYYY-MM-DD\n"
                        "First date to process. Must be in format: YYYY-MM-DD")
    parser.add_argument('--end-date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="Dernière date à traiter. Doit être au format : YYYY-MM-DD\n"
                        "Last date to process. Must be in format: YYYY-MM-DD")

    parser.add_argument('--input-path', default=default_data_path_config["input-path"], type=str,
                        help="Chemin relatif par rapport au 'data-path' vers le dossier d'entrée des données."
                        " (Valeur par défaut: %(default)s)\n"
                        "Relative path to input folder from data path. (default: %(default)s)")
    parser.add_argument('--output-path', default=default_data_path_config["output-path"], type=str,
                        help="Chemin relatif par rapport au 'data-path' vers le dossier de sortie des données."
                        " (Valeur par défaut: %(default)s)\n"
                        "Relative path to output folder from data path. (default: %(default)s)")
    parser.add_argument('--input-file-name', default=default_data_path_config["input-file-name"], type=str,
                        help="Nom du fichier de données d'entrée. (default: %(default)s)\n"
                        "Input parquet file name. (default: %(default)s)")

    args = parser.parse_args()

    logger.setLevel(logging.INFO)

    compute_qs(**vars(args))
