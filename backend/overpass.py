import requests

from flask import current_app


def query(*queryList, search=None, out='xml', timeout=250):
    """
    queryList []: lista de expresiones tipo 'way["boundary"="administrative"]'
    search: osm id o bounding box
    """
    q = ';'.join([f'{ql}({search})' if search else ql for ql in queryList])
    for server in current_app.config.get('OSM3S_URLS'):
        url = f'{server}?' + f'data=[out:{out}][timeout:{timeout}];({q};);out body;>;out skel qt;'
        try:
            resp = requests.get(url)
            if resp.ok:
                return resp.text
        except requests.RequestException as e:
            print(str(e))
    return ""


def getOsmStreets(boundingBox):
    bb = f'{boundingBox[1]},{boundingBox[0]},{boundingBox[3]},{boundingBox[2]}'
    ql = [
        'way["highway"]["name"]',
        'relation["highway"]["name"]',
        'way["place"="square"]["name"]',
        'relation["place"="square"]["name"]',
    ]
    return query(*ql, search=bb)
