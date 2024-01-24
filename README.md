# Introduction
Le projet permet de calculer les statistiques de qualité de service basées sur les données de l'offre réalisée.

# Utiliser le module

## Installer le package Python
```console
git clone git@ssh.dev.azure.com:v3/IDFM-AZURE/Data%20Analytics/idfm_offre_realisee_qualite_de_service
cd idfm_offre_realisee_qualite_de_service
pip install .
```

## Run it on local data

### Data structure
Le code a été implémenté en suivant une structure de répertoire définie. Les données d'entrée doivent être un fichier parquet nommé "**input-file-name**" partitionné par jour "DAY=AAAA-MM-JJ" en fonction du jour des données. Le dossier "**output**" contiendra les données de sortie. La création de dossiers pour organiser les fichiers de sortie est automatique.

│─ **data-path**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ input\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ input-file-name\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ JOUR=AAAA-MM-JJ\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ output

Les valeurs suivantes peuvent être modifiées en fonction de la structure de votre répertoire :
- data-path
- input (Valeur par défaut: "input")
- output (Valeur par defaut: "output")
- input-file-name (Valeur par defaut: "offre_realisee.parquet")


### Example
```console
offre_realisee
    --data-path=<dossier-racine-des-donnees>
    --start-date=YYYY-MM-DD
    --end-date=YYYY-MM-DD
    --input-path=<chemin-relatif-du-dossier-des-donnees-en-entree>
    --output-path=<chemin-relatif-du-dossier-des-donnees-en-sortie>
    --input-file-name=<nom-du-fichier-de-donnees-en-entree>
```

Cette commande permet de calculer et d'agréger les statistiques de qualite de service entre la date de début (start-date) et la date de fin (end-date).

Des paramètres supplémentaires peuvent être ajoutés pour exécuter le script sur :
- la mesure ou l'aggrégation uniquement
- la ponctualité ou la régularité uniquement

Par défaut la qualité de service est calculé par jour et agrégée par période pour la ponctualité et la régularité.

### More details on this package parameters

```console
$ offre_realisee -h

usage: offre_realisee [-h] [--mesure] [--aggregation] [--ponctualite] [--regularite] --data-path DATA_PATH --start-date START_DATE --end-date END_DATE [--input-path INPUT_PATH] [--output-path OUTPUT_PATH] [--input-file-name INPUT_FILE_NAME]

Calcul de la qualite de service.
Compute qs

options:
  -h, --help            show this help message and exit
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
```
