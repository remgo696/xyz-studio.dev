# XYZ Studio - E-commerce

Plataforma e-commerce de decoración e impresión 3D con manufactura digital personalizada. Construida con Django Oscar y dockerizada con PostgreSQL, Redis y Solr.

## 📦 Stack Tecnológico

### Backend
- **Django 5.2** - Framework web asincrónico
- **Django Oscar 4.1** - Plataforma e-commerce empresarial
- **PostgreSQL 16** - Base de datos relacional
- **Python 3.13** - Runtime

### Frontend  
- **Tailwind CSS 4.1** - Utilidades CSS modernas
- **HTML 5** - Plantillas responsivas
- **Font Awesome 6.4** - Iconografía

### Búsqueda & Indexación
- **Apache Solr 6.6.6** - Motor de búsqueda legacy
- **Haystack 3.x** - ORM para búsqueda

### DevOps & Desarrollo
- **Docker Compose** - Orquestación de contenedores
- **docker-compose.override.yml** - Configuración dev con hot-reload
- **Pipenv** - Gestor de dependencias Python

### Otras Herramientas
- **Gunicorn** - WSGI server
- **WhiteNoise** - Servir estáticos
- **Sorl-Thumbnail** - Procesamiento de imágenes
- **django-tailwind** - Compilación de estilos

---

## 🚀 Requisitos del Sistema

- **Docker** 20.10+ y **Docker Compose** 2.10+
- **WSL 2** (si usas Windows)
- **Git** 2.25+

---

## 🛠️ Configuración Inicial

### 1. Clonar y preparar

```bash
git clone <url-del-repo> xyz-studio.dev
cd xyz-studio.dev

# Copiar archivos de configuración
cp .env.example .env.docker

# Verificar que todo esté listo
ls docker-compose.yml docker-compose.override.yml .docker/
```

### 2. Levantar contenedores

```bash
# Levantar entorno de desarrollo
make dev

# Alternativamente:
docker compose up --build -d

# Monitorear logs
docker compose logs -f web

# Alternativamente, usar:
make logs
```

### 3. Ejecutar migraciones

```bash
# Dentro del contenedor
make migrate

# O manualmente
docker exec xyz-web-dev python manage.py migrate
```

### 4. Crear superusuario

```bash
make createsuperuser

# O manualmente
docker exec -it xyz-web-dev python manage.py createsuperuser
```

## 📍 Accesos en Desarrollo

| Servicio | URL | Credenciales |
|----------|-----|-----------------|
| **Django (Tienda)** | http://localhost:8000 | - |
| **Admin/Dashboard** | http://localhost:8000/admin | Tu superusuario |
| **Oscar Dashboard** | http://localhost:8000/dashboard | Tu superusuario |
| **PostgreSQL** | localhost:5432 | `xyz_user` / `xyz_secret_password` |
| **Solr Search UI** | http://localhost:8983/solr | - |

### Hot-reload & Desarrollo
- **CSS**: Tailwind watcher actualiza automáticamente (`theme/static/css/dist/styles.css`)
- **Python**: Django dev server reinicia al detectar cambios
- **Templates**: Cambios visibles al refrescar el navegador

---

## 📂 Estructura del Proyecto

```
xyz-studio.dev/
├── .docker/                      # Configuración Docker
│   ├── django/
│   │   ├── Dockerfile           # Build para producción
│   │   ├── Dockerfile.dev       # Build para desarrollo
│   │   ├── entrypoint.sh        # Inicialización prod
│   │   └── entrypoint.dev.sh    # Inicialización dev
│   ├── solr/                    # Scripts de Solr
│   └── nginx/                   # Configuración Nginx
│
├── apps/                         # Aplicaciones Django customizadas
│   ├── address/                 # Direcciones (fork de Oscar)
│   ├── basket/                  # Carrito de compras
│   ├── catalogue/               # Catálogo de productos
│   ├── checkout/                # Checkout personalizado
│   └── shipping/                # Envíos personalizados
│
├── website/                      # Configuración principal Django
│   ├── settings.py              # Settings (DB, cache, Solr, etc)
│   ├── urls.py                  # Rutas principales
│   ├── context_processors.py    # Procesadores de contexto
│   └── wsgi.py / asgi.py        # Entry points
│
├── theme/                        # Tema frontend
│   ├── static/                  # CSS/JS compilados
│   │   └── css/dist/styles.css  # Tailwind compilado
│   ├── static_src/              # Fuentes de estilos
│   │   ├── src/styles.css       # CSS entrada Tailwind
│   │   ├── tailwind.config.js   # Config Tailwind
│   │   └── package.json         # Dependencias Node
│   └── templates/               # HTML templates
│
├── templates/                    # Templates generales
│   └── oscar/                   # Overrides de Oscar
│
├── media/                        # Uploads de usuarios
├── staticfiles/                  # Statics compilados (producción)
│
├── docker-compose.yml            # Config base (dev + prod)
├── docker-compose.override.yml   # Override solo desarrollo
├── docker-compose.prod.yml       # Config producción local
│
├── scripts/
│   ├── migrate_data.py          # Migrar SQLite → PostgreSQL
│   └── migrate_sqlite_to_postgres.sh
│
├── Makefile                      # Comandos útiles
├── Pipfile / Pipfile.lock        # Dependencias Python
└── README.md                     # Este archivo
```

