# borrador comprobación actualización
import json
import os
import re

DATA='/media/javier/memo/catastro/update/'

if __name__ == '__main__':
    municipios = {}
    for mun_code in os.listdir(DATA):
        if not re.match(r'[0-9]{5}', mun_code):
            continue
        mun = {
            'code': mun_code,
            'exists': '',
            'status': '',
            'error': '',
            'tasks': 0,
        }
        log_file = DATA + mun_code + '/catatom2osm.log'
        mun['exists'] = 'exists' if os.path.exists(DATA + mun_code) else ''
        if (mun['exists']):
            if (
                os.path.exists(DATA + mun_code + '/tasks')
                and os.path.exists(DATA + mun_code + '/report.json')
                and os.path.exists(log_file)
            ):
                with open(DATA + mun_code + '/report.json') as fo:
                    report = json.load(fo)
                    if 'tasks' in report:
                        mun['tasks'] = report['tasks']
                        mun['status'] = 'OK' if True else 'KO'
                with open(log_file) as fo:
                    log_text = fo.read()
                mun['error'] = 'error' if 'ERROR' in log_text else ''
        municipios[mun_code] = mun
        print('\t'.join([str(v) for v in mun.values()]))
