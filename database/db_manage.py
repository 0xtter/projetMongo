import pprint
import logging
import vlille.vlille_api as vlille_api
from pymongo import GEOSPHERE
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
        
        
        db_vls.stations.create_index([("geometry", GEOSPHERE)])
        vlilles = vlille_api.get_vlille()
        db_vls.stations.insert_many(vlilles)
    except Exception as e:
        logger.error(e)
        raise ValueError("Unknown error, data were not inserted in database : {}".format(e))


def update_vlille_data():
    datas = vlille_api.updated_vlille()
    nb_data_to_insert = len(datas)
    
    logger.info(f"Updating databse : {nb_data_to_insert} elements to update")

    for data in datas:
        db_vls.datas.update_one({'date': data["date"], "station_id": data["station_id"]}, {
                            "$set": data}, upsert=True)
                            
        logger.info(f"Element {datas.index(data)+1}/{nb_data_to_insert} updated!")

def get_vlille_around(x, y, range = 10):
    logger.info(f'Finding available vlille around...')
    try:
        vlille_around=db_vls.stations.find({'geometry':{"$nearSphere" : [ x , y ],'$maxDistance': range}})

        size = 0
        for doc in vlille_around:
            size+=1
            logger.debug(f'Found {doc}')
            
        logger.info(f'Found {size} available vlille around ({x} , {y}) in a range of {range}')

        return vlille_around

    except Exception as e:
        logger.error(f'Something went wrong finding vlille around in a range of {range}')
    logger.info("No vlille Near")

