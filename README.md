# Introduction
Le projet permet de calculer les statistiques de qualité de service basées sur les données de l'offre réalisée.

[La documentation du code est disponible ici.](https://iledefrancemobilites.github.io/idfm_offre_realisee_ponctualite_regularite/index.html)

# Utiliser le module

## Structure du code

Le code est organisé selon l'architecture hexagonal.
- Les fonctions "principales" sont rangées dans le sous-dossier **usecases**.
- Les fonctions "secondaires", qui peuvent être appelées dans les "principales" sont rangées dans le sous-dossier
**entities**.
- Les variables sont définies dans les fichiers de configuration contenus dans le dossier **config**.
- Et enfin les fonctions relatives à l'infrastructure sont rangées dans le dossier **infrastructure**.

|- **sources**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- **offre_realisee**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- config\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- domain\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- entities\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- port\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- usecases\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- infrastructure

## Calculer les indicateurs de Qualité de Service

### Installer le package Python
```console
pip install idfm-qualite-de-service-calculateur
```

### Executer le module sur des données locales

#### Structure des données
Placer vos données dans un dossier respectant la structure définie.

Le code a été implémenté en suivant une structure de répertoire définie. Les données d'entrée doivent être un fichier parquet nommé "**input-file-name**" partitionné par jour "JOUR=AAAA-MM-JJ" en fonction du jour des données ainsi qu'un fichier parquet nommé "**calendrier-scolaire-file-name**" contenant le référentiel du calendrier scolaire (ce fichier pouvant être téléchargé via le code). Le dossier "**output**" contiendra les données de sortie. La création de dossiers pour organiser les fichiers de sortie est automatique.

|- **data-path**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- input\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- input-file-name\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- JOUR=AAAA-MM-JJ\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- calendrier-scolaire-file-name\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- output

Les valeurs suivantes peuvent être modifiées en fonction de la structure de votre répertoire :
- data-path
- input (Valeur par défaut: "input")
- output (Valeur par défaut: "output")
- input-file-name (Valeur par défaut: "offre_realisee.parquet")
- calendrier-scolaire-file-namee (Valeur par défaut: "calendrier_scolaire.parquet")


#### Exemple d'execution
```console
offre_realisee
    --telecharge-calendrier-scolaire
    --data-path=<dossier-racine-des-donnees>
    --start-date=YYYY-MM-DD
    --end-date=YYYY-MM-DD
    --input-path=<chemin-relatif-du-dossier-des-donnees-en-entree>
    --output-path=<chemin-relatif-du-dossier-des-donnees-en-sortie>
    --input-file-name=<nom-du-fichier-de-donnees-en-entree>
    --periode-ete 07_01 08_31
    --calendrier-scolaire-file-name=<nom-du-fichier-de-référentiel-du-calendrier-scolaire>
    --list-journees-exceptionnelles YYYY-MM-DD YYYY-MM-DD YYYY-MM-DD
    --n-thread=<nombre-de-thread-d'execution-parallèle>
```

Cette commande permet de calculer et d'agréger les statistiques de qualite de service entre la date de début (start-date) et la date de fin (end-date).

Des paramètres supplémentaires peuvent être ajoutés pour exécuter le script sur :
- le téléchargment du calendrier scolaire
- la mesure ou l’agrégation uniquement
- la ponctualité ou la régularité uniquement

Par défaut la qualité de service est calculé par jour et agrégée par période pour la ponctualité et la régularité.

#### Plus de détails sur les paramètres d'execution du package

```console
$ offre_realisee -h
usage: offre_realisee [-h] [--telecharge-calendrier-scolaire | --no-telecharge-calendrier-scolaire] [--mesure | --no-mesure]
                      [--aggregation | --no-aggregation] [--ponctualite | --no-ponctualite] [--regularite | --no-regularite]
                      --data-path DATA_PATH --start-date START_DATE --end-date END_DATE [--input-path INPUT_PATH]
                      [--output-path OUTPUT_PATH] [--input-file-name INPUT_FILE_NAME]
                      [--calendrier-scolaire-file-name CALENDRIER_SCOLAIRE_FILE_NAME] [--periode-ete PERIODE_ETE PERIODE_ETE]
                      [--list-journees-exceptionnelles [LIST_JOURNEES_EXCEPTIONNELLES ...]] [--n-thread N_THREAD]

Calcul de la qualite de service.
Compute qs

options:
  -h, --help            show this help message and exit
  --telecharge-calendrier-scolaire, --no-telecharge-calendrier-scolaire
                        Télécharge le calendrier scolaire.
                         (Valeur par défaut: False)
                        Download holidays. (default: False)
  --mesure, --no-mesure
                        Calcule la mesure par jour.
                         (Valeur par défaut: True)
                        Compute mesure by day. (default: True)
  --aggregation, --no-aggregation
                        Calcule l'agrégation des données journalières.
                         (Valeur par défaut: True)
                        Compute aggregation of daily mesures. (default: True)
  --ponctualite, --no-ponctualite
                        Calcule les statistiques (mesure ou aggregation) sur la ponctualité.
                         (Valeur par défaut: True)
                        Compute stats on ponctualite. (default: True)
  --regularite, --no-regularite
                        Calcule les statistiques (mesure ou aggregation) sur la régularité.
                         (Valeur par défaut: True)
                        Compute stats on regularite. (default: True)
  --data-path DATA_PATH
                        Chemin vers le dossier racine des données.
                        Path to the root folder of your data.
  --start-date START_DATE
                        Première date à traiter. Doit être au format : YYYY-MM-DD
                        First date to process. Must be in format: YYYY-MM-DD
  --end-date END_DATE   Dernière date à traiter. Doit être au format : YYYY-MM-DD
                        Last date to process. Must be in format: YYYY-MM-DD
  --input-path INPUT_PATH
                        Chemin relatif par rapport au 'data-path' vers le dossier d'entrée des données. (Valeur par défaut: input)
                        Relative path to input folder from data path. (default: input)
  --output-path OUTPUT_PATH
                        Chemin relatif par rapport au 'data-path' vers le dossier de sortie des données. (Valeur par défaut: output)
                        Relative path to output folder from data path. (default: output)
  --input-file-name INPUT_FILE_NAME
                        Nom du fichier de données d'entrée. (default: offre_realisee.parquet)
                        Input parquet file name. (default: offre_realisee.parquet)
  --calendrier-scolaire-file-name CALENDRIER_SCOLAIRE_FILE_NAME
                        Nom du fichier du referentiel du calendrier scolaire. (default: calendrier_scolaire.parquet)
                        School calendar parquet file name. (default: calendrier_scolaire.parquet)
  --periode-ete PERIODE_ETE PERIODE_ETE
                        Dates sous forme de string au format ['mois_jour', 'mois_jour'] definissant la période d'été. (default: ('07_01', '08_31'))
                        Summer period between two dates. (default: ('07_01', '08_31'))
  --list-journees-exceptionnelles [LIST_JOURNEES_EXCEPTIONNELLES ...]
                        Liste des dates des journées exceptionnelles à exclure des calculs agrégés. (Valeur par défaut: None)
                        Datetime list of exceptionnal days to exclude. (default: None)
  --n-thread N_THREAD   Nombre de threads en parallèle dans le calcul des mesures. (Valeur par défaut: 1)
                        Number of parallel threads. (default: 1)
```
