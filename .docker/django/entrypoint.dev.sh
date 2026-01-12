#!/bin/bash
# =============================================================================
# XYZ Studio - Entrypoint para Desarrollo
# =============================================================================
# Versión simplificada del entrypoint para desarrollo local
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

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
