.PHONY: dev-up dev-down dev-logs dev-migrate

# Convenience targets for local Docker Compose workflows.

dev-up:
	docker compose up --build -d

dev-down:
	docker compose down

dev-logs:
	docker compose logs -f --tail=200

# Optional: only needed if you bypass the backend entrypoint or want migrations without restart.
dev-migrate:
	docker compose exec backend alembic upgrade head
