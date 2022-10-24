from vlille.vlille_api import *

from database.db_conn import db_vls
from main import logger

def init_vlille_data():
    """ Init database data with vlille data

    Raises:
        ValueError: Si l'init n'a pas été mise à jour
    """
    vlilles = vlille_api.get_vlille()
    try:
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