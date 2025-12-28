# XYZ Studio - E-commerce

Tienda online de decoración e impresión 3D construida con Django Oscar.

## Tecnologías

- **Django 5.2** - Framework web
- **Django Oscar** - Plataforma e-commerce
- **SQLite** - Base de datos (desarrollo)
- **Haystack** - Motor de búsqueda

## Requisitos

- Python 3.10+
- Pipenv

## Instalación

```bash
# Clonar repositorio
git clone <url-del-repo>
cd xyz-studio.dev

# Instalar dependencias
pipenv install

# Aplicar migraciones
pipenv run python manage.py migrate

# Crear superusuario
pipenv run python manage.py createsuperuser

# Ejecutar servidor
pipenv run python manage.py runserver
```

## Estructura

```
├── website/          # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── images/           # Archivos media (uploads)
├── cache/            # Cache de thumbnails
└── manage.py
```

## Accesos

- **Tienda**: http://127.0.0.1:8000/
- **Catálogo**: http://127.0.0.1:8000/catalogue/
- **Dashboard**: http://127.0.0.1:8000/dashboard/


## Notas

- En desarrollo, los archivos media se sirven automáticamente
- Para producción, configurar servidor web (nginx/apache) para archivos estáticos

---

**XYZ Studio** - Decoración e Impresión 3D
