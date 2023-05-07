COMPOSE_PROFILES ?= development
CATASTRO_DATA ?= $(shell [ "$$COMPOSE_PROFILES" = "production" ] && echo /var/catastro || echo ./data)

.PHONY: help
help:  ## Muestra esta ayuda
	@echo "Please use \`make <target>\` where <target> is one of"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: prueba
prueba:
	@echo $(CATASTRO_DATA)

.PHONY: install
install:  ## Crea las carpetas de datos
	@mkdir -p "$(CATASTRO_DATA)/update" && \
	 mkdir -p "$(CATASTRO_DATA)/dist" && \
	 chown -R 1000:1000 "$(CATASTRO_DATA)/update"
	@$(shell [ ! -f .env.development.local ] && cp env.development.local.tpl .env.development.local)
	@$(shell [ ! -f .env.production.local ] && cp  env.production.local.tpl .env.production.local)
	@$(shell [ ! -f frontend/.env.local ] && cp frontend/.env frontend/.env.local)

.PHONY: build
build:  ## Construir imágenes
	@docker pull egofer/catatom2osm
	@docker-compose build
	@npm install --prefix frontend

.PHONY: up
up: build  ## Inicia servicios
	@if [ "$(COMPOSE_PROFILES)" = "production" ]; then \
		docker-compose -f docker-compose.yaml up -d; \
	else \
		docker-compose up -d; \
	fi

.PHONY: logs
logs:  ## Muestra los registros
	@docker-compose logs -f

.PHONY: down
down:  ## Finaliza los servicios
	@docker-compose down  --remove-orphans
