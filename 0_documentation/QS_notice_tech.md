# Notice technique - Calcul des indicateurs de Qualité de Service

# Partie 1 - Structure des données

## 1. Données en entrée

### Format des données
Ce code a été implémenté à partir d'un format de données en entrée dont toutes les colonnes sont nécessaires.
Les fichiers en entrée doivent être au format parquet. La granularité des fichiers est au jour (1 fichier par jour).
La partie "Arborescence" de la notice vous donnera l'organisation de ces fichiers dans les dossiers adéquats.
Ci-dessous, un descriptif des colonnes nécessaires pour l'exécution du code :

| Nom de la colonne | Type                | Description                                                                                                                             |
|:------------------|:--------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| LIGNE             | string              | Le numéro de la ligne de bus/tram/train concernée.                                                                                      |
| SENS              | string              | Le format des valeurs est `[arrêt_départ]->[terminus]`. Ex : "VIL->RAM".                                                                |
| ARRET             | string              | Le nom unique de l'arrêt. Si un arrêt est sur plusieurs lignes, le nom doit être le même.                                               |
| HEURE_THEORIQUE   | datetime64[ns, UTC] | L'heure théorique de passage du bus/tram/train. Les valeurs de cette colonne doivent être au format datetime et sous la timezone "UTC". |
| HEURE_REELLE      | datetime64[ns, UTC] | L'heure réelle de passage du bus/tram/train. Les valeurs de cette colonne doivent être au format datetime et sous la timezone "UTC".    |
| IS_TERMINUS       | boolean             | "False" si l'arrêt n'est pas le terminus de la course, "True" s'il s'agit du terminus.                                                  |


## 2. Données en sortie

Tous les fichiers de sortie sont au format csv de sorte à faciliter l'analyse (sous excel par exemple).

### Format des données - Ponctualité

| Nom de la colonne                                           | Type   | Description                                                                                                                                                                               |
|:------------------------------------------------------------|:-------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LIGNE                                                       | string | Le numéro de la ligne de bus/tram/train concernée.                                                                                                                                        |
| NOMBRE_PASSAGES_THEORIQUES                                  | int64  | Nombre de passages théoriques total sur la période analysée.                                                                                                                              |
| NOMBRE_PASSAGES_REELS                                       | int64  | Nombre de passages réels total sur la période analysée. Ce nombre peut-être inférieur au nombre de passages théoriques, à de rares occasions il peut être supérieur.                      |
| SCORE_DE_CONFORMITE                                         | float  | La somme de l'ensemble des scores de conformité obtenus par arrêt et par course sur la ligne pour la période analysée et selon les règles de calcul précisées dans le cahier des charges. |
| SITUATION_INACCEPTABLE_RETARD                               | int64  | Le nombre de SI causées par un retard >12min ou 15min selon la fréquence de la ligne.                                                                                                     |
| SITUATION_INACCEPTABLE_AVANCE                               | int64  | Le nombre de SI causées par une avance >2min.                                                                                                                                             |
| SITUATION_INACCEPTABLE_THEORIQUE_SANS_HORAIRE_REEL_ATTRIBUE | int64  | Le nombre de SI causées par un horaire de passage réel absent (face à un horaire de passage théorique renseigné).                                                                         |
| SITUATION_INACCEPTABLE_TOTAL                                | int64  | La somme de l'ensemble des SI pour la ligne et la période analysée.                                                                                                                       |
| TAUX_DE_CONFORMITE                                          | float  | Le score de conformité / nombre de passages théoriques * 100.                                                                                                                                   |
| TAUX_ABSENCE_DE_DONNEES                                     | float  | (Le nombre de passages théoriques - le nombre de passages réels) / le nombre de passages théoriques * 100.                                                                                |

### Format des données - Régularité

