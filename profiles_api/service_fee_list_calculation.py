import datetime
from datetime import date
import jsonschema
from jsonschema import validate

from profiles_api import test_service_fee_calculation as test_sfc

_FEE_LIST_JSON_KEY = ("name", "value", "from", "to")

# Service_Fee_List
def find_key(key,dict):
    if dict["name"] == key:
        return True
    else:
        return False

# Describe what kind of json you expect.
FeeListSchema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "value": {"type": "number"},
        "from": {"type": "string"},
    },
}

def validate_Json(jsonData):
    try:
        validate(instance=jsonData, schema=FeeListSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


def validate_Json_key(jsondata):
    """Handles checking Service Fee List json data is valid"""
    error_msg = ""
    jsondata_valid = True
    for city in jsondata.keys():
        if city not in test_sfc._CITY_LIST:
            jsondata_valid = False
            error_msg = error_msg + "city code: " + city + " does NOT exist!"
        city_data = jsondata.get(city)
        for service_code in city_data.keys():
            code_items =  service_code.split("_")
            if code_items[0] not in test_sfc._SERVICE_TYPE_LIST:
                jsondata_valid = False
                error_msg = error_msg + "service type code: " + code_items[0] + " does NOT exist!"
            if code_items[1] not in test_sfc._PRODUCT_LIST:
                jsondata_valid = False
                error_msg = error_msg + "product code: " + code_items[1] + " does NOT exist!"
            if city == "079":
                service_code_list =  test_sfc._DEFAUT_SERVICE_CODE_LIST.get(city)
            else:
                service_code_list =  test_sfc._DEFAUT_SERVICE_CODE_LIST.get("others")
            if service_code_list != None:
                fee_name_list = service_code_list.get(code_items[1])
                new_fee_list = []
                if fee_name_list != None:
                    for key in city_data.get(service_code).keys():
                        if key not in fee_name_list:
                            jsondata_valid = False
                            error_msg = error_msg + "Fee Name: " + city + " - " + key + " does NOT exist! " + code_items[1] + "fee_name_list: " + str(fee_name_list) + "service_code_list: " + str(service_code_list)
                    if jsondata_valid:
                        for key in fee_name_list:
                            if key not in city_data.get(service_code).keys():
                                jsondata_valid = False
                                error_msg = error_msg + "Fee Name: " + key + " NOT in new fee list!"

    return error_msg, jsondata_valid


def from_later_than_to(old_day, new_day):
    olds = str(old_day).split('-')
    oldday = date(int(olds[0]), int(olds[1]), int(olds[2]))
    news = str(new_day).split('-')
    newday = date(int(news[0]), int(news[1]), int(news[2]))
    return newday < oldday


def get_active_city(fee_data):
    active_city = []
    for city in fee_data.keys():
        active_city.append(city)

    return active_city


def match_active_city(new_city_active, old_city_active):
    for x in new_city_active:
        if x in old_city_active:
            return True

    return False


def check_fee_list_duplication(fee_data,feedatalist, except_id):
    #feedatalist.reverse()
    error_msg = ""
    error_found = False
    new_city_active = get_active_city(fee_data)
    for this_item in reversed(feedatalist):
        if this_item.get("id") != except_id and this_item.get("active"):
            old_city_active = get_active_city(this_item.get("fee_list"))
            if match_active_city(new_city_active, old_city_active):
                error_found = True
                error_msg = "Fee list city: " + str(new_city_active) + " matches with id: " + str(this_item.get("id")) + "!"
                return error_found, error_msg

    return error_found, error_msg
