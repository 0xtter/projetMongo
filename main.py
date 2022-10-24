import logging
import logging.config
import time

import database.db_manage


def setupLogger():
    global logger
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('project')


def main():
    database.db_manage.init_vlille_data()
    while True: 
        database.db_manage.update_vlille_data()
        time.sleep(10)


if __name__ == "__main__":
    setupLogger()
    logger.debug("Starting the application...")
    main()
