# =============================================================================
# XYZ Studio - Makefile
# =============================================================================
# Comandos útiles para desarrollo y despliegue con Docker
# =============================================================================

.PHONY: help dev build up down logs shell migrate test clean prod-build prod-up

# Colores
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help: ## Muestra esta ayuda
	@echo ""
	@echo "$(CYAN)XYZ Studio - Comandos disponibles:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# DESARROLLO LOCAL CON DOCKER
# =============================================================================

dev: ## Inicia todos los servicios en modo desarrollo (con watch)
	docker compose up --build

dev-d: ## Inicia servicios en background
	docker compose up -d --build

watch: ## Inicia con Docker Compose Watch (hot-reload mejorado)
	docker compose watch

up: ## Inicia los servicios (sin rebuild)
	docker compose up

down: ## Detiene todos los servicios
	docker compose down

down-v: ## Detiene servicios Y elimina volúmenes (⚠️ BORRA DATOS)
	docker compose down -v

restart: ## Reinicia todos los servicios
	docker compose restart

logs: ## Muestra logs de todos los servicios
	docker compose logs -f

logs-web: ## Muestra logs solo de Django
	docker compose logs -f web

logs-tailwind: ## Muestra logs del watcher de Tailwind
	docker compose logs -f tailwind

# =============================================================================
# DJANGO COMMANDS (dentro del contenedor)
# =============================================================================
# Usamos -u devuser para que los archivos creados pertenezcan al usuario del host
DOCKER_EXEC = docker compose exec -u devuser web

shell: ## Abre shell de Django
	$(DOCKER_EXEC) python manage.py shell

bash: ## Abre bash en el contenedor web (como devuser)
	$(DOCKER_EXEC) bash

bash-root: ## Abre bash en el contenedor web (como root)
	docker compose exec web bash

migrate: ## Ejecuta migraciones de Django
	$(DOCKER_EXEC) python manage.py migrate

makemigrations: ## Crea nuevas migraciones
	$(DOCKER_EXEC) python manage.py makemigrations

createsuperuser: ## Crea un superusuario
	$(DOCKER_EXEC) python manage.py createsuperuser

collectstatic: ## Recolecta archivos estáticos
	$(DOCKER_EXEC) python manage.py collectstatic --noinput

rebuild-index: ## Reconstruye índice de búsqueda (Haystack/Solr)
	$(DOCKER_EXEC) python manage.py rebuild_index --noinput

update-index: ## Actualiza índice de búsqueda
	$(DOCKER_EXEC) python manage.py update_index

startapp: ## Crea una nueva app Django (uso: make startapp APP=nombre)
	@mkdir -p apps/$(APP)
	$(DOCKER_EXEC) python manage.py startapp $(APP) apps/$(APP)

# =============================================================================
# TESTING
# =============================================================================

test: ## Ejecuta tests
	$(DOCKER_EXEC) python manage.py test

lint: ## Ejecuta linting con pylint
	$(DOCKER_EXEC) pylint apps/ --load-plugins pylint_django

# =============================================================================
# DATABASE
# =============================================================================

db-shell: ## Abre psql en PostgreSQL
	docker compose exec db psql -U xyz_user -d xyz_studio

db-backup: ## Crea backup de la base de datos
	@mkdir -p backups
	docker compose exec db pg_dump -U xyz_user xyz_studio > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup creado en backups/$(RESET)"

db-restore: ## Restaura backup (usa: make db-restore FILE=backups/backup.sql)
	docker compose exec -T db psql -U xyz_user -d xyz_studio < $(FILE)

# =============================================================================
# SOLR
# =============================================================================

solr-status: ## Verifica estado del core de Solr
	curl -s "http://localhost:8983/solr/admin/cores?action=STATUS&core=xyz_core" | python -m json.tool

# =============================================================================
# PRODUCCIÓN (SIMULACIÓN LOCAL)
# =============================================================================

prod-build: ## Construye imagen de producción
	docker compose -f docker-compose.yml build web

prod-up: ## Inicia stack de producción local (requiere BD y Solr externos)
	docker compose -f docker-compose.prod.yml up --build

prod-down: ## Detiene stack de producción
	docker compose -f docker-compose.prod.yml down

# =============================================================================
# LIMPIEZA
# =============================================================================

clean: ## Elimina contenedores, imágenes huérfanas y caché
	docker compose down --rmi local --remove-orphans
	docker system prune -f

clean-all: ## Limpieza profunda (⚠️ ELIMINA TODO incluyendo volúmenes)
	docker compose down -v --rmi all --remove-orphans
	docker system prune -af --volumes

# =============================================================================
# CI/CD
# =============================================================================

build-push: ## Construye y sube imagen a registry (ajustar REGISTRY)
	@echo "$(YELLOW)Construyendo imagen...$(RESET)"
	docker build -f .docker/django/Dockerfile -t xyz-studio/django:$(TAG) .
	@echo "$(YELLOW)Subiendo a registry...$(RESET)"
	docker push xyz-studio/django:$(TAG)
	@echo "$(GREEN)¡Listo!$(RESET)"
