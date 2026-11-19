VENV = .venv
BIN = ${VENV}/bin
PYTHON = ${BIN}/python3
PIP = ${BIN}/pip
FLAKE = ${BIN}/flake8 .
MYPY = ${BIN}/mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
MYPY_STRICT = ${BIN}/mypy . --strict

MAIN = main.py
MAP = map.txt
REQ = requirements.txt
INSTALLED = .installed

all: run

run: install
	${PYTHON} ${MAIN} ${MAP}

install: ${INSTALLED}

${INSTALLED}: ${REQ}
	python3 -m venv ${VENV}
	${PIP} install --upgrade pip
	${PIP} install -r ${REQ}
	touch ${INSTALLED}

lint: ${INSTALLED}
	${FLAKE}
	${MYPY}

lint-strict: ${INSTALLED}
	${FLAKE}
	${MYPY_STRICT}

clean:
	rm -rf ${INSTALLED} ${VENV}
	rm -rf *.egg-info
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -rf {} +

.PHONY: all run install lint lint-strict clean
