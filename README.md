# visor-catastro

Prototipo para la importación directa de los archivos del [catastro de españa](https://www1.sedecatastro.gob.es/). El objetivo es poder colaborar sin pasos intermedios: acercarse al sitio que se desee importar, seleccionar una parcela y mapearla.

Demo: https://visor-catastro.cartobase.es/

**NOTA**: No utilizarse para mapear catastro. Por el momento esto es una simple maqueta con la parte de la interacción del usuario. No almacena información ni guarda estados de las parcelas.

## Desarrollo

### Instalación

Crear el archivo .env.local a partir de env.tpl.
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

Preparar la base de datos:

    docker-compose up -d postgres
    docker-compose exec postgres psql -U admin gis -c "DROP EXTENSION postgis_tiger_geocoder;"
    docker-compose run --rm backend flask db upgrade
    docker-compose down

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

    docker-compose exec backend flask db migrate -m "Comentario migración"
    docker-compose exec backend flask db upgrade

Si se modifican dependencias Python, hay que reflejarlo en los archivos requirements.txt.
Por ejemplo, en backend:

    docker-compose run --rm backend pip install ...
    docker-compose run --rm backend pip freeze > backend/requirements.txt

## Producción

### Instalación

Crear y configurar el archivo .env.local a partir de env.tpl.
Eliminar o vaciar las variables INCLUDE_PROVS, EXCLUDE_PROVS, INCLUDE_MUNS, EXCLUDE_MUNS.

Crear las carpetas de datos:

    sudo mkdir -p data/dist
    sudo mkdir -p data/update
    sudo chown 1000:1000 data/update

Construir la imagen:

    docker pull egofer/catatom2osm
    docker-compose build

Preparar la base de datos:

    docker-compose --env-file .env.local up -d postgres
    docker-compose exec postgres psql -U admin gis -c "DROP EXTENSION postgis_tiger_geocoder;"
    docker-compose  --env-file .env.local run --rm backend flask db upgrade
    docker-compose down

Poner en marcha los servicios

    docker-compose --profile prod --env-file .env.local -f docker-compose.yaml -f docker-compose.prod.yaml up -d

Visualización de registro

    docker-compose logs -f

Parar los servicios

    docker-compose down --remove-orphans
