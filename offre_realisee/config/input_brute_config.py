from offre_realisee.config.file_extensions import FileExtensions


class InputBruteColumns:
    ligne = 'LIGNE'
    jour = 'JOUR'
    sens = 'SENS'
    arret = 'ARRET'
    course_id = 'COURSE_ID'
    is_terminus = 'IS_TERMINUS'
    heure_theorique_depart = 'HEURE_THEORIQUE_DEPART'
    heure_theorique_arrivee = 'HEURE_THEORIQUE_ARRIVEE'
    heure_reelle_depart = 'HEURE_REELLE_DEPART'
    heure_reelle_arrivee = 'HEURE_REELLE_ARRIVEE'
    passage_evaluable = 'PASSAGE_EVALUABLE'


# Colonnes que le fichier brut livré par le transporteur doit contenir pour pouvoir être transformé.
COLONNES_BRUTES_REQUISES = [
    InputBruteColumns.ligne,
    InputBruteColumns.jour,
    InputBruteColumns.sens,
    InputBruteColumns.arret,
    InputBruteColumns.course_id,
    InputBruteColumns.is_terminus,
    InputBruteColumns.heure_theorique_depart,
    InputBruteColumns.heure_theorique_arrivee,
    InputBruteColumns.heure_reelle_depart,
    InputBruteColumns.heure_reelle_arrivee,
    InputBruteColumns.passage_evaluable,
]

# Les heures brutes sont naïves et déjà exprimées en UTC : on les localise sans conversion.
TIMEZONE_OFFRE_REALISEE = 'UTC'

# Les transporteurs livrent un fichier par jour : le nom du fichier est construit à partir de sa date.
DEFAULT_INPUT_BRUTE_PATH = 'input_brute'
DEFAULT_INPUT_BRUTE_FILE_NAME_PATTERN = f'offre_realisee_brute_%Y-%m-%d{FileExtensions.parquet}'
