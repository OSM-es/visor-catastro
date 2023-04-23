CATASTRO_DATA=/var/catastro/
CLIENT_URL="https://visor-catastro.cartobase.es"
FLASK_SECRET_KEY="una clave secreta"
POSTGRES_USER=admin
POSTGRES_DB=gis
POSTGRES_PASSWORD=admin

CHECK_TIME=00:13 # Hora para comprobación diaria de actualizaciones
# Eliminar o vaciar en producción
INCLUDE_PROVS=Lista de códigos de provincia a incluir
EXCLUDE_PROVS=Lista de códigos de provincia a excluir
INCLUDE_MUNS=Lista de códigos de municipio a incluir
EXCLUDE_MUNS=Lista de códigos de municipio a excluir