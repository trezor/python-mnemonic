PYTHON=python3
POETRY=poetry

EXCLUDES=.vscode

STYLE_TARGETS=src tests tools

all: build

build:
	$(POETRY) build

install:
	$(POETRY) install

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

git-clean:
	git clean -dfx -e $(EXCLUDES)

style:
	black $(STYLE_TARGETS)
	isort $(STYLE_TARGETS)
	make style_check

style_check:
	black --check $(STYLE_TARGETS)
	flake8 $(STYLE_TARGETS)
	pyright $(STYLE_TARGETS)

.PHONY: all build install clean style style_check git-clean clean-build clean-pyc clean-test
