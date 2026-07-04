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
	@echo "Perl agent tests: see agent-perl/t (run 'prove -l agent-perl/t' once agent-perl is implemented)."

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
	@echo "Backend API not implemented yet in this iteration (see ROADMAP.md)."

run-worker:
	@echo "Worker not implemented yet in this iteration (core edition has no Celery/RQ, see ROADMAP.md)."

scan-demo:
	@echo "demo-legacy-app fixtures are not implemented yet. In the meantime, run: aegis scan <path-to-any-legacy-project>"

report-demo:
	@echo "HTML report generation not implemented yet in this iteration (see ROADMAP.md)."

docker-up:
	@echo "No docker-compose.yml in the core edition (no Postgres/Redis/Celery, see ROADMAP.md)."

docker-down:
	@echo "No docker-compose.yml in the core edition (no Postgres/Redis/Celery, see ROADMAP.md)."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
