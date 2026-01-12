#!/bin/bash
# =============================================================================
# XYZ Studio - Django Oscar E-commerce
# Entrypoint Script
# =============================================================================
# Este script:
#   1. Espera a que PostgreSQL esté disponible
#   2. Espera a que Solr esté disponible (opcional)
#   3. Ejecuta migraciones de base de datos
#   4. Recolecta archivos estáticos
#   5. Reconstruye índice de búsqueda (opcional)
#   6. Inicia la aplicación
# =============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# -----------------------------------------------------------------------------
# Función: Esperar a que un servicio esté disponible
# -----------------------------------------------------------------------------
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=${4:-30}
    local attempt=1

    log_info "Esperando a que ${service_name} esté disponible en ${host}:${port}..."

    while ! nc -z "$host" "$port" > /dev/null 2>&1; do
        if [ $attempt -ge $max_attempts ]; then
            log_error "${service_name} no está disponible después de ${max_attempts} intentos. Abortando."
            exit 1
        fi
        log_warn "Intento ${attempt}/${max_attempts}: ${service_name} no disponible. Reintentando en 2s..."
        sleep 2
        attempt=$((attempt + 1))
    done

    log_info "✓ ${service_name} está disponible!"
}

# -----------------------------------------------------------------------------
# Esperar a PostgreSQL
# -----------------------------------------------------------------------------
if [ -n "$DATABASE_HOST" ] && [ -n "$DATABASE_PORT" ]; then
    wait_for_service "$DATABASE_HOST" "$DATABASE_PORT" "PostgreSQL" 60
elif [ -n "$DATABASE_URL" ]; then
    # Extraer host y puerto de DATABASE_URL
    # Formato: postgres://user:pass@host:port/dbname
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
        wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL" 60
    fi
fi

# -----------------------------------------------------------------------------
# Esperar a Solr (Opcional)
# -----------------------------------------------------------------------------
if [ -n "$SOLR_HOST" ] && [ -n "$SOLR_PORT" ]; then
    wait_for_service "$SOLR_HOST" "$SOLR_PORT" "Solr" 30
elif [ -n "$SOLR_URL" ]; then
    # Extraer host y puerto de SOLR_URL
    # Formato: http://host:port/solr/core
    SOLR_HOST_EXTRACTED=$(echo "$SOLR_URL" | sed -n 's|http://\([^:]*\):.*|\1|p')
    SOLR_PORT_EXTRACTED=$(echo "$SOLR_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    if [ -n "$SOLR_HOST_EXTRACTED" ] && [ -n "$SOLR_PORT_EXTRACTED" ]; then
        wait_for_service "$SOLR_HOST_EXTRACTED" "$SOLR_PORT_EXTRACTED" "Solr" 30
    fi
fi

# -----------------------------------------------------------------------------
# Ejecutar migraciones
# -----------------------------------------------------------------------------
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    log_info "Ejecutando migraciones de base de datos..."
    python manage.py migrate --noinput
    log_info "✓ Migraciones completadas!"
fi

# -----------------------------------------------------------------------------
# Recolectar archivos estáticos
# -----------------------------------------------------------------------------
if [ "${COLLECT_STATIC:-true}" = "true" ]; then
    log_info "Recolectando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
    log_info "✓ Archivos estáticos recolectados!"
fi

# -----------------------------------------------------------------------------
# Reconstruir índice de búsqueda (Haystack/Solr)
# -----------------------------------------------------------------------------
if [ "${REBUILD_INDEX:-false}" = "true" ]; then
    log_info "Reconstruyendo índice de búsqueda..."
    python manage.py rebuild_index --noinput || log_warn "No se pudo reconstruir el índice. Continuando..."
    log_info "✓ Índice de búsqueda reconstruido!"
fi

# -----------------------------------------------------------------------------
# Crear superusuario si se especifica (útil para desarrollo)
# -----------------------------------------------------------------------------
if [ "${CREATE_SUPERUSER:-false}" = "true" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    log_info "Creando superusuario..."
    python manage.py createsuperuser --noinput || log_warn "El superusuario ya existe o hubo un error."
fi

# -----------------------------------------------------------------------------
# Ejecutar comando principal
# -----------------------------------------------------------------------------
log_info "Iniciando aplicación..."
exec "$@"
