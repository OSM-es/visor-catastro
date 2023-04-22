# visor-catastro

Prototipo para la importación directa de los archivos del [catastro de españa](https://www1.sedecatastro.gob.es/). El objetivo es poder colaborar sin pasos intermedios: acercarse al sitio que se desee importar, seleccionar una parcela y mapearla.

Demo: https://visor-catastro.cartobase.es/

**NOTA**: No utilizarse para mapear catastro. Por el momento esto es una simple maqueta con la parte de la interacción del usuario. No almacena información ni guarda estados de las parcelas.

## Instalación

Crear las carpetas de datos:

    mkdir -p data/update
    mkdir -p data/dist

Construir la imagen:

    docker pull egofer/catatom2osm
    docker-compose build

Preparar la base de datos:

    docker-compose up -d
    docker-compose exec postgres psql -U admin gis -c "DROP EXTENSION postgis_tiger_geocoder;"
    docker-compose exec backend flask db upgrade
    docker-compose down

## Desarrollo

Ventana 1:

    docker-compose up

Ventana 2:

    cd frontend
    npm run dev

Si se modifica el modelo de la base de datos, hay que registrarlo en otra ventana:

    docker-compose exec backend flask db migrate -m "Comentario migración"
    docker-compose exec backend flask db upgrade

## Producción

Crear y configurar el archivo .env.local a partir de env.tpl.
...

    docker-compose --env-file .env.local -f docker-compose.yaml -f docker-compose.prod.yaml up -d