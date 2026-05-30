ALEMBIC = alembic -c core/db/alembic.ini

.PHONY: migrate upgrade downgrade history run

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
