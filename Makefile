.PHONY: dev-build
dev-build:
	docker compose -f compose-dev.yml build

.PHONY: dev-up-d
dev-up-d:
	docker compose -f compose-dev.yml up -d

.PHONY: dev
dev:
	@make dev-build
	@make dev-up-d

.PHONY: down
down:
	docker compose -f compose-dev.yml down

.PHONY: bash
bash:
	docker compose -f compose-dev.yml exec django bash

.PHONY: logs
logs:
	docker compose -f compose-dev.yml logs

.PHONY: test
test:
	docker compose -f compose-dev.yml exec django python manage.py test

# Lintとフォーマット
.PHONY: black
black:
	docker compose -f compose-dev.yml exec django black .
	docker compose -f compose-dev.yml exec discord-bot black .

.PHONY: isort
isort:
	docker compose -f compose-dev.yml exec django isort .
	docker compose -f compose-dev.yml exec discord-bot isort .

.PHONY: flake8
flake8:
	docker compose -f compose-dev.yml exec django flake8 .
	docker compose -f compose-dev.yml exec discord-bot flake8 .

.PHONY: lint
lint:
	@make black
	@make isort
	@make flake8

.PHONY: prod-build
prod-build:
	docker compose -f compose-prod.yml build --no-cache

.PHONY: prod-up-d
prod-up-d:
	docker compose -f compose-prod.yml up -d

.PHONY: prod
prod:
	@make prod-build
	@make prod-up-d
