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
    
    logger.info(f"Updating databse : {nb_data_to_insert} elements to update...")

    for data in datas:
        db_vls.datas.update_one({'date': data["date"], "station_id": data["station_id"]}, {"$set": data}, upsert=True)
                            
        logger.debug(f"Element {datas.index(data)+1}/{nb_data_to_insert} updated!")
    logger.info(f'{nb_data_to_insert} Stations have been updated!')


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


def get_stations_by_name(name):
    """ Find all station where their name contains the
    substring given in argument (case insensitive)

    Args:
        name (string): 

    Returns:
       Cursor: research result
    """
    logger.info(f"Finding stations whose name includes substring : {name} ")
    try:
        query = {'fields.nom': {'$regex': f"{name}", '$options': 'i' } }    # i for case insensitive
        stations_cursor = db_vls.stations.find(query)
        
        size = 0
        for station in stations_cursor:
            size+=1
            logger.debug("Found '{}'".format(station["fields"]["nom"]))

        logger.info(f"Found {size} stations including substring '{name}' in its name.")

        return stations_cursor.rewind()     # rewind() is necessary as cursor have already been evaluated

    except Exception as e:
        logger.error(f"Something went wrong searching station {name} : {e}")


def update_station(_id, newvalues_dict):
    """ Update station values

    Args:
        _id (bson.objectid.ObjectId): station's id
        newvalues_dict (_type_): dictionnary of fields and their values. For instance :
        { 'fields.etat': "EN TEST", 'fields.nom: "BetaTest" }
    
    Returns:
        Boolean: True if update went well, False otherwise
    """
    logger.info(f"Updating station _id={_id} with values {newvalues_dict}")

    custom_filter = {'_id': _id}
    newvalues = {'$set': newvalues_dict}

    try:
        update_result = db_vls.stations.update_one(custom_filter, newvalues)

        # check if update successful
        if update_result.matched_count == 1:
            logger.debug(f"Station id {_id} updated.")
            return True
        else:
            logger.debug(f"No station found with id {_id}.")
            return False

    except Exception as e:
        logger.error(f"Something went wrong when updating station {_id} : {e}")


def delete_station(_id):
    """ Met à jour les informations d'une station

    Args:
        _id (bson.objectid.ObjectId): id de la station
        newvalues_dict (_type_): dictionnaire des valeurs à modifier. Par exemple :
        { 'fields.etat': "EN TEST", 'fields.nom: "BetaTest" }
    
    Returns:
        Boolean: True if deleted, False otherwise
    """    
    logger.info(f"Deleting station _id={_id}")

    custom_filter = {'_id': _id}

    try:
        result = db_vls.stations.delete_one(custom_filter)

        if result.deleted_count == 1:
            logger.debug(f"Station id {_id} deleted.")
            return True

        logger.debug(f"Station id {_id} not deleted.")
        return False

    except Exception as e:
        logger.error(f"Something went wrong when deleting station {_id} : {e}")


def get_stations_under_ratio(ratio_level=0.2):
    """ Between 6pm and 7pm & from monday to friday

    Args:
        ratio_level (float, optional): ratio bike/total_stand. Defaults to 0.2.

    Returns:
        CommandCursor: result of the research
    """    

    total_stands = {'$sum': ['$bike_availbale', '$stand_availbale'] }
    ratio = { "$divide": [ "$bike_availbale", total_stands ] }

    pipeline = [
        {
        # combine stations and datas collection
        '$lookup': {
            'from': 'stations', 
            'localField': 'station_id',
            'foreignField': 'fields.libelle', 
            'as': 'station_info'
            }
        },
        {
        # prevent division from zero in ratio division
        '$match': {
            '$and': [
                {
                    'bike_availbale': {'$ne': 0}
                },
                {
                    'stand_availbale': {'$ne': 0}
                }
            ]
            }  
        },
        { # Add station name to output doc
        '$addFields': {
            'nom'  : "$station_info.fields.nom"
            }
        },
        {
            '$unwind': "$nom"
        },
        {
        # set output doc 
        '$project': {
            '_id': 0,
            'station_id': { '$toInt': '$station_id'},
            'ratio': ratio,
            'dayOfWeek': { '$dayOfWeek': "$date" },     # <-- important
            'date': { '$toString': "$date" },
            'hour': { '$hour': "$date" },
            'bike_availbale': 1,
            'stand_availbale': 1,
            'nom': 1,
            }
        },
        { 
        # only from monday to friday (sun=1 -> sat=7)
        # only a ratio <= 0.2
        # only between 18 and 19
        '$match': {
            'dayOfWeek': { '$in': [2, 3, 4, 5, 6] },
            'ratio': { '$lte': ratio_level },
            'hour': { '$eq': 18 },
            }
        },
        { 
        # sort by date
        '$sort': {
            'date': 1,
            }
        }
    ]

    result = db_vls.datas.aggregate(pipeline)
    
    return result