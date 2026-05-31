ALEMBIC = alembic -c core/db/alembic.ini

.PHONY: migrate upgrade downgrade history run test test-cov \
        migrate-staging upgrade-staging downgrade-staging \
        docker-up docker-down docker-build docker-logs docker-shell

# ── Development (DATABASE_URL) ────────────────────────────────────────────────

migrate:
	$(ALEMBIC) revision --autogenerate -m "$(msg)"

upgrade:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1

history:
	$(ALEMBIC) history --verbose

run:
	uvicorn main:app --reload

# ── Staging (STAGING_DATABASE_URL) ───────────────────────────────────────────

migrate-staging:
	bash -c 'set -a && source .env && set +a && DATABASE_URL=$$STAGING_DATABASE_URL $(ALEMBIC) revision --autogenerate -m "$(msg)"'

upgrade-staging:
	bash -c 'set -a && source .env && set +a && DATABASE_URL=$$STAGING_DATABASE_URL $(ALEMBIC) upgrade head'

downgrade-staging:
	bash -c 'set -a && source .env && set +a && DATABASE_URL=$$STAGING_DATABASE_URL $(ALEMBIC) downgrade -1'

# ── Tests ─────────────────────────────────────────────────────────────────────

test:
	pytest -v

test-cov:
	pytest -v --cov=modules --cov=core --cov-report=term-missing

# ── Docker ────────────────────────────────────────────────────────────────────

docker-build:
	docker compose build

docker-up:
	docker compose up

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f backend

docker-shell:
	docker compose exec backend sh
