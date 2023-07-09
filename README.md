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

Configurar en .env.development.local los municipios a descargar usando las 
variables INCLUDE_PROVS, EXCLUDE_PROVS, INCLUDE_MUNS, EXCLUDE_MUNS.
La vista inicial del mapa se puede configurar en frontend/.env.local

Para poder autenticar hay que añadir OSM_CLIENT_ID, OSM_CLIENT_SECRET
obtenidos de https://www.openstreetmap.org/oauth2/applications/new

La URI de redirección es http://127.0.0.1/api/authorize

Marcar 'Leer preferencias de usuario'
Descmarcar '¿Solicitud confidencial?'

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

git Configura en .env.production.local las claves a usar.

En https://www.openstreetmap.org/oauth2/applications/new
hay que obtener OSM_CLIENT_ID, OSM_CLIENT_SECRET y registrar la redirección a

https://visor-catastro.cartobase.es/api/authorize
    
    make build

Poner en marcha los servicios

    make up

Visualización de registro

    make logs

Parar los servicios

    make down
