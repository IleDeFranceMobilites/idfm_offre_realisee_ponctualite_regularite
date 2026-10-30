# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Batch CLI tool that computes transit quality-of-service (QS) statistics — **ponctualité**
(on-time performance) and **régularité** (headway adherence) — from Île-de-France Mobilités
"offre réalisée" data. Published to PyPI as `idfm-qualite-de-service-calculateur`; installing it
registers an `offre_realisee` console script (`[project.scripts]` in `pyproject.toml`).

Code, docstrings and docs are in French. Domain vocabulary (ponctualite, regularite, mesure,
aggregation, dsp, ligne, arret, sens) matches the identifiers — keep it in French when writing code.

## Commands

```bash
pip install -r requirements.txt -r requirements_dev.txt   # dev setup

make test                      # python3 -m pytest (what CI runs)
python3 -m pytest tests/test_unit/domain/entities/ponctualite/test_calculate_compliance_score.py
python3 -m pytest -k test_create_mesure_qs_ponctualite_date_range   # single test

make static-validation         # flake8 + vulture + safety + bandit — NOT run in CI, run locally
make yaml-validation           # yamllint (target references a missing .ci_templates/, currently broken)
make build-wheel               # python -m build --wheel
make generate-documentation    # sphinx-build -M html ./source ./0_documentation
```

- pytest has no config file; it discovers `tests/` by default (69 tests pass on the current tree).
- `.flake8`: `max-line-length = 120`, excludes `./.venv ./venv ./data ./tests ./.venv-qs`.
- `make static-validation` fails today at the `vulture` step: it reports pre-existing
  `situtation_conforme_types` / abstract-property findings in `offre_realisee/config/offre_realisee_config.py`
  and also scans the committed `build/` artifacts (not excluded). `flake8 .` alone is clean.
- CI (`.github/workflows/pipeline.yml`) runs only `make test`, on Python 3.11/3.12/3.13.
  Tagged `v*` pushes additionally build Sphinx docs → GitHub Pages and publish to PyPI.
- `pre-commit` is in `requirements_dev.txt` but there is no `.pre-commit-config.yaml` — nothing is
  wired up; don't assume hooks run.

## Running the pipeline

```bash
offre_realisee --data-path=./data --start-date=2023-09-27 --end-date=2023-09-28 [--n-thread=6]
```

`--data-path` is the root; `--input-path` (default `input`) and `--output-path` (default `output`)
are relative to it. Input must be `offre_realisee.parquet` partitioned by `JOUR=YYYY-MM-DD` with
columns `LIGNE, SENS, ARRET, HEURE_THEORIQUE, HEURE_REELLE, IS_TERMINUS` (see
`offre_realisee/config/input_config.py`). `--telecharge-calendrier-scolaire` fetches the school
calendar reference parquet from data.education.gouv.fr into the input folder.

Four boolean toggles (all default True) select the work: `--mesure` / `--aggregation` pick the stage,
`--ponctualite` / `--regularite` pick the mesure type. Use `--no-*` to narrow a run.

`--preparation` (default False, opt-in) adds an upstream bronze→silver stage: it reads one raw
transporteur parquet per day from `--input-brute-path` (file name built with
`--input-brute-file-name-pattern`, a strftime pattern), keeps the `PASSAGE_EVALUABLE` rows, merges
`HEURE_DEPART_*` / `HEURE_ARRIVEE_*` into `HEURE_THEORIQUE` / `HEURE_REELLE` (departure first, arrival
at the arrival terminus), localizes them to UTC, and writes the `JOUR=` partitions of
`input/offre_realisee.parquet` that the mesure stage reads. The transporteur delivery format is wider
than what is kept — see `COLONNES_BRUTES_REQUISES` in `config/input_brute_config.py` and the
"Préparation des données brutes" section of `0_documentation/QS_notice_tech.md`; extra delivered
columns (`DSP`, `ORDRE`, `ZDA_*`, `LIGNE_NAME`, `HEURE_*_COMMANDEE`, `ELIGIBLE_DECALAGE`) are ignored.

## Architecture

Hexagonal, inside the single `offre_realisee/` package. Respect the layering when adding code:

- **`config/`** — constants only, no I/O. `offre_realisee_config.py` is the central schema file:
  `MesureType`, the abstract `Mesure` and its `MesurePonctualite` / `MesureRegularite` column-name
  classes, the `MESURE_TYPE` registry, and `ComplianceType` scoring/penalty constants. Output CSV
  columns come from `Mesure.column_order` / `column_order_agregated` — adding an output column means
  editing these lists, plus `columns_to_sum` (the per-mesure list `aggregate_df` sums) and the output
  column tables in `0_documentation/QS_notice_tech.md` (the functional notice — a real doc, unlike the
  generated `0_documentation/html/`).
