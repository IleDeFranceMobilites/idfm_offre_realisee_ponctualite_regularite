# Profiling

Dans le but d'accélérer les calculs des indicateurs de ponctualité, nous effectuons un profiling du code.
Il s'avère que la partie la plus lente des processus est la création de la matrice de coûts et en particulier des calculs des scores des paires théorique / réelles de la matrice (offre_realisee/domain/entities/ponctualite/compliance_score.py)
https://github.com/IleDeFranceMobilites/idfm_offre_realisee_ponctualite_regularite/blob/main/offre_realisee/domain/entities/ponctualite/process_stop_ponctualite.py

En cherchant à mieux cerner la source de la lenteur des processus (1s pour un fichier de 3k lignes) nous comprenons que la partie la plus lente du code réside dans les comparaisons des valeurs de la matrice avec les thresholds.

```python
    # Calcul de la compliance des arrêts
    matrix_score[
        (matrix > FrequencyThreshold.lower_si[freq]) & (matrix <= FrequencyThreshold.compliance[freq])
    ] = ComplianceType.compliant
    matrix_score[
        (matrix > FrequencyThreshold.compliance[freq]) & (matrix <= FrequencyThreshold.semi_compliance[freq])
    ] = ComplianceType.semi_compliant[MesureType.ponctualite][freq]
    matrix_score[
        (matrix > FrequencyThreshold.semi_compliance[freq]) & (matrix < FrequencyThreshold.upper_si[freq])
    ] = ComplianceType.not_compliant[MesureType.ponctualite][freq]
```

Il s'avère que les données contenues dans la matrice `matrix` sont des timedelta, ceux là sont construits en `numpy` sur la base de `datetimes pandas` :

```python
    matrix_timedelta = np.subtract.outer(
        heure_reelle_col,
        df_by_stop[MesurePonctualite.heure_theorique].to_numpy()
    ).T
```

Nous cherchons donc à travailler avec des timedeltas sous la forme d'integers représentant le nombre de secondes d'écart entre les dates et non plus avec des objets timedelta.

Cela semble réduire la durée du calcul de la matrice de coûts d'un facteur 100.
