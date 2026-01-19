.PHONY: migrate miggen

migrate:
	alembic -c ./infrastructure/database/migrations/alembic.ini upgrade head

miggen:
	alembic -c ./infrastructure/database/migrations/alembic.ini revision --autogenerate -m "$(msg)"
