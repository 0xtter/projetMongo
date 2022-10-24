import json
import requests


def get_vlille():
    url = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=3000&facet=libelle&facet=nom&facet=commune&facet=etat&facet=type&facet=etatconnexion"
    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode('utf8'))
    return response_json.get("records", [])

def vlilles_to_insert(vlilles):
    vlilles_to_insert = [
        {
            '_id': elem.get('fields', {}).get('libelle'),
            'name': elem.get('fields', {}).get('nom', '').title(),
            'geometry': elem.get('geometry'),
            'size': elem.get('fields', {}).get('nbvelosdispo') + elem.get('fields', {}).get('nbplacesdispo'),
            'source': {
                'dataset': 'Lille',
                'id_ext': elem.get('fields', {}).get('libelle')
            },
            'tpe': elem.get('fields', {}).get('type', '') == 'AVEC TPE'
        }
        for elem in vlilles
    ]
    
    return vlilles_to_insert