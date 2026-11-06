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
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- input_brute\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- offre_realisee_brute_AAAA-MM-JJ.parquet\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- input\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- input-file-name\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- JOUR=AAAA-MM-JJ\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- calendrier-scolaire-file-name\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|- output

Le dossier "**input-brute-path**" ne concerne que l'étape de préparation (`--preparation`) : il contient les données brutes livrées par le transporteur, à raison d'un fichier par jour.

Les valeurs suivantes peuvent être modifiées en fonction de la structure de votre répertoire :
- data-path
- input (Valeur par défaut: "input")
- output (Valeur par défaut: "output")
- input-file-name (Valeur par défaut: "offre_realisee.parquet")
- calendrier-scolaire-file-namee (Valeur par défaut: "calendrier_scolaire.parquet")
- input-brute-path (Valeur par défaut: "input_brute")
- input-brute-file-name-pattern (Valeur par défaut: "offre_realisee_brute_%Y-%m-%d.parquet")

#### Format des données
Certaines colonnes doivent être présente dans les fichiers d'entrée :
- LIGNE : Identifiant unique de ligne (idéalement égale à l'identifiant dans [le référentiel ILICO](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://data.iledefrance-mobilites.fr/api/v2/catalog/datasets/referentiels-lignes-arrets-offre-netex/attachments/referentiel_des_lignes_netex_v1_pdf&ved=2ahUKEwjiyveh8OCKAxUTR6QEHY-UNCEQFnoECA4QAQ&usg=AOvVaw1Q8OgKhgRHN2Ao_Yyw8Lcr))
- SENS : Sens du déplacement sur la ligne (0 ou 1)
- ARRET : Identifiant unique de l'arrêt sur la ligne (idéalement égale à l'identifiant dans [le referentiel ICAR](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://data.iledefrance-mobilites.fr/api/v2/catalog/datasets/referentiels-lignes-arrets-offre-netex/attachments/referentiel_des_arrets_netex_v1_pdf&ved=2ahUKEwiyz6Wi8eCKAxWOT6QEHdTUPKIQFnoECBMQAQ&usg=AOvVaw1NZUNibX1nfLt94B3-txG3))
- COURSE_ID : Identifiant unique de la course théorique
- HEURE_THEORIQUE : Heure de passage théorique
- HEURE_REELLE : Heure de passage réalisée
- IS_TERMINUS : Indique si l'arrêt correspond à un terminus ou non (Booléen)

Si vos données sont au format brut transporteur (heures séparées en départ / arrivée et colonne PASSAGE_EVALUABLE), l'étape de préparation `--preparation` les transforme au format ci-dessus. Le détail des colonnes brutes attendues et des règles de transformation est décrit dans la [notice technique](0_documentation/QS_notice_tech.md).


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
- la préparation des données brutes (`--preparation`), la mesure ou l’agrégation uniquement
- la ponctualité ou la régularité uniquement

Par défaut la qualité de service est calculé par jour et agrégée par période pour la ponctualité et la régularité.

#### Plus de détails sur les paramètres d'execution du package

```console
$ offre_realisee -h
usage: offre_realisee [-h] [--telecharge-calendrier-scolaire | --no-telecharge-calendrier-scolaire]
                      [--preparation | --no-preparation] [--mesure | --no-mesure]
                      [--aggregation | --no-aggregation] [--ponctualite | --no-ponctualite] [--regularite | --no-regularite] --data-path
                      DATA_PATH --start-date START_DATE --end-date END_DATE [--input-path INPUT_PATH] [--output-path OUTPUT_PATH]
                      [--input-file-name INPUT_FILE_NAME] [--input-brute-path INPUT_BRUTE_PATH]
                      [--input-brute-file-name-pattern INPUT_BRUTE_FILE_NAME_PATTERN]
                      [--calendrier-scolaire-file-name CALENDRIER_SCOLAIRE_FILE_NAME]
                      [--periode-ete-start-date PERIODE_ETE_START_DATE] [--periode-ete-end-date PERIODE_ETE_END_DATE]
                      [--list-journees-exceptionnelles [LIST_JOURNEES_EXCEPTIONNELLES ...]] [--n-thread N_THREAD]

Calcul de la qualite de service.
Compute qs

options:
  -h, --help            show this help message and exit
  --telecharge-calendrier-scolaire, --no-telecharge-calendrier-scolaire
                        Télécharge le calendrier scolaire.
                         (Valeur par défaut: False)
                        Download holidays.
  --preparation, --no-preparation
                        Transforme les données brutes livrées par le transporteur au format attendu en entrée.
                         (Valeur par défaut: False)
                        Transform raw input data to the expected input format.
  --mesure, --no-mesure
                        Calcule la mesure par jour.
                         (Valeur par défaut: True)
                        Compute mesure by day.
  --aggregation, --no-aggregation
                        Calcule l'agrégation des données journalières.
                         (Valeur par défaut: True)
                        Compute aggregation of daily mesures.
  --ponctualite, --no-ponctualite
                        Calcule les statistiques (mesure ou aggregation) sur la ponctualité.
                         (Valeur par défaut: True)
                        Compute stats on ponctualite.
  --regularite, --no-regularite
                        Calcule les statistiques (mesure ou aggregation) sur la régularité.
                         (Valeur par défaut: True)
                        Compute stats on regularite.
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
  --input-brute-path INPUT_BRUTE_PATH
                        Chemin relatif par rapport au 'data-path' vers le dossier des données brutes livrées par le transporteur. (Valeur par défaut: input_brute)
                        Relative path to the raw input folder from data path. (default: input_brute)
  --input-brute-file-name-pattern INPUT_BRUTE_FILE_NAME_PATTERN
                        Patron du nom des fichiers de données brutes, au format strftime (un fichier par jour). (Valeur par défaut: offre_realisee_brute_%Y-%m-%d.parquet)
                        Raw input file name pattern, in strftime format (one file per day). (default: offre_realisee_brute_%Y-%m-%d.parquet)
  --calendrier-scolaire-file-name CALENDRIER_SCOLAIRE_FILE_NAME
                        Nom du fichier du referentiel du calendrier scolaire. (default: calendrier_scolaire.parquet)
                        School calendar parquet file name. (default: calendrier_scolaire.parquet)
  --periode-ete-start-date PERIODE_ETE_START_DATE
                        Première date de la periode d'été. Doit être au format : YYYY-MM-DD
                        Summer first date. Must be in format: YYYY-MM-DD
  --periode-ete-end-date PERIODE_ETE_END_DATE
                        Dernière date de la periode d'été. Doit être au format : YYYY-MM-DD
                        Summer last date. Must be in format: YYYY-MM-DD
  --list-journees-exceptionnelles [LIST_JOURNEES_EXCEPTIONNELLES ...]
                        Liste des dates des journées exceptionnelles à exclure des calculs agrégés. (Valeur par défaut: None)
                        Datetime list of exceptionnal days to exclude. (default: None)
  --n-thread N_THREAD   Nombre de threads en parallèle dans le calcul des mesures. (Valeur par défaut: 1)
                        Number of parallel threads. (default: 1)
```
