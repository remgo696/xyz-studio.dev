#!/usr/bin/env python
"""
XYZ Studio - Script de Migración SQLite → PostgreSQL
=====================================================
Este script realiza una migración segura de datos usando Django ORM.
Ejecutar desde el host con: python scripts/migrate_data.py

Maneja automáticamente:
- Conflictos de contenttypes y permissions
- Encoding UTF-8
- Orden de dependencias de modelos
- Natural keys para evitar conflictos de IDs
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Configuración de paths
BASE_DIR = Path(__file__).resolve().parent.parent
DUMP_DIR = BASE_DIR / "data_dumps"
SQLITE_DB = BASE_DIR / "db.sqlite3"

# Colores ANSI
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_step(step, total, text):
    print(f"{Colors.YELLOW}[{step}/{total}]{Colors.END} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def run_cmd(cmd, check=True):
    """Ejecuta un comando y retorna el resultado."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print_error(f"Error ejecutando: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result

def main():
    print_header("XYZ Studio - Migración SQLite → PostgreSQL")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    DUMP_DIR.mkdir(exist_ok=True)
    
    # =========================================================================
    # PASO 0: Verificaciones
    # =========================================================================
    print_step(0, 5, "Verificando requisitos...")
    
    if not SQLITE_DB.exists():
        print_error(f"No se encontró {SQLITE_DB}")
        sys.exit(1)
    print_success(f"SQLite encontrado: {SQLITE_DB}")
    
    # Verificar PostgreSQL
    result = run_cmd("docker exec xyz-db pg_isready -U xyz_user", check=False)
    if result.returncode != 0:
        print_error("PostgreSQL no está disponible. Ejecuta 'make dev' primero.")
        sys.exit(1)
    print_success("PostgreSQL disponible")
    
    # =========================================================================
    # PASO 1: Dump desde SQLite (ejecutando localmente con SQLite config)
    # =========================================================================
    print_step(1, 5, "Exportando datos desde SQLite...")
    
    dump_file = DUMP_DIR / f"sqlite_dump_{timestamp}.json"
    
    # Apps que Django crea automáticamente (excluir para evitar conflictos)
    exclude_apps = [
        "contenttypes",
        "auth.permission", 
        "sessions",
        "admin.logentry",
    ]
    exclude_args = " ".join([f"--exclude={app}" for app in exclude_apps])
    
    # Crear el dump usando SQLite (sin variables de Docker)
    # Necesitamos desactivar las variables de entorno de Docker temporalmente
    env_backup = {
        'DATABASE_URL': os.environ.pop('DATABASE_URL', None),
        'DATABASE_HOST': os.environ.pop('DATABASE_HOST', None),
    }
    
    try:
        # Ejecutar dumpdata apuntando a SQLite
        cmd = f'python manage.py dumpdata {exclude_args} --natural-foreign --natural-primary --indent=2 -o "{dump_file}"'
        print(f"  → Ejecutando: {cmd}")
        result = run_cmd(cmd)
        print_success(f"Dump creado: {dump_file}")
        
    finally:
        # Restaurar variables de entorno
        for key, value in env_backup.items():
            if value is not None:
                os.environ[key] = value
    
    # Verificar tamaño del dump
    dump_size = dump_file.stat().st_size / 1024  # KB
    print(f"  → Tamaño del dump: {dump_size:.1f} KB")
    
    # =========================================================================
    # PASO 2: Verificar integridad del JSON
    # =========================================================================
    print_step(2, 5, "Verificando integridad del dump...")
    
    with open(dump_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            record_count = len(data)
            print_success(f"JSON válido: {record_count} registros")
        except json.JSONDecodeError as e:
            print_error(f"JSON inválido: {e}")
            sys.exit(1)
    
    # Mostrar resumen por modelo
    models_count = {}
    for record in data:
        model = record.get('model', 'unknown')
        models_count[model] = models_count.get(model, 0) + 1
    
    print("\n  Registros por modelo:")
    for model, count in sorted(models_count.items()):
        print(f"    → {model}: {count}")
    
    # =========================================================================
    # PASO 3: Limpiar PostgreSQL
    # =========================================================================
    print_step(3, 5, "Limpiando PostgreSQL (flush)...")
    
    run_cmd("docker exec xyz-web-dev python manage.py flush --no-input")
    print_success("PostgreSQL limpiado")
    
    # =========================================================================
    # PASO 4: Cargar datos en PostgreSQL
    # =========================================================================
    print_step(4, 5, "Importando datos a PostgreSQL...")
    
    # Copiar dump al contenedor
    run_cmd(f'docker cp "{dump_file}" xyz-web-dev:/tmp/data_dump.json')
    
    # Cargar datos
    result = run_cmd("docker exec xyz-web-dev python manage.py loaddata /tmp/data_dump.json", check=False)
    
    if result.returncode != 0:
        print_error("Error durante la carga de datos:")
        print(result.stderr)
        
        # Intentar carga individual por app si falla
        print("\n  → Intentando carga por aplicación...")
        # Crear dumps individuales por app crítica
        critical_apps = ['auth.user', 'catalogue', 'partner', 'basket', 'order']
        for app in critical_apps:
            app_dump = DUMP_DIR / f"{app.replace('.', '_')}_{timestamp}.json"
            cmd = f'python manage.py dumpdata {app} --natural-foreign --natural-primary --indent=2 -o "{app_dump}"'
            run_cmd(cmd, check=False)
            if app_dump.exists():
                run_cmd(f'docker cp "{app_dump}" xyz-web-dev:/tmp/{app.replace(".", "_")}_dump.json')
                run_cmd(f'docker exec xyz-web-dev python manage.py loaddata /tmp/{app.replace(".", "_")}_dump.json', check=False)
    else:
        print_success("Datos importados exitosamente")
    
    # Limpiar temporal
    run_cmd("docker exec xyz-web-dev rm -f /tmp/data_dump.json", check=False)
    
    # =========================================================================
    # PASO 5: Verificación
    # =========================================================================
    print_step(5, 5, "Verificando migración...")
    
    verification_script = '''
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model

User = get_user_model()
Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")
Partner = get_model("partner", "Partner")
Order = get_model("order", "Order")

print(f"Usuarios:   {User.objects.count()}")
print(f"Productos:  {Product.objects.count()}")
print(f"Categorías: {Category.objects.count()}")
print(f"Partners:   {Partner.objects.count()}")
print(f"Órdenes:    {Order.objects.count()}")
'''
    
    result = run_cmd(f'docker exec xyz-web-dev python manage.py shell -c "{verification_script}"')
    print(f"\n{Colors.BLUE}Estadísticas en PostgreSQL:{Colors.END}")
    for line in result.stdout.strip().split('\n'):
        print(f"  → {line}")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_header("✓ MIGRACIÓN COMPLETADA")
    print(f"Backup guardado en: {dump_file}")
    print(f"\n{Colors.YELLOW}Notas:{Colors.END}")
    print("  • Los usuarios conservan sus contraseñas")
    print("  • Las sesiones se reiniciaron (normal)")
    print("  • Verifica el sitio en http://localhost:8000")

if __name__ == "__main__":
    os.chdir(BASE_DIR)
    main()
