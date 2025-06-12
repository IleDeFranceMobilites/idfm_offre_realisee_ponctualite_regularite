import argparse
from datetime import date, datetime
import logging
from typing import Optional

from offre_realisee.config.aggregation_config import AggregationLevel
from offre_realisee.config.file_extensions import FileExtensions
from offre_realisee.config.offre_realisee_config import MesureType
from offre_realisee.domain.usecases.aggregate_mesure_qs import aggregate_mesure_qs
from offre_realisee.domain.usecases.create_mesure_qs_ponctualite import create_mesure_qs_ponctualite_date_range
from offre_realisee.domain.usecases.create_mesure_qs_regularite import create_mesure_qs_regularite_date_range
from offre_realisee.domain.usecases.download_calendrier_scolaire import download_calendrier_scolaire
from offre_realisee.infrastructure.calendrier_scolaire_api_handler import CalendrierScolaireApiHandler
from offre_realisee.infrastructure.local_file_system_handler import LocalFileSystemHandler
from offre_realisee.config.logger import logger


default_data_path_config = {
    'input-path': 'input',
    'output-path': 'output',
    'input-file-name': f'offre_realisee{FileExtensions.parquet}',
    'calendrier-scolaire-file-name': f'calendrier_scolaire{FileExtensions.parquet}',
    'periode-ete-start-date': date(2023, 7, 1),
    'periode-ete-end-date': date(2023, 8, 31),
}


def compute_qs(
    telecharge_calendrier_scolaire: bool,
    mesure: bool,
    aggregation: bool,
    ponctualite: bool,
    regularite: bool,
    data_path: str,
    start_date: date,
    end_date: date,
    input_path: str,
    output_path: str,
    input_file_name: str,
    calendrier_scolaire_file_name: str,
    periode_ete_start_date: date,
    periode_ete_end_date: date,
    list_journees_exceptionnelles: Optional[list[date]],
    n_thread: 1,
) -> None:

    file_system_handler = LocalFileSystemHandler(
        data_path=data_path,
        input_path=input_path,
        output_path=output_path,
        input_file_name=input_file_name,
        calendrier_scolaire_file_name=calendrier_scolaire_file_name
    )

    if telecharge_calendrier_scolaire:
        calendrier_scolaire_api_handler = CalendrierScolaireApiHandler()
        download_calendrier_scolaire(calendrier_scolaire_api_handler, file_system_handler)

    date_range = (start_date, end_date)

    if mesure:
        if ponctualite:
            create_mesure_qs_ponctualite_date_range(file_system_handler, date_range, n_thread)
        if regularite:
            create_mesure_qs_regularite_date_range(file_system_handler, date_range, n_thread)

    if aggregation:
        for aggregation_level in [AggregationLevel.by_period, AggregationLevel.by_period_weekdays]:
            if ponctualite:
                aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.ponctualite,
                                    (periode_ete_start_date, periode_ete_end_date), list_journees_exceptionnelles)
            if regularite:
                aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.regularite,
                                    (periode_ete_start_date, periode_ete_end_date), list_journees_exceptionnelles)


def main():  # noqa

    parser = argparse.ArgumentParser(
        description='Calcul de la qualite de service.\n'
                    'Compute qs',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--telecharge-calendrier-scolaire', default=False, action=argparse.BooleanOptionalAction,
                        help="Télécharge le calendrier scolaire.\n"
                             " (Valeur par défaut: %(default)s)\n"
                             "Download holidays.")
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

    parser.add_argument('--start-date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
                        help="Première date à traiter. Doit être au format : YYYY-MM-DD\n"
                        "First date to process. Must be in format: YYYY-MM-DD")
    parser.add_argument('--end-date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
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
    parser.add_argument('--calendrier-scolaire-file-name',
                        default=default_data_path_config["calendrier-scolaire-file-name"], type=str,
                        help="Nom du fichier du referentiel du calendrier scolaire. (default: %(default)s)\n"
                             "School calendar parquet file name. (default: %(default)s)")

    parser.add_argument('--periode-ete-start-date', required=False,
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
                        help="Première date de la periode d'été. Doit être au format : YYYY-MM-DD\n"
                        "Summer first date. Must be in format: YYYY-MM-DD")
    parser.add_argument('--periode-ete-end-date', required=False,
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
                        help="Dernière date de la periode d'été. Doit être au format : YYYY-MM-DD\n"
                        "Summer last date. Must be in format: YYYY-MM-DD")

    parser.add_argument('--list-journees-exceptionnelles', nargs="*", default=[],
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
                        help="Liste des dates des journées exceptionnelles à exclure des calculs agrégés. "
                             "(Valeur par défaut: None)\n"
                        "Datetime list of exceptionnal days to exclude. (default: None)\n")

    parser.add_argument('--n-thread', default=1, type=int,
                        help="Nombre de threads en parallèle dans le calcul des mesures. "
                             "(Valeur par défaut: %(default)s)\n"
                        "Number of parallel threads. (default: %(default)s)")

    args = parser.parse_args()

    logger.setLevel(logging.INFO)

    compute_qs(**vars(args))


if __name__ == "__main__":
    compute_qs(
        telecharge_calendrier_scolaire=False,
        mesure=True,
        aggregation=True,
        ponctualite=True,
        regularite=True,
        data_path="./data",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 2),
        dsp="",
        input_path=default_data_path_config["input-path"],
        output_path=default_data_path_config["output-path"],
        input_file_name=default_data_path_config["input-file-name"],
        calendrier_scolaire_file_name=default_data_path_config["calendrier-scolaire-file-name"],
        periode_ete_start_date=default_data_path_config["periode-ete-start-date"],
        periode_ete_end_date=default_data_path_config["periode-ete-end-date"],
        list_journees_exceptionnelles=None,

        n_thread=5,
    )
