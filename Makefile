
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
export GEOSERVER_URL

PROXY_PREFIX ?=
export PROXY_PREFIX

# End of customisable environment variables

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
		docker-build-front-server \
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
	docker-compose up -d app-tools
	docker-compose exec -T --user=$(shell id -u) app-tools black /app/

.PHONY: check
check: ## Check the code with black and prospector
check:
	docker-compose up -d app-tools
	docker-compose exec -T --user=$(shell id -u) app-tools black --check /app/
	docker-compose exec -T --user=$(shell id -u) app-tools prospector /app/

.PHONY: test
test: ## Run tests
test:
	docker-compose up -d db_tests app-tools
	docker-compose exec -T --user=$(shell id -u) app-tools pytest -vv --color=yes /app/tests

.PHONY: docs
docs: ## Build documentation
	docker-compose up -d app-tools
	docker-compose exec -T --user=$(shell id -u) app-tools make -C docs html

.PHONY: front-test
front-test: ## Run front tests
front-test:
	docker-compose up -d front-server
	docker-compose exec -T --user=$(shell id -u) front-server npm run test

.PHONY: front-format
front-format: ## Run front formating
front-format:
	docker-compose up -d front-server
	docker-compose exec -T --user=$(shell id -u) front-server npm run format

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
bash: ## Open bash in app-tools container
bash:
	docker-compose up -d app-tools
	docker-compose exec --user=$(shell id -u) app-tools bash

.PHONY: psql
psql: ## Launch psql in db container
psql:
	docker-compose up -d db
	docker-compose exec db psql -U drealcorse -d drealcorse

.PHONY: pshell
pshell: ## Launch pshell in app container
pshell:
	docker-compose run --rm app pshell c2c://drealcorsereports.ini


# Docker images

.PHONY: docker-build-db
docker-build-db:
	docker build -t ${DOCKER_BASE}-db:${DOCKER_TAG} db

.PHONY: docker-build-front-server
docker-build-front-server:
	docker build --target=front-server -t ${DOCKER_BASE}-front-server:${DOCKER_TAG} app

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

# make local valid certs
# mkcert need to be init first !! (must done once only)
.PHONY: cert
.ONESHELL:
cert:
	cd resources/ssl
	mkcert georchestra.mydomain.org
	cp georchestra.mydomain.org.pem georchestra.mydomain.org.crt
	cp georchestra.mydomain.org-key.pem georchestra.mydomain.org.key

