# visor-catastro

Prototipo para la importación directa de los archivos del [catastro de españa](https://www1.sedecatastro.gob.es/). El objetivo es poder colaborar sin pasos intermedios: acercarse al sitio que se desee importar, seleccionar una parcela y mapearla.

Demo: https://visor-catastro.cartobase.es/

**NOTA**: No utilizarse para mapear catastro. Por el momento esto es una simple maqueta con la parte de la interacción del usuario. No almacena información ni guarda estados de las parcelas.

## Desarrollo

### Instalación

Crear el archivo .env.development.local a partir de env.development.local.tpl.
Configurar municipios a descargar usando las variables INCLUDE_PROVS, EXCLUDE_PROVS,
INCLUDE_MUNS, EXCLUDE_MUNS.
La vista inicial del mapa se puede configurar en frontend/.env.local (usa como
plantilla frontend/.env)

Crear las carpetas de datos:

    mkdir -p data/update
    mkdir -p data/dist

Construir la imagen:

    docker pull egofer/catatom2osm
    docker-compose build

Instalar las dependencias del frontend:

    npm install --prefix frontend

### Ejecución

Ventana 1:

    docker-compose up

Ventana 2:

    cd frontend
    npm run dev

### Contribución

Si se modifica el modelo de la base de datos, hay que registrarlo:

    docker-compose run --rm backend flask db migrate -m "Comentario migración"
    docker-compose run --rm backend flask db upgrade

Si se modifican dependencias Python, hay que reflejarlo en los archivos requirements.txt.
Por ejemplo, en backend:

    docker-compose run --rm backend pip install ...
    docker-compose run --rm backend pip freeze > backend/requirements.txt

## Producción

### Instalación

Añade /etc/environment esta variables de entorno

CATASTRO_DATA=/var/catastro/

Copiar env.development.local.tpl en .env.development.local
Crear y configurar el archivo .env.production.local a partir de env.production.local.tpl.

Crear las carpetas de datos:

    sudo mkdir -p /var/catastro/dist
    sudo mkdir -p /var/catastro/update
    sudo chown 1000:1000 /var/catastro/update

Construir la imagen:

    docker pull egofer/catatom2osm
    COMPOSE_PROFILES=production docker-compose build

Poner en marcha los servicios

    COMPOSE_PROFILES=production docker-compose -f docker-compose.yaml up -d

Visualización de registro

    docker-compose logs -f

Parar los servicios

    docker-compose down --remove-orphans