| Nom de la colonne                                           | Type   | Description                                                                                                                                                                               |
|:------------------------------------------------------------|:-------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LIGNE                                                       | string | Le numéro de la ligne de bus/tram/train concernée.                                                                                                                                        |
| NOMBRE_PASSAGES_THEORIQUES                                  | int64  | Nombre de passages théoriques total sur la période analysée.                                                                                                                              |
| NOMBRE_PASSAGES_REELS                                       | int64  | Nombre de passages réels total sur la période analysée. Ce nombre peut-être inférieur au nombre de passages théoriques, à de rares occasions il peut être supérieur.                      |
| SCORE_DE_CONFORMITE                                         | float  | La somme de l'ensemble des scores de conformité obtenus par arrêt et par course sur la ligne pour la période analysée et selon les règles de calcul précisées dans le cahier des charges. |
| SITUATION_INACCEPTABLE_TRAIN_DE_BUS                         | int64  | Le nombre de SI causées par un train de bus (moins de 2min d'écart avec le passage du bus précédent).                                                                                     |
| SITUATION_INACCEPTABLE_ECART_IMPORTANT                      | int64  | Le nombre de SI causées par un écart important avec le passage du bus précédent (plus de 2 fois l'écart théorique avec le bus précédent).                                                 |
| SITUATION_INACCEPTABLE_TOTAL                                | int64  | La somme de l'ensemble des SI pour la ligne et la période analysée.                                                                                                                       |
| TAUX_DE_CONFORMITE                                          | float  | Le score de conformité / nombre de passages théoriques * 100.                                                                                                                                   |
| TAUX_ABSENCE_DE_DONNEES                                     | float  | (Le nombre de passages théoriques - le nombre de passages réels) / le nombre de passages théoriques * 100.                                                                                |

### Les niveaux d'aggrégation
Afin d'analyser plus finement certaines périodes et certaines situation, nous avons mis en place 3 niveaux d'aggrégation :
- par jour
- par mois
- par période
- par période et type de journée (semaine, samedi, dimanche, vacances scolaires/plein trafic/été)
- par année
- par année et type de journée (semaine ou weekend)

Le calendrier qui a permi de déterminer les vacances scolaires, le plein trafic et les vacances d'été est disponible
ci-dessous :

**Vacances scolaires :**
- 01/01/2023 - 02/01/2023
- 19/02/2023 - 05/03/2023
- 23/04/2023 - 06/05/2023
- 01/09/2023 - 03/09/2023
- 22/10/2023 - 05/11/2023
- 24/12/2023 - 31/12/2023

**Été :**
- 01/07/2023 - 31/08/2023

**Plein trafic :**
- 03/01/2023 - 18/02/2023
- 06/03/2023 - 22/04/2023
- 09/05/2023 - 30/06/2023
- 04/09/2023 - 21/10/2023
- 06/11/2023 - 23/12/2023

## 3. Arborescence

Le code a été implémenté suivant une arborescence définie. Les données d'entrée doivent être divisées par jour et par
ligne et placées dans le dossier "**silver**" et dans le sous-sous-dossier "JOUR=AAAA-MM-JJ" correspondant au jour des
données. Le dossier "**gold**" contiendra les données de sortie. La création des dossiers pour ranger les fichiers de
sortie est automatique.

├── **sources**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── offre_realisee\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── config\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;── domain\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── infrastructure

├── **data**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── **silver**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── offre_realisee.parquet\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── JOUR=AAAA-MM-JJ\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── *ligne_AAAA-MM-JJ.parquet*\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── **gold**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── ponctualite\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── *mesure_ponctualite_AAAA_MM_JJ.csv*\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── regularite\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── *mesure_regularite_AAAA_MM_JJ.csv*\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── **platinum**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── by_month\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── ponctualite\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── *mesure_ponctualite_AAAA_MM.csv*\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── regularite\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── *mesure_regularite_AAAA_MM.csv*\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── by_period\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── by_period_weekdays\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── by_period_weekdays_window\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── by_year\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── by_year_weekdays

# Partie 2 - Lancer le code

## Structure du code

Le code est organisé selon l'architecture hexagonal.
- Les fonctions "principales" sont rangées dans le sous-dossier **usecases**.
- Les fonctions "secondaires", qui peuvent être appelées dans les "principales" sont rangées dans le sous-dossier
**entities**.
- Les variables sont définies dans les fichiers de configuration contenus dans le dossier **config**.
- Et enfin les fonctions relatives à l'infrastructure sont rangées dans le dossier **infrastructure**.

├── **sources**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── **offre_realisee**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── config\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── domain\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── entities\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── port\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── usecases\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── infrastructure

## Calculer les indicateurs de Qualité de Service

### Installer le package Python
```console
git clone git@ssh.dev.azure.com:v3/IDFM-AZURE/Data%20Analytics/idfm_offre_realisee_qualite_de_service
cd idfm_offre_realisee_qualite_de_service
pip install .
```

### Executer le module sur des données locales

#### Structure des données
Placer vos données dans un dossier respectant la structure définie.

Le code a été implémenté en suivant une structure de répertoire définie. Les données d'entrée doivent être un fichier parquet nommé "**input-file-name**" partitionné par jour "DAY=AAAA-MM-JJ" en fonction du jour des données. Le dossier "**output**" contiendra les données de sortie. La création de dossiers pour organiser les fichiers de sortie est automatique.

│─ **data-path**\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ input\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ input-file-name\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ JOUR=AAAA-MM-JJ\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│─ output

Les valeurs suivantes peuvent être modifiées en fonction de la structure de votre répertoire :
- data-path
- input (Valeur par défaut: "input")
- output (Valeur par défaut: "output")
- input-file-name (Valeur par défaut: "offre_realisee.parquet")


#### Exemple d'execution
```console
offre_realisee
    --data-path=<dossier-racine-des-donnees>
    --start-date=YYYY-MM-DD
    --end-date=YYYY-MM-DD
    --input-path=<chemin-relatif-du-dossier-des-donnees-en-entree>
    --output-path=<chemin-relatif-du-dossier-des-donnees-en-sortie>
    --input-file-name=<nom-du-fichier-de-donnees-en-entree>
    --n-thread=<nombre-de-thread-d'execution-parallèle>
```

Cette commande permet de calculer et d'agréger les statistiques de qualite de service entre la date de début (start-date) et la date de fin (end-date).

Des paramètres supplémentaires peuvent être ajoutés pour exécuter le script sur :
- la mesure ou l’agrégation uniquement
- la ponctualité ou la régularité uniquement

Par défaut la qualité de service est calculé par jour et agrégée par période pour la ponctualité et la régularité.

#### Plus de détails sur les paramètres d'execution du package

```console
$ offre_realisee -h

usage: offre_realisee [-h] [--mesure | --no-mesure] [--aggregation | --no-aggregation] [--ponctualite | --no-ponctualite]
                      [--regularite | --no-regularite] --data-path DATA_PATH --start-date START_DATE --end-date END_DATE
                      [--input-path INPUT_PATH] [--output-path OUTPUT_PATH] [--input-file-name INPUT_FILE_NAME] [--n-thread N_THREAD]

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
  --n-thread N_THREAD   Nombre de threads en parallèle dans le calcul des mesures. (default: 1)
                        Number of parallel threads. (default: 1)
```

# Partie 3: Calcul de qualite de service

## Fréquence

Dans le calcul de la qualité de service, on distingue les passages en haute fréquence et les passages en faible
fréquence. Un passage à un arrêt sera considéré comme un passage de haute fréquence si les cinq passages théoriques
suivants du même arrêt ont lieu dans l'heure. Les cinq derniers passages sont donc systématiquement en basse fréquence.

## Ponctualite

### Calcul du score pour un passage théorique donné

Le score est calculé de la manière suivante pour chaque passage:

##### Haute fréquence
- Au le terminus de destination : Heure réelle <= Heure théorique - 1 min (une min d'avance ou plus)
    - Score = 1
- Pour les autres passages : Heure réelle <= Heure théorique - 1 min (une min d'avance ou plus)
    - Score = 0
    - Situation inacceptable avance
- Heure théorique - 1 min < Heure réelle <= Heure théorique + 3 min
    - Score = 1
- Heure théorique + 3 min < Heure réelle <= Heure théorique + 6 min
    - Score = 0.75
- Heure théorique + 6 min < Heure réelle < Heure théorique + 12 min
    - Score = 0.25
- Heure théorique + 12 min <= Heure réelle <= Heure théorique + 60 min
    - Score = 0
    - Situation inacceptable retard
- Heure théorique + 60 min < Heure réelle
    - Le trajet est considéré comme non affecté
    - Score = 0
    - Situation inacceptable absence
- Si le trajet n'est pas affecté
    - Score = 0
    - Situation inacceptable absence

##### Basse fréquence
- Au le terminus de destination : Heure réelle <= Heure théorique - 1 min (une min d'avance ou plus)
    - Score = 1
- Pour les autres passages : Heure réelle <= Heure théorique - 1 min (une min d'avance ou plus)
    - Score = 0
    - Situation inacceptable avance
- Heure théorique - 1 min < Heure réelle <= Heure théorique + 5 min
    - Score = 1
- Heure théorique + 5 min < Heure réelle <= Heure théorique + 10 min
    - Score = 0.5
- Heure théorique + 10 min < Heure réelle < Heure théorique + 15 min
    - Score = 0
- Heure théorique + 15 min <= Heure réelle <= Heure théorique + 60 min
    - Score = 0
    - Situation inacceptable retard
- Heure théorique + 60 min < Heure réelle
    - Le trajet est considéré comme non affecté
    - Score = 0
    - Situation inacceptable absence
- Si le trajet n'est pas affecté
    - Score = 0
    - Situation inacceptable absence

### Comment les passages réels sont-ils associés aux passages théoriques à un arrêt ?

Pour chaque arrêt d'une ligne donnée

- Pour l'ensemble des heures réelles et théorique
- Le score détaillé ci-dessus est calculé pour chaque paire possible
- On utilise un algorithme ([Algorithme Hongrois](https://en.wikipedia.org/wiki/Hungarian_algorithm)) afin de trouver la
meilleur combinaison possible entre ces heures réelles et théoriques. La meilleur combinaison est définie comme suit:
    - Elle minimise les situations inacceptables
    - Pour un nombre équivalent de situations inacceptables elle favorise les situations inacceptables de retard sur
    les autres et les situations inacceptables d'avance sur celles d'absence
    - Enfin, une fois ces deux conditions remplies, on maximise le score total (la somme des scores)

### Calcul du score pour une ligne par jours

Le score final est calculé de la manière suivante :
- Le nombre de situations inacceptables retenu est celui de l'arrêt de la ligne en ayant généré le plus.
- Le score est égal à la somme des scores par arrêts divisée par la somme des passages théoriques par arrêts.


## Regularite

### Calcul du score pour un passage théorique donné

Le score est calculé par intervals, l'interval entre deux passages réels doit être au plus proche de l'interval
entre deux passages théoriques.

Le calcul du score de régularité n'est possible que pour les lignes ayant au moins un arrêt avec une en haute fréquence
dans la journée.

Le score est calculé de la manière suivante pour chaque passage:

Soit :
- « i » l’intervalle théorique entre la course précédente et la course étudiée
- « i’ » l’intervalle réel entre la course précédente et la course étudiée

Score :
- Si i’ est inférieur à 1’30
    - Score = 0
    - Situation inacceptable train de bus
- Si i’ est supérieur ou égal à 1’30 et inférieur ou égal à i +2‘ alors 1
    - Score = 1
- Si i ‘ est supérieur à i +2’ et inférieur ou égal à 2i alors 0,5
    - Score = 0.65
- Si i’ est supérieur à 2i alors 0
    - Score = 0
    - Situation inacceptable faible frequence


### Comment les passages réels sont-ils associés aux passages théoriques à un arrêt ?

- Toutes les heures réelles sont considérées à l'exception de la première heure de la journée n'ayant pas de passage
antérieur donc pas d'interval.
- On associe à chaque heure réelle l'heure théorique la plus proche. (Une même heure théorique peut être associée à
deux heures réelles différentes)
- Dans le cas ou une heure réelle est aussi aussi proche de l'heure théorique inferieur que de l'heure théorique
supérieur on prend l'heure associée maximisant le score et minimisant les situations inacceptables.

### Calcul du score pour une ligne par jours

Le score final est calculé de la manière suivante:
- Le nombre de situations inacceptables est la somme des situations inacceptables générées par trajets.
- Le score est égal à la somme des scores par arrêts divisée par la somme des passages théoriques par arrêts.
