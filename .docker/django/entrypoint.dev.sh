#!/bin/bash
# =============================================================================
# XYZ Studio - Entrypoint para Desarrollo
# =============================================================================
# Versión simplificada del entrypoint para desarrollo local
# Ejecuta el proceso como el usuario del host (evita archivos como root)
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_debug() { echo -e "${CYAN}[DEBUG]${NC} $1"; }

# =============================================================================
# Manejo de permisos: ejecutar como usuario del host
# =============================================================================
# Si estamos corriendo como root y tenemos HOST_UID definido,
# cambiar al usuario del host para que los archivos creados le pertenezcan
if [ "$(id -u)" = "0" ] && [ -n "${HOST_UID}" ] && [ "${HOST_UID}" != "0" ]; then
    log_info "Ejecutando como usuario del host (UID=${HOST_UID}, GID=${HOST_GID})"
    
    # Asegurar que el usuario existe y tiene los permisos correctos
    if id "${APP_USER}" &>/dev/null; then
        # Ajustar ownership del directorio de trabajo si es necesario
        # (solo de archivos que son root, no recursivamente en todo)
        find /app -maxdepth 1 -user root -exec chown ${HOST_UID}:${HOST_GID} {} \; 2>/dev/null || true
        
        # Re-ejecutar este script como el usuario del host usando gosu
        exec gosu ${APP_USER} "$0" "$@"
    else
        log_warn "Usuario ${APP_USER} no encontrado, continuando como root"
    fi
fi

log_debug "Corriendo como: $(whoami) (UID=$(id -u), GID=$(id -g))"

# Esperar a PostgreSQL
if [ -n "$DATABASE_HOST" ] && [ -n "$DATABASE_PORT" ]; then
    log_info "Esperando a PostgreSQL..."
    while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT" 2>/dev/null; do
        log_warn "PostgreSQL no disponible, reintentando..."
        sleep 2
    done
    log_info "✓ PostgreSQL disponible!"
fi

# Esperar a Solr
if [ -n "$SOLR_HOST" ] && [ -n "$SOLR_PORT" ]; then
    log_info "Esperando a Solr..."
    while ! nc -z "$SOLR_HOST" "$SOLR_PORT" 2>/dev/null; do
        log_warn "Solr no disponible, reintentando..."
        sleep 2
    done
    log_info "✓ Solr disponible!"
fi

# Ejecutar migraciones si se solicita
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    log_info "Ejecutando migraciones..."
    python manage.py migrate --noinput
fi

# Ejecutar comando
log_info "Iniciando servidor de desarrollo..."
exec "$@"
