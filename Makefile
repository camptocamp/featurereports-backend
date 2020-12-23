
# Customisable environment variables

DEVELOPMENT = TRUE
export DEVELOPMENT

DOCKER_BASE ?= camptocamp/drealcorse-reports
DOCKER_TAG ?= latest
DOCKER_PORT ?= 8080
export DOCKER_BASE
export DOCKER_TAG
export DOCKER_PORT

PGHOST ?= db
PGHOST_SLAVE ?= db
PGPORT ?= 5432
PGDATABASE ?= drealcorse
PGUSER ?= drealcorse
PGPASSWORD ?= drealcorse
export PGHOST
export PGHOST_SLAVE
export PGPORT
export PGDATABASE
export PGUSER
export PGPASSWORD

PROXY_PREFIX ?=
export PROXY_PREFIX

# End of customisable environment variables

COMMON_DOCKER_RUN_OPTIONS ?= \
	--name="drealcorse-reports-tools" \
	--volume="${PWD}/app:/app" \
	--user=$(shell id -u) \
	${DOCKER_BASE}-app-tools:${DOCKER_TAG}

# DOCKER_MAKE_CMD = docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} make -f $(firstword $(MAKEFILE_LIST))

default: help

.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@grep -Eh '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    %-20s%s\n", $$1, $$2}'

.PHONY: meacoffee
meacoffee: ## Build, run and show logs
meacoffee: up
	make initdb
	docker-compose logs -f app

.PHONY: up
up: ## docker-compose up
up: build
	docker-compose rm --stop --force app
	docker-compose up -d

.PHONY: build
build: ## Build runtime files and docker images
build: \
		docker-build-db \
		docker-build-app-tools \
		docker-build-app \
		docker-compose-env

.PHONY: docker-compose-env
docker-compose-env: ## Build docker-compose environment file
	cat ".env.tmpl" | sed "/^#/d" | envsubst > ".env"

.PHONY: initdb
initdb:
	docker-compose exec app alembic upgrade head
	# docker-compose exec app setup_test_data c2c://development.ini#app

.PHONY: black
black:
black: ## Format Python code with black
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} black /app/drealcorsereports setup.py

.PHONY: check
check: ## Check the code with black and flake8
check:
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} black --check /app/drealcorsereports setup.py || ( \
		echo 'Please run "make black" to format your Python code' && \
		false \
	)
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} prospector /app/drealcorsereports

.PHONY: test
test: ## Run tests
test:
	docker-compose up -d db_tests
	docker-compose run --rm test

.PHONY: docs
docs: ## Build documentation
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} make -C docs html

.PHONY: cleanall
cleanall: ## Clean everything including docker containers and images
cleanall: clean
	docker-compose down --remove-orphans
	rm -f .env
	docker rmi \
		${DOCKER_BASE}-postgresql:${DOCKER_TAG} \
		${DOCKER_BASE}-build:${DOCKER_TAG} \
		${DOCKER_BASE}-app:${DOCKER_TAG} || true

# Development tools

.PHONY: bash
bash: ## Open bash in build container
bash: docker-build-build
	docker run --rm -ti ${COMMON_DOCKER_RUN_OPTIONS} bash

.PHONY: psql
psql: ## Launch psql in postgres image
psql:
	docker-compose exec -u postgres db psql -U drealcorse -d drealcorse

.PHONY: psqldocs
psqldocs: ## Launch psql in postgres image
psqldocs:
	docker-compose exec -u postgres db postgresql-autodoc reports

.PHONY: pshell
pshell: ## Launch getitfixed pshell
pshell:
	docker-compose run --rm app pshell c2c://development.ini


# Docker images

.PHONY: docker-build-db
docker-build-db:
	docker build -t ${DOCKER_BASE}-db:${DOCKER_TAG} db

.PHONY: docker-build-app-tools
docker-build-app-tools:
	docker build --target=tools -t ${DOCKER_BASE}-app-tools:${DOCKER_TAG} app

.PHONY: docker-build-app
docker-build-app:
	docker build --target=app -t ${DOCKER_BASE}-app:${DOCKER_TAG} app

.PHONY: docker-push
docker-push: ## Push docker images on docker hub
	docker push ${DOCKER_BASE}-app:${DOCKER_TAG}

.PHONY: docker-pull
docker-pull: ## Pull docker images from docker hub
	docker pull ${DOCKER_BASE}-app:${DOCKER_TAG}