# =============================================================================
# XYZ Studio - Django Oscar E-commerce
# Multi-Stage Dockerfile for Production-Ready Images
# =============================================================================
# Stages:
#   1. node-builder    - Compila Tailwind CSS assets
#   2. python-builder  - Instala dependencias Python con Pipenv
#   3. runner          - Imagen final limpia sin compiladores
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: Node Builder - Compilación de Tailwind CSS
# -----------------------------------------------------------------------------
FROM node:20-alpine AS node-builder

LABEL stage="node-builder"

WORKDIR /build

# Copiar solo archivos necesarios para instalación de deps (cache layer)
COPY theme/static_src/package*.json ./

# Instalar dependencias de Node
RUN npm ci --prefer-offline --no-audit --silent

# Copiar el resto del código fuente de tailwind
COPY theme/static_src/ ./

# Crear directorio de salida y compilar CSS para producción
RUN mkdir -p ../static/css/dist && \
    npm run build

# El CSS compilado queda en /build/../static/css/dist/styles.css
# que es /static/css/dist/styles.css

# -----------------------------------------------------------------------------
# STAGE 2: Python Builder - Instalación de Dependencias
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS python-builder

LABEL stage="python-builder"

# Variables de entorno para optimizar Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Instalar dependencias de compilación (gcc, libpq-dev para psycopg)
# y herramientas necesarias para build123d y otras deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar pipenv
RUN pip install --no-cache-dir pipenv

# Copiar solo Pipfile primero para maximizar cache
COPY Pipfile Pipfile.lock ./

# Instalar dependencias en el sistema (no en virtualenv)
# --deploy: Falla si Pipfile.lock está desactualizado
# --system: Instala en site-packages del sistema
RUN pipenv install --system --deploy --ignore-pipfile

# -----------------------------------------------------------------------------
# STAGE 3: Runner - Imagen Final de Producción
# -----------------------------------------------------------------------------
FROM python:3.13-slim AS runner

LABEL maintainer="XYZ Studio <dev@xyz-studio.dev>" \
      version="1.0.0" \
      description="Django Oscar E-commerce Production Image"

# Variables de entorno de producción
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Directorio de la aplicación
    APP_HOME=/app \
    # Usuario no privilegiado
    APP_USER=appuser \
    APP_GROUP=appgroup \
    # Django settings
    DJANGO_SETTINGS_MODULE=website.settings \
    # Puerto de la aplicación
    PORT=8000

WORKDIR ${APP_HOME}

# Instalar solo dependencias de runtime (libpq para psycopg, netcat para healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no privilegiado para seguridad
RUN groupadd --gid 1000 ${APP_GROUP} && \
    useradd --uid 1000 --gid ${APP_GROUP} --shell /bin/bash --create-home ${APP_USER}

# Copiar librerías Python instaladas desde el builder
COPY --from=python-builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=python-builder /usr/local/bin/ /usr/local/bin/

# Copiar CSS compilado desde el node-builder
# El CSS va a theme/static/css/dist/
COPY --from=node-builder /static/css/dist/ ${APP_HOME}/theme/static/css/dist/

# Copiar código fuente de la aplicación
COPY --chown=${APP_USER}:${APP_GROUP} . ${APP_HOME}/

# Copiar y configurar entrypoint
COPY --chown=${APP_USER}:${APP_GROUP} .docker/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Crear directorios necesarios con permisos correctos
RUN mkdir -p ${APP_HOME}/staticfiles ${APP_HOME}/media && \
    chown -R ${APP_USER}:${APP_GROUP} ${APP_HOME}

# Cambiar a usuario no privilegiado
USER ${APP_USER}

# Exponer puerto
EXPOSE ${PORT}

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health/ || exit 1

# Entrypoint y comando por defecto
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "website.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--access-logfile", "-", "--error-logfile", "-"]
