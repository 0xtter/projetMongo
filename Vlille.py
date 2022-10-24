
import requests
import json
import dateutil.parser
import time
import logging
import logging.config

from db_conn import client
from vlille_api import get_vlille

def setupLogger():
    global logger
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('project')

def main():
    db = client.vls
    vlilles = get_vlille()

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
    
    try: 
        db.stations.insert_many(vlilles_to_insert, ordered=False)
    except:
        pass

    while True:
        print('update')
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
        
        for data in datas:
            logger.info("Inserting into databse")
            db.datas.update_one({'date': data["date"], "station_id": data["station_id"]}, { "$set": data }, upsert=True)
            logger.info("Insert sucessfull")

        time.sleep(10)


    
if __name__ == "__main__":
    setupLogger()
    logger.info("test")
    main()