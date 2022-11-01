import datetime
from datetime import date
import jsonschema
from jsonschema import validate

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
    for x in jsondata.keys():
        if x not in _FEE_LIST_JSON_KEY:
            return False
    return True


def compare_dates(old_day, new_day):
    olds = str(old_day).split('-')
    oldday = date(int(olds[0]), int(olds[1]), int(olds[2]))
    news = str(new_day).split('-')
    newday = date(int(news[0]), int(news[1]), int(news[2]))
    return newday < oldday


def check_fee_list_duplication(fee_data,feedatalist):
    #feedatalist.reverse()
    error_msg = ""
    error_found = False
    for thisdict in reversed(feedatalist):
        if thisdict["fee_list"]["name"] == fee_data["name"]:
            if thisdict["fee_list"]["to"] == None:
                error_msg = error_msg + 'Duplicate Fee Name! Please use PATCH() method to update "to" key of ' + thisdict["fee_list"]["name"]
                error_msg = error_msg + ' in database before insert new one. '
                error_found = True
                return error_found, error_msg
            elif compare_dates(thisdict["fee_list"]["to"],fee_data["from"]):
                error_msg = "Duplicate Fee Name " + thisdict["fee_list"]["name"] + '! New "from" day ' + fee_data["from"] + ' must be later than old "to" day ' + thisdict["fee_list"]["to"] + '.'
                error_found = True
                return error_found, error_msg
    return error_found, error_msg
