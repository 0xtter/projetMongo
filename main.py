import json
import logging
import logging.config
import time

import database.db_manage
from db_conn import db_vls
from pymongo import GEO2D
import pprint



def setupLogger():
    global logger
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('project')

def func_test():
    # Test avec de la data fait 'main'
    db_vls.places.drop()

    logger.debug(db_vls.places.create_index([("test", GEO2D)]))    
    logger.debug(db_vls.places.insert_many([{"test": [2, 5]},
                                {"test": [30, 5]},
                                {"test": [1, 2]},
                                {"test": [4, 4]}]).inserted_ids)

    logger.info(db_vls.places.find_one())
    logger.info(db_vls.places.index_information())

    for doc in db_vls.places.find({"test": {"$near": [3, 6]}}).limit(3):
        pprint.pprint(doc) # Fonctionne!
    # Fin test

    database.db_manage.init_vlille_data()

    db_vls.stations.create_index([("geometry", GEO2D)])

    logger.info(db_vls.stations.index_information())
    logger.debug('stations:')

    pprint.pprint(db_vls.stations.find_one())
    for doc in db_vls.stations.find({'geometry':{"coordinates": {"$near" : [ 3.048567, 50.634268 ],"$maxDistance": 30,"$minDistance": 0}}}).limit(3):
        pprint.pprint(doc)
    exit()


def main():
    func_test()
    database.db_manage.init_vlille_data()
    # database.db_manage.get_vlille_around()
    exit()
    while True: 
        database.db_manage.update_vlille_data()
        time.sleep(10)


if __name__ == "__main__":
    setupLogger()
    logger.debug("Starting the application...")
    main()
