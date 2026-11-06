from offre_realisee.config.file_extensions import FileExtensions


class InputBruteColumns:
    ligne = 'LIGNE'
    jour = 'JOUR'
    sens_id = 'SENS_ID'
    arret = 'ARRET'
    course_id = 'COURSE_ID'
    is_terminus = 'IS_TERMINUS'
    heure_depart_theorique = 'HEURE_DEPART_THEORIQUE'
    heure_arrivee_theorique = 'HEURE_ARRIVEE_THEORIQUE'
    heure_depart_reelle = 'HEURE_DEPART_REELLE'
    heure_arrivee_reelle = 'HEURE_ARRIVEE_REELLE'
    passage_evaluable = 'PASSAGE_EVALUABLE'


# Colonnes que le fichier brut livré par le transporteur doit contenir pour pouvoir être transformé. Les autres colonnes
# du format de livraison (DSP, ORDRE, ZDA_NAME, ZDA_ID, LIGNE_NAME, HEURE_*_COMMANDEE, ELIGIBLE_DECALAGE) sont ignorées.
COLONNES_BRUTES_REQUISES = [
    InputBruteColumns.ligne,
    InputBruteColumns.jour,
    InputBruteColumns.sens_id,
    InputBruteColumns.arret,
    InputBruteColumns.course_id,
    InputBruteColumns.is_terminus,
    InputBruteColumns.heure_depart_theorique,
    InputBruteColumns.heure_arrivee_theorique,
    InputBruteColumns.heure_depart_reelle,
    InputBruteColumns.heure_arrivee_reelle,
    InputBruteColumns.passage_evaluable,
]

# Les heures brutes sont naïves et déjà exprimées en UTC : on les localise sans conversion.
TIMEZONE_OFFRE_REALISEE = 'UTC'

# Les transporteurs livrent un fichier par jour : le nom du fichier est construit à partir de sa date.
DEFAULT_INPUT_BRUTE_PATH = 'input_brute'
DEFAULT_INPUT_BRUTE_FILE_NAME_PATTERN = f'offre_realisee_brute_%Y-%m-%d{FileExtensions.parquet}'
