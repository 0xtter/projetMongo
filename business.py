# QUESTION 4, BUSINESS PROGRAM
import json
import logging

import jsbeautifier
from bson import json_util

import database.db_manage
from db_conn import db_vls


def setupLogger():
    global logger
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('project')

def display_title(msg):
    print(f"\n#---- {msg} ----#\n")


def display_text(msg):
    print(msg + "\n")


def display_beautiful_dict(d):
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    beautiful_output = jsbeautifier.beautify(json_util.dumps(d), opts)
    display_text(beautiful_output)


def integer_input(msg, min=None, max=None):
    while True:
        try:
            i = input(msg + ' : ')
            choice = int(i)
            if min and max and min <= choice <= max:
                return choice
            elif min and not max and min <= choice:
                return choice
            elif not min and max and choice <= max:
                return choice
            else:
                display_text("Invalid choice, please try again.")
        except Exception:
            display_text("This is not an integer. Please try again.")


def newvalue_input(dictionnary, msg=""):
    """ Ask for user to enter the key and a new value
    associated to that key.

    Args:
        dictionnary (_type_): object to be updated
        msg (_type_): message to prompt to user

    Returns:
        dict: { key, updated_value }
    """

    if msg: display_text(msg)

    key = None
    is_key_valid = False
    while not is_key_valid:
        key_input = input("Enter key name (use . for nested keys, e.g. 'fields.nom') : ")
        keys = [k for k in key_input.split('.') if k ]
        # browse to value inside the dict to verify key exists
        try:
            d = dictionnary
            for k in keys: d = d[k]
            key, is_key_valid = key_input, True
        except:
            display_text(f"Key '{key_input}' does not exists.")
    
    updated_value = input("New value : ")

    newvalue = dict()
    newvalue[key] = updated_value

    return newvalue


def display_business_menu():
    msg = """
    Please select an option :

    (1) - find station with name
    (2) - update a station
    (3) - delete a station
    (4) - deactivate all station in an area
    (5) - give all stations with a ratio bike/total_stand under 20% between 18h and 19h00 (monday to friday)
    """
    display_text(msg)

    choice = integer_input("Your choice ? (a integer between 1 and 5)", min=1, max=5)
    
    if choice == 1:
        return find_station_with_name()
    elif choice == 2:
        return menu_update_station()
    elif choice == 3:
        return menu_delete_station()
    elif choice == 4:
        return menu_deactivate_all_station_in_area()
    elif choice == 5:
        return give_stations_under_ratio()


def find_station_with_name():
    search = input("Enter the name of a station (enter 0 to go back) : ")

    if search == "0":
        return display_business_menu()
    
    cursor = database.db_manage.get_stations_by_name(search)
    found = 0
    for station in cursor:
        found += 1
        display_beautiful_dict(station)
    
    if not found:
        display_title("No matching station name.")
    else:
        display_title(f"Found : {found}")
        input("Press ENTER to continue...")

    return display_business_menu()


def menu_update_station():
    
    stations_cursor = db_vls.stations.find()

    found = 0
    choices = {}

    # display all available stations

    for station in stations_cursor:
        found += 1
        choices[found] = station
        print("({}) - {} ".format(found, station["name"]))

    if not found:
        display_text("No station registered.")
        return display_business_menu()

    idx = integer_input("To update a station, enter the associated integer", min=1, max=len(choices))
    choosen_station = choices[idx]

    # display data of the choosen station

    display_title("Actual data of the station")
    display_beautiful_dict(choosen_station)

    # let user specify the values to be updated

    display_title("Update values")

    newvalues = dict()

    is_modification_done = False
    while not is_modification_done:
        new = newvalue_input(choosen_station)
        newvalues.update(new)

        display_text("Values to be updated :")
        display_beautiful_dict(newvalues)

        next_action_input = input("Enter 'ok' if you have modified everything you need, \notherwise press type anything to continue modifying values : ")

        if next_action_input == "ok": is_modification_done = True
    
    # Update station

    is_updated = database.db_manage.update_station(choosen_station["_id"], newvalues)

    if is_updated:
        display_title("Station updated")
    else:
        display_title("Station not updated")
    
    input("Press ENTER to continue...")

    return display_business_menu()


def menu_delete_station():
    
    stations_cursor = db_vls.stations.find()

    found = 0
    choices = {}

    # display all available stations

    for station in stations_cursor:
        found += 1
        choices[found] = station
        print("({}) - {} ".format(found, station["name"]))

    if not found:
        display_text("No station registered.")
        return display_business_menu()

    idx = integer_input("To delete a station, enter the associated integer", min=1, max=len(choices))
    choosen_station = choices[idx]

    # Confirm deletion

    display_title("Confirm DELETION")
    confirmation = input("Type 'delete' to confirm deletion of {} : ".format(choosen_station["name"]))
    
    if confirmation == 'delete':
        is_deleted = database.db_manage.delete_station(choosen_station["_id"])

        if is_deleted:
            display_title("Station deleted")
        else:
            display_title("Station not deleted")
    else:
        display_text("Abort deletion")
    
    input("Press ENTER to continue...")

    return display_business_menu()

def menu_deactivate_all_station_in_area():
    while True:
        lon = input("Enter longitude (3.048761 for ISEN Lille) : ")
        lat = input("Enter latitude (50.634206 for ISEN Lille) : ")
        try:
            lon_float = float(lon)
            lat_float = float(lat)
            break
        except Exception as e:
            display_text("Invalid choice, please try again.")

    range = integer_input("Enter the range in meter", 0, 1000000)
    
    result = database.db_manage.get_vlille_around(lon_float,lat_float,range)

    found = 0
    ids = []
    for station in result:
        found += 1
        ids.append(station["_id"])
        display_beautiful_dict(station)
    
    if not found:
        display_title("No station found.")
    else:
        display_title("Confirm DEACTIVATION")
    confirmation = input(f"Type 'deactivate' to confirm deactivation of {found} stations : ")
    
    if confirmation == 'deactivate':
        is_deleted = database.db_manage.deactivate_stations(ids)

        if is_deleted:
            display_title("Stations deactivated")
        else:
            display_title("Stations not deactivate")
    else:
        display_text("Abort deactivation")

        input("Press ENTER to continue...")

    return display_business_menu()

def give_stations_under_ratio():

    result = database.db_manage.get_stations_under_ratio()
    
    size = 0
    for doc in result:
        size += 1
        display_beautiful_dict(doc)
    
    display_text(f"Stations under ratio (found {size}) displayed (sorted by date).")
    input("Press ENTER to continue...")

    display_title("Task completed")
    
    return display_business_menu()


if __name__ == "__main__":
    setupLogger()
    database.db_manage.init_vlille_data()
    database.db_manage.update_vlille_data()
    display_business_menu()