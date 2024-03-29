import os
from logging.config import dictConfig

dictConfig(
    {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(levelname)s] %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default',
            }
        },
        'root': {'level': 'INFO', 'handlers': ['console']},
    }
)

class Config:
    # Clave para firma de cookies de sesión.
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'flask secret key')
    # Política de envío de cookie de sesión.
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Cors
    CLIENT_URL = os.getenv('CLIENT_URL', 'http://127.0.0.1:5173')
    
    # Base de datos
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'gis')
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{POSTGRES_USER}:'
        f'{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}'
    )
    
    #OAuth
    OSM_CLIENT_ID = os.getenv('OSM_CLIENT_ID', '')
    OSM_CLIENT_SECRET = os.getenv('OSM_CLIENT_SECRET', '')
    OSM_URL = os.getenv('OSM_URL', 'https://www.openstreetmap.org')

    # Datos catatom
    UPDATE_PATH = '/data/update/'

    # OSM3S
    OSM3S_URLS = [
        'https://osm3s.cartobase.es/api/interpreter',
        'http://overpass-api.de/api/interpreter',
        'http://overpass.osm.rambler.ru/cgi/interpreter',
    ]

    # Catastro
    FOTO_FACHADA_URL = 'http://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral='

    # Cache
    CACHE_TYPE = 'FileSystemCache'
    CACHE_DEFAULT_TIMEOUT = 0
    CACHE_DIR = '/data/cache'
    CACHE_THRESHOLD = 1000
