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

## Desarrollo

Ventana 1:

    docker-compose up

Ventana 2:

    cd frontend
    npm run dev

## Producción

...

    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d