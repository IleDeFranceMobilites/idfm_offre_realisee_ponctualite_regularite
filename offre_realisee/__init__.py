import argparse
from datetime import datetime
import logging
from typing import Optional

from offre_realisee.config.aggregation_config import DEFAULT_PERIODE_ETE, AggregationLevel
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
    'periode-ete': DEFAULT_PERIODE_ETE
}


def compute_qs(
    telecharge_calendrier_scolaire: bool,
    mesure: bool,
    aggregation: bool,
    ponctualite: bool,
    regularite: bool,
    data_path: str,
    start_date: datetime,
    end_date: datetime,
    dsp: str,
    input_path: str,
    output_path: str,
    input_file_name: str,
    calendrier_scolaire_file_name: str,
    periode_ete: tuple[str],
    list_journees_exceptionnelles: Optional[list[datetime]],
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
                                    periode_ete, list_journees_exceptionnelles)
            if regularite:
                aggregate_mesure_qs(file_system_handler, date_range, aggregation_level, MesureType.regularite,
                                    periode_ete, list_journees_exceptionnelles)


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

    parser.add_argument('--start-date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="Première date à traiter. Doit être au format : YYYY-MM-DD\n"
                        "First date to process. Must be in format: YYYY-MM-DD")
    parser.add_argument('--end-date', required=True, type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                        help="Dernière date à traiter. Doit être au format : YYYY-MM-DD\n"
                        "Last date to process. Must be in format: YYYY-MM-DD")

    parser.add_argument('--dsp', required=False, type=str,
                        help="DSP à calculer si elle existe.\n"
                        "DSP to process.")

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
    parser.add_argument('--periode-ete', nargs=2,
                        default=default_data_path_config["periode-ete"], type=str,
                        help="Dates sous forme de string au format ['mois_jour', 'mois_jour'] "
                             "definissant la période d'été. (default: %(default)s)\n"
                             "Summer period between two dates. (default: %(default)s)")

    parser.add_argument('--list-journees-exceptionnelles', nargs="*", default=[],
                        type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
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
        start_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2023-01-02", "%Y-%m-%d"),
        dsp="",
        input_path=default_data_path_config["input-path"],
        output_path=default_data_path_config["output-path"],
        input_file_name=default_data_path_config["input-file-name"],
        calendrier_scolaire_file_name=default_data_path_config["calendrier-scolaire-file-name"],
        periode_ete=DEFAULT_PERIODE_ETE,
        list_journees_exceptionnelles=None,

        n_thread=5,
    )
