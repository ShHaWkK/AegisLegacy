.PHONY: install install-dev test test-python test-perl lint typecheck security \
        format run-api run-worker scan-demo report-demo docker-up docker-down clean

install:
	pip install -e "backend"
	pip install -e "cli"

install-dev:
	pip install -e "backend[dev,api]"
	pip install -e "cli[dev]"

test: test-python test-perl

test-python:
	pytest backend/tests
	pytest cli/tests

test-perl:
	cd agent-perl && for f in t/*.t; do perl "$$f" || exit 1; done

lint:
	cd backend && ruff check .
	cd cli && ruff check .

format:
	cd backend && ruff format .
	cd cli && ruff format .

typecheck:
	cd backend && mypy app
	cd cli && mypy aegislegacy

security:
	cd backend && bandit -r app -q
	cd backend && pip-audit

run-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	@echo "Le worker n'est pas encore implémenté dans cette itération (l'édition core n'inclut pas Celery/RQ, voir ROADMAP.md)."

scan-demo:
	aegis scan demo-legacy-app

report-demo:
	@echo "HTML report generation not implemented yet in this iteration (see ROADMAP.md)."

docker-up:
	@echo "Aucun docker-compose.yml dans l'édition core (pas de Postgres/Redis/Celery, voir ROADMAP.md)."

docker-down:
	@echo "Aucun docker-compose.yml dans l'édition core (pas de Postgres/Redis/Celery, voir ROADMAP.md)."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
