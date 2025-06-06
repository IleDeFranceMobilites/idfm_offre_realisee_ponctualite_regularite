# Profiling

Dans le but d'accélérer les calculs des indicateurs de régularité, nous effectuons un profiling du code.
La majeur partie du temps d'execution est passée dans la fonctions : [`process_stop_regularite`](../../offre_realisee/domain/entities/regularite/process_stop_regularite.py)
Une optimisation intéressante (25% de temps gagné sur le traitement global de la fonction process_stop_regularite) est trouvée sur la fonction :
[`calculate_compliance_score_for_each_borne`](../../offre_realisee/domain/entities/regularite/compliance_score.py) en utilisant `np.select()`
cette optimisation permet d'une part d'accélérer les processus de calcul, mais également de rendre le code plus lisible, nous choisissons de l'appliquer.