---

## 🎯 Comandos Útiles (Make)

```bash
# Levantar desarrollo
make dev

# Migraciones
make migrate

# Crear superusuario
make createsuperuser

# Shell de Django
make shell

# Collectstatic (producción)
make collectstatic

# Logs en tiempo real
make logs

# Detener contenedores
make stop

# Ver todos los comandos
make help
```

---

## 🔧 Variables de Entorno

### .env (Desarrollo local - NO COMMITEAR)
```env
SECRET_KEY=django-insecure-...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Tienda
SHOP_WHATSAPP=51957080898
SHOP_EMAIL=contacto@xyzstudio.pe
SHOP_PHONE=957080898
SHOP_ADDRESS=Zárate, San Juan de Lurigancho, Lima - Perú
```

### .env.docker (Contenedores - Copiar del .env.example)
```env
# Creadas automáticamente por docker-compose.yml
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=xyz_studio
DATABASE_USER=xyz_user
DATABASE_PASSWORD=xyz_secret_password
```

---

## 🐛 Troubleshooting

### "ERROR: [doc=catalogue.product.4] unknown field 'django_ct'" (Solr)
Es normal después de migrar datos. El índice de búsqueda está desincronizado:
```bash
# Reconstruir índice
docker exec xyz-web-dev python manage.py rebuild_index --noinput
```

### "psycopg2 connection refused"
PostgreSQL no está listo. Espera 10s y reinicia:
```bash
docker compose restart web
```

### Los estilos CSS no se ven
Tailwind no está compilando. Verifica el contenedor:
```bash
docker logs xyz-tailwind --tail 50
docker compose restart tailwind
```

### Port 8000 ya está en uso
```bash
# Cambiar puerto en docker-compose.override.yml
# O liberar el puerto
lsof -i :8000  # Encontrar proceso
kill -9 <PID>  # Matar proceso
```

---

## 🚢 Deployment a Producción

### Usando ECS (Fargate) en AWS
Ver archivo `DOCKER.md` para instrucciones completas.

Resumen:
```bash
# 1. Build y push a ECR
docker build -f .docker/django/Dockerfile -t xyz-studio:latest .
aws ecr get-login-password | docker login ...
docker tag xyz-studio:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/xyz-studio:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/xyz-studio:latest

# 2. Deploy a ECS via Terraform o CloudFormation
```

---

## 📊 Bases de Datos & Búsqueda

### PostgreSQL
- Host: `db` (en Docker) / `localhost:5432` (local)
- BD: `xyz_studio`
- Usuario: `xyz_user`
- Datos persistidos en volumen: `xyz-postgres-data`

### Solr (Búsqueda)
- URL: http://localhost:8983/solr
- Core: `xyz_core`
- Índice persistido en: `xyz-solr-data`
- Config: `/opt/solr/server/solr/mycores/xyz_core/conf/`

### Redis (Opcional - para cache)
No incluido por defecto. Para agregar:
```bash
# docker-compose.yml - agregar servicio
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## 📝 Notas Importantes

### Line Endings (CRLF vs LF)
El proyecto fue migrado de Windows a WSL. Los line endings se corrigieron automáticamente:
```bash
git config core.autocrlf input  # Configurado globalmente
```

### Volúmenes Docker
Los datos persisten en volúmenes nombrados. Para limpiarlos completamente:
```bash
docker compose down -v  # Elimina volúmenes
docker compose up --build  # Crea BD desde cero
```

### Migraciones de Datos
Hay un modelo PostgreSQL-only (`ProductCategoryHierarchy` - vista materializada) que se excluye del dump de SQLite. Esto es normal y no afecta funcionalidad.

---

## 👨‍💻 Contribuir

1. Crear rama: `git checkout -b feature/tu-feature`
2. Hacer cambios y commit
3. Push y abrir Pull Request
4. Asegurarse que las migraciones están sincronizadas

---

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.

---

**XYZ Studio** © 2025 - Decoración e Impresión 3D | Lima, Perú
