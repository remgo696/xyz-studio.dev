# 🐳 XYZ Studio - Docker Setup

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DEVELOPMENT                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐          │
│  │  Django │◄──►│ Postgres│    │  Solr   │    │  Tailwind   │          │
│  │  :8000  │    │  :5432  │    │  :8983  │    │  (watcher)  │          │
│  └─────────┘    └─────────┘    └─────────┘    └─────────────┘          │
│       ▲              ▲              ▲               │                   │
│       └──────────────┴──────────────┴───────────────┘                   │
│                    Docker Network                                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐                                             │
│  │  Nginx  │◄──►│  Django │──────►  AWS RDS (PostgreSQL)                │
│  │   :80   │    │ Gunicorn│──────►  EC2 (Solr 6.6.6)                    │
│  └─────────┘    └─────────┘                                             │
│       │                                                                  │
│       ▼                                                                  │
│  Static Files (WhiteNoise/S3)                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start (Desarrollo)

### 1. Clonar y configurar entorno

```bash
# Clonar repositorio
git clone <repo-url> xyz-studio
cd xyz-studio

# Copiar configuración de Docker
cp .env.docker.example .env.docker

# Editar credenciales (cambiar passwords)
nano .env.docker
```

### 2. Iniciar servicios

```bash
# Opción 1: Con Makefile (recomendado)
make dev

# Opción 2: Docker Compose directo
docker compose up --build

# Opción 3: Con Watch (hot-reload mejorado, Docker Compose v2.22+)
docker compose watch
```

### 3. Ejecutar migraciones (primera vez)

```bash
# En otra terminal
make migrate
make createsuperuser
```

### 4. Acceder a la aplicación

- **Django**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Solr Admin**: http://localhost:8983/solr

## 📁 Estructura de Archivos Docker

```
.docker/
├── django/
│   ├── Dockerfile          # Multi-stage para producción
│   ├── Dockerfile.dev      # Single-stage para desarrollo
│   ├── entrypoint.sh       # Script de inicio (producción)
│   └── entrypoint.dev.sh   # Script de inicio (desarrollo)
├── nginx/
│   ├── nginx.conf          # Configuración principal
│   └── conf.d/
│       └── default.conf    # Site config
└── solr/
    └── create-core.sh      # Script para crear core

docker-compose.yml          # Configuración base
docker-compose.override.yml # Override para desarrollo (auto-cargado)
docker-compose.prod.yml     # Simulación de producción local
.dockerignore               # Exclusiones del contexto de build
.env.docker.example         # Template de variables de entorno
Makefile                    # Comandos útiles
```

## 🔧 Comandos Útiles (Makefile)

```bash
# Ver todos los comandos disponibles
make help

# Desarrollo
make dev            # Inicia todos los servicios
make logs           # Ver logs en tiempo real
make shell          # Django shell
make bash           # Bash en contenedor

# Django
make migrate        # Ejecutar migraciones
make makemigrations # Crear migraciones
make createsuperuser
make collectstatic
make rebuild-index  # Reconstruir índice Solr

# Base de datos
make db-shell       # Entrar a psql
make db-backup      # Crear backup
make db-restore FILE=backup.sql

# Limpieza
make clean          # Limpiar contenedores
make clean-all      # Limpiar TODO (⚠️ borra volúmenes)
```

## ⚙️ Variables de Entorno

Crear archivo `.env.docker` basado en `.env.docker.example`:

```env
# Django
SECRET_KEY=tu-secret-key-super-segura-de-50-caracteres-minimo
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=xyz_studio
DATABASE_USER=xyz_user
DATABASE_PASSWORD=tu_password_seguro

# Solr
SOLR_URL=http://solr:8983/solr/xyz_core

# Entrypoint
RUN_MIGRATIONS=true
COLLECT_STATIC=true
REBUILD_INDEX=false
```

## 🔍 Solr 6.6.6 - Notas Importantes

### Problema de Permisos (Legacy)

Solr 6.6.6 tiene problemas conocidos con permisos en volúmenes Docker. La solución implementada:

1. **Usuario explícito**: El contenedor corre como `user: "8983:8983"` (UID/GID de Solr)

2. **Entrypoint personalizado**: Crea el directorio del core y core.properties antes de iniciar

3. **Volumen nombrado**: Usa `solr_data` en lugar de bind mount para evitar problemas de permisos en Windows/Mac

### Crear Core Manualmente (si falla)

```bash
# Entrar al contenedor
docker compose exec solr bash

# Crear estructura del core
mkdir -p /opt/solr/server/solr/mycores/xyz_core/conf
mkdir -p /opt/solr/server/solr/mycores/xyz_core/data

# Copiar configuración base
cp -r /opt/solr/server/solr/configsets/basic_configs/conf/* \
      /opt/solr/server/solr/mycores/xyz_core/conf/

# Crear core.properties
echo "name=xyz_core" > /opt/solr/server/solr/mycores/xyz_core/core.properties
```

### Alternativa: Crear Core vía API

```bash
curl "http://localhost:8983/solr/admin/cores?action=CREATE&name=xyz_core&configSet=basic_configs"
```

## 🏭 Producción (AWS)

### Arquitectura Destino

- **Django**: AWS ECS (Fargate)
- **PostgreSQL**: AWS RDS
- **Solr**: EC2 dedicado
- **Static/Media**: S3 + CloudFront

### Simular Producción Localmente

```bash
# 1. Iniciar BD y Solr (servicios externos simulados)
docker compose up db solr -d

# 2. Iniciar stack de producción
docker compose -f docker-compose.prod.yml up --build
```

### Variables para Producción

```env
DATABASE_URL=postgres://user:pass@rds-endpoint:5432/dbname
SOLR_URL=http://ec2-solr-ip:8983/solr/xyz_core
DEBUG=False
ALLOWED_HOSTS=xyz-studio.dev,www.xyz-studio.dev
```

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Asegúrate de que Docker Desktop esté corriendo
docker info
```

### Error: "Port already in use"

```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8000

# O cambiar el puerto en docker-compose.override.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

### Error: "Solr core not found"

```bash
# Verificar estado del core
curl http://localhost:8983/solr/admin/cores?action=STATUS

# Reiniciar Solr
docker compose restart solr
```

### Error: "Database connection refused"

```bash
# Verificar que PostgreSQL está healthy
docker compose ps

# Ver logs de PostgreSQL
docker compose logs db
```

### Limpiar todo y empezar de cero

```bash
make clean-all
docker volume prune -f
make dev
```

## 📚 Referencias

- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
- [Docker Compose Watch](https://docs.docker.com/compose/file-watch/)
- [Django Oscar Docs](https://django-oscar.readthedocs.io/)
- [Solr 6.6 Reference Guide](https://solr.apache.org/guide/6_6/)
