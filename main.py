import logging
import logging.config
import time

from pymongo import GEO2D

import database.db_manage


def setupLogger():
    global logger
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('project')


def main():
    database.db_manage.init_vlille_data()
    database.db_manage.get_vlille_around(30,50,0.298) # A determiner et convertir les radians en mètres 0.298 est le seuil a partir duquel certaines station sortent de la range
    while True: 
        database.db_manage.update_vlille_data()
        database.db_manage.get_vlille_around(30,50,0.298)
        time.sleep(10)


if __name__ == "__main__":
    setupLogger()
    logger.debug("Starting the application...")
    main()
