.phony: Static validation
static-validation:
	flake8 .
	vulture . --ignore-names "mytimer,return_value,*_fixture" --exclude=".venv,venv,source"
	safety check -r requirements.txt
	safety check -r requirements_dev.txt
	bandit .

.phony: test
test:
	python3 -m pytest

.phony: yaml validation
yaml-validation:
	yamllint *.yml .ci_templates/*.yml

.phony: build wheel
build-wheel:
	python -m build --wheel

.phony: generate documentation
generate-documentation:
	sphinx-build -M html ./source ./0_documentation