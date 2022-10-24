import json

import dateutil.parser
import requests

# from main import logger


def get_vlille():
    """_summary_

    Returns:
        _type_: _description_
    """    
    logger.debug("Getting vlille infos")
    url = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=3000&facet=libelle&facet=nom&facet=commune&facet=etat&facet=type&facet=etatconnexion"
    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode('utf8'))
    return response_json.get("records", [])

def vlilles_to_insert(vlilles):
    """_summary_

    Args:
        vlilles (_type_): _description_

    Returns:
        _type_: _description_
    """    
    logger.debug("Formating vlille to MongoDB format")
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

def updated_vlille():
    """_summary_

    Returns:
        _type_: _description_
    """    
    logger.debug("Start fetching the update from vlille")
    vlilles = get_vlille()
    datas = [
        {
            "bike_availbale": elem.get('fields', {}).get('nbvelosdispo'),
            "stand_availbale": elem.get('fields', {}).get('nbplacesdispo'),
            "date": dateutil.parser.parse(elem.get('fields', {}).get('datemiseajour')),
            "station_id": elem.get('fields', {}).get('libelle')
        }
        for elem in vlilles
    ]
    return datas
