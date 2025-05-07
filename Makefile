DOCKER_COMPOSE = docker compose -f infrastructure/compose/docker-compose.yml

.PHONY: build up down logs restart

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

restart: down up

restart: down up