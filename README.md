# visor-catastro

Prototipo para la importación directa de los archivos del 
[Catastro de España](https://www1.sedecatastro.gob.es/). 
El objetivo es poder colaborar sin pasos intermedios: 
acercarse al sitio que se desee importar, seleccionar una parcela y mapearla.

Demo: https://visor-catastro.cartobase.es/

**NOTA**: No utilizarse para mapear catastro. Por el momento esto es una simple 
maqueta con la parte de la interacción del usuario. No almacena información ni 
guarda estados de las parcelas.

## Desarrollo

### Instalación

    make install

Configurar .env.development.local los municipios a descargar usando las 
variables INCLUDE_PROVS, EXCLUDE_PROVS, INCLUDE_MUNS, EXCLUDE_MUNS.
La vista inicial del mapa se puede configurar en frontend/.env.local

    make build

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

Añade a /etc/environment estas variables de entorno

CATASTRO_DATA=/var/catastro/
COMPOSE_PROFILES=production

Reabre la sesión
    
    sudo make install

Configurar el archivo .env.production.local

    make build

Poner en marcha los servicios

    make up

Visualización de registro

    make logs

Parar los servicios

    make down
