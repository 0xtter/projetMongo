import json
import logging
import vlille.vlille_api as vlille_api
from pymongo import GEO2D
from bson.son import SON

from db_conn import db_vls

logger = logging.getLogger('project')


def init_vlille_data():
    """ Init database data with vlille data

    Raises:
        ValueError: Si l'init n'a pas été mise à jour
    """
    try:
        try:
            db_vls.stations.drop()
            logger.debug('stations collection dropped sucessfuly')
        except Exception as e:
            logger.error(e)
            
        vlilles = vlille_api.get_vlille()
        # db_vls.stations.create_index([("geometry", GEO2D)])
        # db_vls.stations.create_index([("geometry", GEOSPHERE)])
        db_vls.stations.insert_many(vlilles, ordered=False)
    except Exception as e:
        logger.error(e)
        raise ValueError("Unknown error, data were not inserted in database : {}".format(e))


def update_vlille_data():
    datas = vlille_api.updated_vlille()
    nb_data_to_insert = len(datas)
    
    logger.debug(f"Updating databse : {nb_data_to_insert} elements to update")

    for data in datas:
        db_vls.datas.update_one({'date': data["date"], "station_id": data["station_id"]}, {
                            "$set": data}, upsert=True)
                            
        logger.debug(f"Element {datas.index(data)+1}/{nb_data_to_insert} updated!")

def get_vlille_around():
    logger.debug(f'Finding available vlille around...')
    logger.info(db_vls.stations.find_one())

    for vlille in db_vls.stations.find({"location" : SON([("$near", { "$geometry" : SON([("type", "Point"), ("coordinates", [40, 5])])})])}):
        logger.info(vlille)

    # for stat in db_vls.stations.find({"location": {"$near" : {"coordinates": [ 3.048567, 50.634268 ]},"$maxDistance": 300,"$minDistance": 0}}):
    #      logger.info("found!")
    #      logger.info(stat)

    logger.info("No vlille Near")

    #logger.info(db_vls['stations'].find())
    #logger.info(json.dumps(db_vls['stations'].find_one(), indent=4))
