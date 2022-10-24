import json
import logging
import logging.config
from operator import indexOf
import time

import dateutil.parser
import requests

from db_conn import client
from vlille_api import get_vlille, vlilles_to_insert


def setupLogger():
    global logger
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('project')


def main():
    db = client.vls
    vlilles = get_vlille()
    
    try:
        db.stations.insert_many(vlilles_to_insert, ordered=False)
    except:
        pass

    while True: 
        logger.debug("Start Updating the databse")
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

        nb_data_to_insert = len(datas)
        
        logger.debug(f"Inserting into databse {nb_data_to_insert} elements")

        for data in datas:
            logger.debug(f"Element {datas.index(data)+1}/{nb_data_to_insert}")
            db.datas.update_one({'date': data["date"], "station_id": data["station_id"]}, {
                                "$set": data}, upsert=True)

        time.sleep(10)


if __name__ == "__main__":
    setupLogger()
    logger.debug("Starting the application...")
    main()
