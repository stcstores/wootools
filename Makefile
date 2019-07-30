.PHONY: docs

init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

reinit:
	pipenv --rm
	make init

test:
	pipenv run pytest

lock:
	pipenv lock -d
