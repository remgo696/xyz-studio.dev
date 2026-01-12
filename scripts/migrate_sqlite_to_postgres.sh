#!/bin/bash
# =============================================================================
# XYZ Studio - Migración SQLite → PostgreSQL
# =============================================================================
# Este script transfiere todos los datos de db.sqlite3 a PostgreSQL usando
# Django's dumpdata/loaddata para evitar incompatibilidades SQL.
#
# Uso: ./scripts/migrate_sqlite_to_postgres.sh
# =============================================================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     XYZ Studio - Migración SQLite → PostgreSQL                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
SQLITE_DB="db.sqlite3"
DUMP_DIR="./data_dumps"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Crear directorio para dumps
mkdir -p "$DUMP_DIR"

# -----------------------------------------------------------------------------
# PASO 0: Verificaciones previas
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[0/5]${NC} Verificando requisitos..."

if [ ! -f "$SQLITE_DB" ]; then
    echo -e "${RED}ERROR: No se encontró $SQLITE_DB${NC}"
    exit 1
fi

# Verificar que PostgreSQL está corriendo
if ! docker exec xyz-db pg_isready -U xyz_user > /dev/null 2>&1; then
    echo -e "${RED}ERROR: PostgreSQL no está disponible. Ejecuta 'make dev' primero.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ SQLite encontrado: $SQLITE_DB${NC}"
echo -e "${GREEN}✓ PostgreSQL disponible${NC}"

# -----------------------------------------------------------------------------
# PASO 1: Dump desde SQLite (usando settings temporales)
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/5]${NC} Exportando datos desde SQLite..."

# Crear archivo de settings temporal para SQLite
cat > /tmp/sqlite_settings.py << 'EOF'
from website.settings import *

# Override solo la base de datos a SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
EOF

# Apps a excluir (Django las crea automáticamente con migrate)
EXCLUDE_APPS="--exclude=contenttypes --exclude=auth.permission --exclude=sessions --exclude=admin.logentry"

# Dump con natural keys para evitar conflictos de IDs
echo "  → Exportando datos principales..."
DJANGO_SETTINGS_MODULE=tmp.sqlite_settings python manage.py dumpdata \
    $EXCLUDE_APPS \
    --natural-foreign \
    --natural-primary \
    --indent=2 \
    -o "$DUMP_DIR/full_dump_${TIMESTAMP}.json" 2>/dev/null || {
    
    # Si falla el método de settings, usar approach alternativo
    echo "  → Usando método alternativo (DATABASE_URL vacío)..."
    
    # Dump directo modificando temporalmente el entorno
    unset DATABASE_URL
    unset DATABASE_HOST
    python manage.py dumpdata \
        $EXCLUDE_APPS \
        --natural-foreign \
        --natural-primary \
        --indent=2 \
        -o "$DUMP_DIR/full_dump_${TIMESTAMP}.json"
}

# Verificar que el dump se creó
if [ ! -f "$DUMP_DIR/full_dump_${TIMESTAMP}.json" ]; then
    echo -e "${RED}ERROR: No se pudo crear el dump${NC}"
    exit 1
fi

DUMP_SIZE=$(du -h "$DUMP_DIR/full_dump_${TIMESTAMP}.json" | cut -f1)
echo -e "${GREEN}✓ Dump creado: $DUMP_DIR/full_dump_${TIMESTAMP}.json ($DUMP_SIZE)${NC}"

# -----------------------------------------------------------------------------
# PASO 2: Limpiar PostgreSQL (mantener estructura, eliminar datos)
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/5]${NC} Limpiando datos en PostgreSQL..."

# Usar flush con --no-input para limpiar datos (mantiene tablas)
docker exec xyz-web-dev python manage.py flush --no-input

echo -e "${GREEN}✓ PostgreSQL limpiado${NC}"

# -----------------------------------------------------------------------------
# PASO 3: Copiar dump al contenedor
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/5]${NC} Copiando dump al contenedor..."

docker cp "$DUMP_DIR/full_dump_${TIMESTAMP}.json" xyz-web-dev:/tmp/data_dump.json
echo -e "${GREEN}✓ Dump copiado al contenedor${NC}"

# -----------------------------------------------------------------------------
# PASO 4: Cargar datos en PostgreSQL
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/5]${NC} Importando datos a PostgreSQL..."

# Cargar datos con manejo de errores
docker exec xyz-web-dev python manage.py loaddata /tmp/data_dump.json

echo -e "${GREEN}✓ Datos importados exitosamente${NC}"

# -----------------------------------------------------------------------------
# PASO 5: Verificación final
# -----------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/5]${NC} Verificando migración..."

# Contar registros en tablas principales
echo -e "\n${BLUE}Estadísticas de la migración:${NC}"
docker exec xyz-web-dev python manage.py shell -c "
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model

User = get_user_model()
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Partner = get_model('partner', 'Partner')
Order = get_model('order', 'Order')

print(f'  → Usuarios:    {User.objects.count()}')
print(f'  → Productos:   {Product.objects.count()}')
print(f'  → Categorías:  {Category.objects.count()}')
print(f'  → Partners:    {Partner.objects.count()}')
print(f'  → Órdenes:     {Order.objects.count()}')
"

# Limpiar archivo temporal del contenedor
docker exec xyz-web-dev rm -f /tmp/data_dump.json

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✓ MIGRACIÓN COMPLETADA EXITOSAMENTE                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo -e "\n${BLUE}Backup guardado en:${NC} $DUMP_DIR/full_dump_${TIMESTAMP}.json"
echo -e "${YELLOW}Nota:${NC} El superusuario existe, usa las mismas credenciales de antes."
