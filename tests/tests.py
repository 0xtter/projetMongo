# TO RUN UNIT TESTS:
# python -m unittest <path_to_this_directory>/tests.py


import unittest
import logging

import database.db_manage
from bson.objectid import ObjectId

class TestSearchStationsByName(unittest.TestCase):
    """
    Unit tests for database.db_manage.get_stations_by_name method

    """
    def test_no_match_found(self):
        cursor = database.db_manage.get_stations_by_name("blabla")
        size = len(list(cursor))
        self.assertEqual(size, 0)

    def test_one_match(self):
        cursor = database.db_manage.get_stations_by_name("pompidou")
        station = cursor.next()
        self.assertEqual(station["fields"]["nom"], 'POMPIDOU')

    def test_several_match(self):
        cursor = database.db_manage.get_stations_by_name("ch")
        size = len(list(cursor))
        self.assertGreaterEqual(size, 1)


class TestUpdateOneStation(unittest.TestCase):
    """
    Unit tests for database.db_manage.update_station method

    """
    def test_update_station_wrong_id(self):
        _id = ObjectId(b"123456789012")
        newvalues_dict = { "fields.etat": "EN TEST" }
        bool_result = database.db_manage.update_station(_id, newvalues_dict)
        self.assertFalse(bool_result)

    def test_update_station(self):
        station_cursor = database.db_manage.get_stations_by_name("POMPIDOU")
        station = station_cursor.next()

        _id = station["_id"]
        newvalues_dict = { "fields.etat": "EN TESTb" }
        bool_result = database.db_manage.update_station(_id, newvalues_dict)

        self.assertTrue(bool_result)
