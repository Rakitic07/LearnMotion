PY ?= .venv/bin/python
PORT ?= 5050

.PHONY: setup run test cluster cluster-full teardown

setup:
	python3 -m venv .venv
	$(PY) -m pip install -q -r requirements.txt

run:
	PORT=$(PORT) $(PY) run.py

test:
	$(PY) -m pytest -q

cluster:
	bash scripts/setup_cluster.sh

cluster-full:
	bash scripts/setup_cluster.sh --with-ingress --with-vpa

teardown:
	bash scripts/teardown.sh