- **`domain/entities/`** — pure business logic on DataFrames, no I/O. Organized by concern:
  `ponctualite/`, `regularite/`, `aggregation/` (date bucketing + filename suffixes),
  `calendrier_scolaire/`, `preparation/` (raw → input schema), plus shared `add_frequency.py`,
  `drop_*.py`.
- **`domain/port/`** — abstract interfaces: `FileSystemHandler`, `CalendrierScolaireSourceHandler`,
  `CalendrierScolaireFileSystemHandler`, `OffreRealiseeBruteFileSystemHandler`. Any new I/O need goes
  through a port method.
- **`domain/usecases/`** — orchestration: `create_mesure_qs_ponctualite.py`,
  `create_mesure_qs_regularite.py`, `aggregate_mesure_qs.py`, `download_calendrier_scolaire.py`,
  `prepare_offre_realisee.py`.
  The `*_date_range` variants fan out over days with `multiprocess.Pool(processes=n_thread)`.
- **`infrastructure/`** — adapters: `LocalFileSystemHandler` (implements all three filesystem ports;
  all parquet/CSV paths and auto-mkdir live here) and `CalendrierScolaireApiHandler`.
- **`offre_realisee/__init__.py`** — argparse CLI (`main`) plus `compute_qs`, the only place the
  adapters are constructed and the stages are sequenced.

### Data flow

0. (optional, `--preparation`) Per day, `prepare_offre_realisee` reads
   `input_brute/offre_realisee_brute_<YYYY-MM-DD>.parquet`, runs `transform_offre_realisee_brute`, and
   writes `input/offre_realisee.parquet/JOUR=<YYYY-MM-DD>/part-<YYYYMMDD>.parquet` — the `JOUR` column
   is dropped on write since the partition directory carries it. Deterministic file name, so re-running
   a day overwrites its own output instead of duplicating rows.
1. Per day, `LocalFileSystemHandler.get_daily_offre_realisee` reads the parquet with a pushdown
   filter on `JOUR` (plus optional `DSP` / `LIGNE`), selecting only the needed columns.
2. The usecase drops stops with no real-time data, then either writes an `*_error.csv` via
   `save_error_mesure_qs` (when `HEURE_THEORIQUE` is all-NaN, or `SENS`/`ARRET` has NaN) or computes
   stats in the entity layer and writes
   `output/<dsp>/<mesure_type>/mesure_<type>_<YYYY_MM_DD>.csv`.
3. `aggregate_mesure_qs` reads those daily CSVs back, buckets dates into periods via
   `domain/entities/aggregation/` (school holidays, summer window, excluded exceptional days), sums
   counts/scores per `LIGNE`, recomputes `TAUX_DE_CONFORMITE` / `TAUX_ABSENCE_DE_DONNEES`, and writes
   `output/<dsp>/<aggregation_level>/<mesure_type>/mesure_<type>_<suffix>.csv`.

Daily mesures are therefore an on-disk contract between the two stages: changing mesure output
columns breaks aggregation unless both `column_order` and `column_order_agregated` are updated.

## Testing conventions

`tests/test_unit/` mirrors `offre_realisee/domain/entities/`; `tests/test_integration/domain/usecases/`
drives real usecases against fixture parquet in `tests/test_data/input/` and compares with
`pd.testing.assert_frame_equal` against `tests/test_data/expected_data/`. Integration tests build a
real `LocalFileSystemHandler` pointed at `TEST_DATA_PATH` and use a `file_system_fixture` that
`shutil.rmtree`s the output dir on teardown. Tests follow a `# Given / # When / # Assert` layout.

Changing scoring logic changes the expected CSVs — regenerate them deliberately and review the diff,
don't overwrite blindly.

## Known gotchas

- `compute_qs` used to call `create_mesure_qs_*_date_range(file_system_handler, date_range, n_thread)`
  positionally, so `--n-thread` landed in the `dsp` parameter and the `DSP` pushdown filter crashed
  the whole CLI (`TypeError: 'int' object is not iterable`). Fixed — all stage calls in `compute_qs`
  now use keyword arguments. Keep it that way: the usecases take `(file_system_handler, date_range,
  dsp, ligne, metadata_cols, n_thread)`.
- Top-level `config/__init__.py` is an empty, unused stray package — unrelated to
  `offre_realisee/config/`. Don't import from it.
- `build/`, `0_documentation/html/`, `0_documentation/doctrees/` and
  `idfm_qualite_de_service_calculateur.egg-info/` are committed build artifacts, not source.
- Version lives in `pyproject.toml` (`version = "1.12.2"`); releases are driven by `v*` git tags.
