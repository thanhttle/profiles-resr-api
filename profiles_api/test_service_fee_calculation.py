import json
import jsonfield
import datetime
from datetime import date, timedelta
from datetime import time
import jsonschema
from jsonschema import validate

import math

_SPECIAL_DAYS = {
    "2022":{
        "LNY":["2022-01-31","2022-02-01","2022-02-02","2022-02-03","2022-02-04","2022-02-05"],
        "BLNY":["2022-01-30","2022-01-29","2022-01-28"],
        "ALNY":["2022-02-06","2022-02-07","2022-02-08"],
        "HOL":["2022-01-01","2022-01-02","2022-01-03","2022-04-10","2022-04-11","2022-04-30","2022-05-01","2022-05-02","2022-05-03","2022-09-01","2022-09-02","2022-12-31"]
    },
    "2023":{
        "LNY":["2023-01-20","2023-01-21","2023-01-22","2023-01-23","2023-01-24","2023-01-25","2023-01-26"],
        "BLNY":["2023-01-10","2023-01-11","2023-01-12","2023-01-13","2023-01-14","2023-01-15","2023-01-16","2023-01-17","2023-01-18","2023-01-19"],
        "ALNY":["2023-01-27","2023-01-28","2023-01-29","2023-01-30","2023-01-31","2023-02-01","2023-02-02","2023-02-03","2023-02-04","2023-02-05"],
        "HOL":["2023-01-01","2023-01-02","2023-04-29","2023-04-30","2023-05-01","2023-05-02","2023-09-02","2023-09-03","2023-09-04","2023-12-31"]
    }
}

_CITY_LIST = ('001','079','048','031','092','001','002','004','006','008','010',
'011','012','014','015','017','019','020','022','024','025','026','027',
'030','033','034','035','036','037','038','040','042','044','045','046','049',
'051','052','054','056','058','060','062','064','064','066','067','068','070',
'072','074','075','077','080','082','083','084','086','087','089','091','093',
'095','094','096')
_AREA_LIST = ('I','II','III')
_PRODUCT_LIST = ('Shopping','PestControl','DeepConstruction','Elderly','Patient','Child','HomeBasic',
'Spiderman','PC','OfficeBasic','AC','Sofa','DeepHome','Basic')
_SERVICE_TYPE_LIST = ('O','S','Q')
_HOUSE_TYPE_LIST = ("apartment/single-story house", "building/multi-storey house", "villa",  "office")
_TOTAL_AREA_LIST = ("< 50m2", "50m2 - 90m2", "90m2 - 140m2", "140m2 - 255m2", "255m2 - 500m2", "500m2 - 1000m2")
_DEFAUT_FEE_LIST = {
    "079": {
        "O_Basic":{
            "I_P4h":69000,
            "I_P3h":73000,
            "I_P2h":88000,
            "II_P4h":69000,
            "II_P3h":73000,
            "II_P2h":88000,
            "III_P4h":76000,
            "III_P3h":80000,
            "III_P2h":96000,
            "OOH": 0.17,
            "WKD":0.17,
            "HOL": 0.17,
            "LNY":1.0,
            "BLNY":0.65,
            "ALNY":0.60,
            "OwnTools":30000,
            "Urgent":20000
        },
        "S_Basic":{
            "I_P4h":69000,
            "I_P3h":73000,
            "I_P2h":88000,
            "II_P4h":69000,
            "II_P3h":73000,
            "II_P2h":88000,
            "III_P4h":76000,
            "III_P3h":80000,
            "III_P2h":96000,
            "OOH": 0.17,
            "WKD":0.17,
            "HOL": 0.17,
            "LNY":1.0,
            "BLNY":0.65,
            "ALNY":0.60,
            "OwnTools":30000,
            "Urgent":20000
        },
        "O_DeepHome":{
            "I_P4h":90000,
            "II_P4h":85000,
            "III_P4h":100000,
            "OOH":0.2,
            "WKD":0.2,
            "HOL":2,
            "LNY":3,
            "BLNY":1.65,
            "ALNY":1.2,
            "Urgent":20000
        },
        "O_Sofa":{
            "Cotton1-Seat":370000,
            "Cotton2-Seat":440000,
            "Cotton3-Seat":580000,
            "CottonStool":50000,
            "Leather1-Seat":420000,
            "Leather2-Seat":480000,
            "Leather3-Seat":620000,
            "LeatherRecliner":290000,
            "LeatherStool":60000,
            "OOH":0.2,
            "WKD":0.2,
            "HOL":2,
            "LNY":3,
            "BLNY":1.65,
            "ALNY":1.2,
            "Urgent":20000
        }
    }
}
_Sofa_Duration = {
    "Cotton1-Seat":1.0,
    "Cotton2-Seat":1.5,
    "Cotton3-Seat":2.0,
    "CottonStool":0.25,
    "Leather1-Seat":1.0,
    "Leather2-Seat":1.5,
    "Leather3-Seat":2.0,
    "LeatherRecliner":0.5,
    "LeatherStool":0.25
}
_FEE_LIST_AVAILABLE = ("O_Basic_079","S_Basic_079","O_DeepHome_079","O_Sofa_079")
_DEFAUT_SERVICE_FEE_DETAILS = {"is_OutOfficeHours":False, "is_Weekend":False, "is_Holiday":False, "is_NewYear":False, "is_BeforeNewYear":False, "is_AfterNewYear":False, "is_OwnTools":False}
_WORK_DAY_LIST = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def get_servicecode_details(servicecode):
    servicecodelist = servicecode.split("_")
    city = servicecodelist[2]
    area = servicecodelist[3]
    servicename = servicecodelist[0] + "_" + servicecodelist[1]
    return servicename, city, area


# Service Fee calculation
def get_base_rate(area, duration, feelist):
    fee_detail = {}
    base_rate = 0
    if duration == 2:
        basename = area + "_" + "P2h"
        fee_detail["is_P2h"] = True
    elif duration == 3:
        basename = area + "_" + "P3h"
        fee_detail["is_P3h"] = True
    elif duration >= 4:
        basename = area + "_" + "P4h"
    else:
        return {"base_rate": 0,"fee_detail": fee_detail}
    base_rate = feelist[basename]

    #return {"base_rate": base_rate,"fee_detail": fee_detail}
    return base_rate, fee_detail


def is_weekend(bookdate):
	days = str(bookdate).split('-')
	d = date(int(days[0]), int(days[1]), int(days[2]))

	return d.weekday() > 4


def is_OutOfWorkingHour(starttime):
	timelist = str(starttime).split(":")
	time_formated = time(int(timelist[0]),int(timelist[1]),int(timelist[2]))
	return time_formated < time(8,0,0) or time_formated >= time(18,0,0)


def check_valid_input(city,area,servicename,duration,propertydetails,subscription_schedule_details):
    error_messagge = ""
    if city not in _CITY_LIST:
        error_messagge  = error_messagge + "INVALID city code; "
    if area not in _AREA_LIST:
        error_messagge  = error_messagge + "INVALID area code; "
    fee_available = servicename + "_" + city
    if fee_available not in _FEE_LIST_AVAILABLE:
        error_messagge  = error_messagge + "INVALID service code or Fee List for " + fee_available + " NOT yet availabble"

    error_propertydetails = False
    error_messagge_propertydetails = ""
    if servicename == "O_Basic" or servicename == "O_DeepHome" or servicename == "S_Basic":
        if propertydetails == None or json.dumps(propertydetails) == "{}":
            error_messagge_propertydetails  = "propertydetails is " + json.dumps(propertydetails) + "; "
            error_propertydetails = True
        else:
            if propertydetails["housetype"] == None:
                housetype = "None"
            else:
                housetype = propertydetails["housetype"]
            if propertydetails["totalarea"] == None:
                totalarea = "None"
            else:
                totalarea = propertydetails["totalarea"]
            if housetype not in _HOUSE_TYPE_LIST:
                error_messagge_propertydetails  = "INVALID house type in propertydetails; "
            if totalarea not in _TOTAL_AREA_LIST:
                error_messagge_propertydetails  = "INVALID total area in propertydetails; "

    if servicename == "O_Basic" or servicename == "O_DeepHome":
        if duration == 0:
            if error_propertydetails == True:
                error_messagge  = error_messagge + "Duration = 0 and " + error_messagge_propertydetails
        elif duration < 6 and servicename == "O_DeepHome":
            error_messagge  = error_messagge + "Minimun duration for DeepHome Service is 6 hours; "
        elif duration < 2 and servicename == "O_Basic":
            error_messagge  = error_messagge + "Minimun duration for Basic Service is 2 hours; "

    elif servicename == "S_Basic":
        if subscription_schedule_details == None or json.dumps(subscription_schedule_details) == "{}":
            error_messagge  = error_messagge + "Subscription Service requires subscription_schedule_details. It's " + json.dumps(subscription_schedule_details)  + "; "
        else:
            if subscription_schedule_details.get("workingdays") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: working_ays empty;  "
            if subscription_schedule_details.get("workingtime") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: workingtime empty;  "
            if subscription_schedule_details.get("workingduration") == None:
                if error_propertydetails == True:
                    error_messagge  = error_messagge + "subscription_schedule_details: workingduration is required when propertydetails empty;  "
            else:
                workingduration = subscription_schedule_details.get("workingduration")
                if workingduration == 0:
                    if error_propertydetails == True:
                        error_messagge  = error_messagge + "subscription_schedule_details: workingduration is required when propertydetails empty;  "
                elif workingduration < 2:
                    error_messagge  = error_messagge + "Minimun duration for Subscription Service is 2 hours; "
            if subscription_schedule_details.get("startdate") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: startdate empty;  "
            if subscription_schedule_details.get("enddate") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: enddate empty;  "
            if subscription_schedule_details.get("workingdays") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: workingdays empty;  "
            else:
                workingdays = subscription_schedule_details.get("workingdays")
                for wday in workingdays:
                    if wday not in _WORK_DAY_LIST:
                        error_messagge  = error_messagge + "subscription_schedule_details: workingdays INVALID;  "

    elif servicename == "O_Sofa":
        if propertydetails.get("withpets") == None:
            withpets = False
        else:
            withpets = propertydetails.get("withpets")
        number_of_services = 6

        if propertydetails.get("curtainswaterwashing") == None:
            number_of_services -= 1
        else:
            curtainswaterwashing = propertydetails.get("curtainswaterwashing")
            if curtainswaterwashing != "< 10kg" and curtainswaterwashing != "10kg – 15kg":
                str_value = curtainswaterwashing.strip("kg")
                try:
                    num = int(str_value)
                    if num <= 15:
                        error_messagge  = error_messagge + "curtainswaterwashing: number must be > 15kg"
                except ValueError as ex:
                    error_messagge  = error_messagge + "curtainswaterwashing " + str(curtainswaterwashing) + ": " + str(ex)
            error_messagge  = error_messagge + "curtainswaterwashing: currently unavailable; "

        if propertydetails.get("cottonsofacleaning") == None:
            number_of_services -= 1
        else:
            cottonsofacleaning = propertydetails.get("cottonsofacleaning")
            if cottonsofacleaning.get("1-seatsofa") == None:
                if cottonsofacleaning.get("2-seatsofa") == None:
                    if cottonsofacleaning.get("3-seatsofa") == None:
                        if cottonsofacleaning.get("stool") == None:
                            error_messagge  = error_messagge + "Details for cottonsofacleaning is empty in propertydetails; "

        if propertydetails.get("leathersofacleaning") == None:
            number_of_services -= 1
        else:
            leathersofacleaning = propertydetails.get("leathersofacleaning")
            if leathersofacleaning.get("1-seatsofa") == None:
                if leathersofacleaning.get("2-seatsofa") == None:
                    if leathersofacleaning.get("3-seatsofa") == None:
                        if leathersofacleaning.get("recliner") == None:
                            if leathersofacleaning.get("stool") == None:
                                error_messagge  = error_messagge + "Details for leathersofacleaning is empty in propertydetails; "

        if propertydetails.get("mattresscleaning") == None:
            number_of_services -= 1
        else:
            error_messagge  = error_messagge + "mattresscleaning: currently unavailable; "

        if propertydetails.get("carpetcleaning") == None:
            number_of_services -= 1
        else:
            error_messagge  = error_messagge + "carpetcleaning: currently unavailable; "

        if propertydetails.get("curtainsdrycleaning") == None:
            number_of_services -= 1
        else:
            error_messagge  = error_messagge + "curtainsdrycleaning: currently unavailable; "

        if number_of_services <= 0:
            error_messagge  = error_messagge + "Details for ServideCode " + servicename + " is empty in propertydetails; "

    return error_messagge


def get_estimated_duration_for_cleaning(ironingclothes, propertydetails):
    """Estimation for Cleaning Service"""
    estimatedduration = 0.0

    if propertydetails.get("housetype") != None:
        housetype = propertydetails.get("housetype")

        if propertydetails.get("numberoffloors") == None:
            numberoffloors = 1
        else:
            numberoffloors = propertydetails.get("numberoffloors")

        if propertydetails.get("numberoffbedroom") == None:
            numberoffbedroom = 0
        else:
            numberoffbedroom = propertydetails.get("numberoffbedroom")

        if propertydetails.get("numberofflivingroom") == None:
            numberofflivingroom = 0
        else:
            numberofflivingroom = propertydetails.get("numberofflivingroom")

        if propertydetails.get("numberoffkitchen") == None:
            numberoffkitchen = 0
        else:
            numberoffkitchen = propertydetails.get("numberoffkitchen")

        if propertydetails.get("numberoffofficeroom") == None:
            numberoffofficeroom = 0
        else:
            numberoffofficeroom = propertydetails.get("numberoffofficeroom")

        if propertydetails.get("numberoffbathroom") == None:
            numberoffbathroom = 0
        else:
            numberoffbathroom = propertydetails.get("numberoffbathroom")

        if propertydetails.get("totalarea") == None:
            totalarea = "None"
        else:
            totalarea = propertydetails.get("totalarea")

        estimatedduration = estimatedduration + numberoffbedroom * 0.5
        estimatedduration = estimatedduration + numberofflivingroom * 0.5
        estimatedduration = estimatedduration + numberoffkitchen * 0.5
        estimatedduration = estimatedduration + numberoffofficeroom * 0.5
        estimatedduration = estimatedduration + numberoffbathroom * 0.3
        if housetype == "building/multi-storey house":
            estimatedduration = estimatedduration + 0.5
        if ironingclothes:
            estimatedduration = estimatedduration + 0.5

        # Check min for estimatedduration
        if estimatedduration < 12.0 and totalarea == "500m2 - 1000m2":
            estimatedduration = 12.0
        elif estimatedduration < 7.0 and totalarea == "255m2 - 500m2":
            estimatedduration = 7.0
        elif estimatedduration < 4.0 and totalarea == "140m2 - 255m2":
            estimatedduration = 4.0
        elif estimatedduration < 3.0 and totalarea == "90m2 - 140m2":
            estimatedduration = 3.0
        elif estimatedduration < 3.0 and housetype == "villa":
            estimatedduration = 3.0
        elif estimatedduration < 3.0 and numberoffbedroom >= 3:
            estimatedduration = 3.0

        # Check max for estimatedduration
        if estimatedduration > 3.0 and (totalarea == "< 50m2" or totalarea == "50m2 - 90m2"):
            estimatedduration = 3.0

    # Add 0.5 hours if withpets
    if propertydetails.get("withpets") == None:
        withpets = False
    else:
        withpets = propertydetails.get("withpets")
    if withpets:
        estimatedduration = estimatedduration + 0.5

    # Minimum serbvice is 2 hours
    if estimatedduration < 2.0:
        estimatedduration = 2.0

    return math.ceil(estimatedduration)

def get_estimated_duration_for_DeepHome(ironingclothes, propertydetails):
    """Estimation for Cleaning Service"""
    estimatedduration = 0.0

    if propertydetails.get("housetype") != None:

        housetype = propertydetails.get("housetype")

        if propertydetails.get("numberoffloors") == None:
            numberoffloors = 1
        else:
            numberoffloors = propertydetails.get("numberoffloors")

        if propertydetails.get("numberoffbedroom") == None:
            numberoffbedroom = 0
        else:
            numberoffbedroom = propertydetails.get("numberoffbedroom")

        if propertydetails.get("numberofflivingroom") == None:
            numberofflivingroom = 0
        else:
            numberofflivingroom = propertydetails.get("numberofflivingroom")

        if propertydetails.get("numberoffkitchen") == None:
            numberoffkitchen = 0
        else:
            numberoffkitchen = propertydetails.get("numberoffkitchen")

        if propertydetails.get("numberoffofficeroom") == None:
            numberoffofficeroom = 0
        else:
            numberoffofficeroom = propertydetails.get("numberoffofficeroom")

        if propertydetails.get("numberoffbathroom") == None:
            numberoffbathroom = 0
        else:
            numberoffbathroom = propertydetails.get("numberoffbathroom")

        if propertydetails.get("totalarea") == None:
            totalarea = "None"
        else:
            totalarea = propertydetails.get("totalarea")

        # Check min for estimatedduration
        if estimatedduration < 64.0 and totalarea == "500m2 - 1000m2":
            estimatedduration = 64.0
        elif estimatedduration < 32.0 and totalarea == "255m2 - 500m2":
            estimatedduration = 32.0
        elif estimatedduration < 16.0 and totalarea == "140m2 - 255m2":
            estimatedduration = 16.0
        elif estimatedduration < 12.0 and totalarea == "90m2 - 140m2":
            estimatedduration = 12.0
        elif estimatedduration < 8.0 and totalarea == "50m2 - 90m2":
            estimatedduration = 8.0
        elif estimatedduration < 6.0 and totalarea == "< 50m2":
            estimatedduration = 6.0

    # Minimum serbvice is 2 hours
    if estimatedduration < 6.0:
        estimatedduration = 6.0

    return math.ceil(estimatedduration)


def get_estimated_fee_cottonsofacleaning(propertydetails,feelist,adjust_rate):
    estimatedfee = 0.0
    details_response = {}
    fee_details_response = {}
    estimatedduration = 0.0

    if propertydetails.get("cottonsofacleaning") != None:
        cottonsofacleaning = propertydetails.get("cottonsofacleaning")
        if cottonsofacleaning.get("1-seatsofa") != None:
            one_seatsofa = cottonsofacleaning.get("1-seatsofa")
            one_seatsofa_fee =  int(one_seatsofa * feelist["Cotton1-Seat"] * adjust_rate)
            estimatedfee = estimatedfee + one_seatsofa_fee
            one_seatsofa_response = {"1-Seat Cotton Sofa":one_seatsofa_fee}
            details_response.update(one_seatsofa_response)
            estimatedduration += _Sofa_Duration["Cotton1-Seat"] * one_seatsofa
        if cottonsofacleaning.get("2-seatsofa") != None:
            two_seatsofa = cottonsofacleaning.get("2-seatsofa")
            two_seatsofa_fee =  int(two_seatsofa * feelist["Cotton2-Seat"] * adjust_rate)
            estimatedfee = estimatedfee + two_seatsofa_fee
            two_seatsofa_response = {"2-Seat Cotton Sofa":two_seatsofa_fee}
            details_response.update(two_seatsofa_response)
            estimatedduration += _Sofa_Duration["Cotton2-Seat"] * two_seatsofa
        if cottonsofacleaning.get("3-seatsofa") != None:
            three_seatsofa = cottonsofacleaning.get("3-seatsofa")
            three_seatsofa_fee =  int(three_seatsofa * feelist["Cotton3-Seat"] * adjust_rate)
            estimatedfee = estimatedfee + three_seatsofa_fee
            three_seatsofa_response = {"3-Seat Cotton Sofa":three_seatsofa_fee}
            details_response.update(three_seatsofa_response)
            estimatedduration += _Sofa_Duration["Cotton3-Seat"] * three_seatsofa
        if cottonsofacleaning.get("stool") != None:
            stool = cottonsofacleaning.get("stool")
            stool_fee =  int(stool * feelist["CottonStool"] * adjust_rate)
            estimatedfee = estimatedfee + stool_fee
            stool_response = {"Cotton Stool":stool_fee}
            details_response.update(stool_response)
            estimatedduration += _Sofa_Duration["CottonStool"] * stool

        if estimatedfee > 0:
            fee_details_response = {"Cotton Sofa":{"Cleaning Fee":int(estimatedfee),"Details":details_response}}
    return estimatedfee, fee_details_response, estimatedduration


def get_estimated_fee_leathersofacleaning(propertydetails,feelist,adjust_rate):
    estimatedfee = 0.0
    details_response = {}
    fee_details_response = {}
    estimatedduration = 0.0

    if propertydetails.get("leathersofacleaning") != None:
        leathersofacleaning = propertydetails.get("leathersofacleaning")
        if leathersofacleaning.get("1-seatsofa") != None:
            one_seatsofa = leathersofacleaning.get("1-seatsofa")
            one_seatsofa_fee =  int(one_seatsofa * feelist["Leather1-Seat"] * adjust_rate)
            estimatedfee = estimatedfee + one_seatsofa_fee
            one_seatsofa_response = {"1-Seat Cotton Sofa":one_seatsofa_fee}
            details_response.update(one_seatsofa_response)
            estimatedduration += _Sofa_Duration["Leather1-Seat"] * one_seatsofa
        if leathersofacleaning.get("2-seatsofa") != None:
            two_seatsofa = leathersofacleaning.get("2-seatsofa")
            two_seatsofa_fee =  int(two_seatsofa * feelist["Leather2-Seat"] * adjust_rate)
            estimatedfee = estimatedfee + two_seatsofa_fee
            two_seatsofa_response = {"2-Seat Cotton Sofa":two_seatsofa_fee}
            details_response.update(two_seatsofa_response)
            estimatedduration += _Sofa_Duration["Leather2-Seat"] * two_seatsofa
        if leathersofacleaning.get("3-seatsofa") != None:
            three_seatsofa = leathersofacleaning.get("3-seatsofa")
            three_seatsofa_fee =  int(three_seatsofa * feelist["Leather3-Seat"] *  adjust_rate)
            estimatedfee = estimatedfee + three_seatsofa_fee
            three_seatsofa_response = {"3-Seat Cotton Sofa":three_seatsofa_fee}
            details_response.update(three_seatsofa_response)
            estimatedduration += _Sofa_Duration["Leather3-Seat"] * three_seatsofa
        if leathersofacleaning.get("recliner") != None:
            recliner = leathersofacleaning.get("recliner")
            recliner_fee =  int(recliner * feelist["LeatherRecliner"] * adjust_rate)
            estimatedfee = estimatedfee + recliner_fee
            recliner_response = {"Cotton Recliner":recliner_fee}
            details_response.update(recliner_response)
            estimatedduration += _Sofa_Duration["LeatherRecliner"] * recliner
        if leathersofacleaning.get("stool") != None:
            stool = leathersofacleaning.get("stool")
            stool_fee =  int(stool * feelist["LeatherStool"] * adjust_rate)
            estimatedfee = estimatedfee + stool_fee
            stool_response = {"Cotton Stool":stool_fee}
            details_response.update(stool_response)
            estimatedduration += _Sofa_Duration["LeatherStool"] * stool

        if estimatedfee > 0:
            fee_details_response = {"Leather Sofa":{"Cleaning Fee":int(estimatedfee),"Details":details_response}}
    return estimatedfee, fee_details_response, estimatedduration


def get_estimated_fee_mattresscleaning(propertydetails,feelist):
    estimatedfee = 0.0
    details_response = {}
    fee_details_response = {}

    if propertydetails.get("mattresscleaning") != None:
        mattresscleaning = propertydetails.get("mattresscleaning")
        if mattresscleaning.get("< 1.5m") == None:
            less_than_onefive = 0
        else:
            less_than_onefive = mattresscleaning.get("< 1.5m")
        if mattresscleaning.get("1.5m - 1.8m") == None:
            onefive_to_oneeight = 0
        else:
            onefive_to_oneeight = mattresscleaning.get("1.5m - 1.8m")
        if mattresscleaning.get("> 1.8m") == None:
            more_than_oneeight = 0
        else:
            more_than_oneeight = mattresscleaning.get("> 1.8m")

    return estimatedfee, fee_details_response


def get_estimated_fee_carpetcleaning(propertydetails,feelist):
    estimatedfee = 0.0
    details_response = {}
    fee_details_response = {}

    if propertydetails.get("carpetcleaning") != None:
        carpetcleaning = propertydetails.get("carpetcleaning")
        if carpetcleaning.get("< 1.5m") == None:
            less_than_onefive = 0
        else:
            less_than_onefive = carpetcleaning.get("< 1.5m")
        if carpetcleaning.get("1.5m - 1.8m") == None:
            onefive_to_oneeight = 0
        else:
            onefive_to_oneeight = carpetcleaning.get("1.5m - 1.8m")

    return estimatedfee, fee_details_response


def get_estimated_fee_curtainsdrycleaning(propertydetails,feelist):
    estimatedfee = 0.0
    details_response = {}
    fee_details_response = {}

    if propertydetails.get("curtainsdrycleaning") != None:
        curtainsdrycleaning = propertydetails.get("curtainsdrycleaning")
        if curtainsdrycleaning.get("numberoffbedroom") == None:
            numberoffbedroom = 0
        else:
            numberoffbedroom = curtainsdrycleaning.get("numberoffbedroom")
        if curtainsdrycleaning.get("numberofflivingroom") == None:
            numberofflivingroom = 0
        else:
            numberofflivingroom = curtainsdrycleaning.get("numberofflivingroom")

    return estimatedfee, fee_details_response


def get_estimated_fee_curtainswaterwashing(propertydetails,feelist):
    estimatedfee = 0.0
    details_response = {}
    fee_details_response = {}

    if propertydetails.get("curtainswaterwashing") != None:
        curtainswaterwashing = propertydetails.get("curtainswaterwashing")
        if curtainswaterwashing == "< 10kg":
            estimate = 2
        elif curtainswaterwashing == "10kg – 15kg":
            estimate = 3
        else:
            num = int(curtainswaterwashing.strip("kg"))
            estimate = 4 + (num - 15)/5

    return estimatedfee, fee_details_response


def get_estimated_fee_sofacleaning(bookdate,starttime,propertydetails,urgentbooking,feelist):
    estimatedfee = 0.0;
    estimatedduration = 0.0
    fee_details_response = {"Total Fee": int(estimatedfee), "Estimated Duration": math.ceil(estimatedduration)}

    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,feelist)
    adjust_rate = 1 + extra_fee_percent

    if urgentbooking:
        urgentbooking_fee = feelist["Urgent"]
        estimatedfee += urgentbooking_fee
        urgentbooking_fee_response = {"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)

    cotton_sofa_fee, cotton_sofa_response, cotton_duration = get_estimated_fee_cottonsofacleaning(propertydetails,feelist,adjust_rate)
    if cotton_sofa_fee > 0:
        estimatedfee = estimatedfee + cotton_sofa_fee
        fee_details_response.update(cotton_sofa_response)
        estimatedduration  = estimatedduration + cotton_duration

    leather_sofa_fee, leather_sofa_response, leather_duration = get_estimated_fee_leathersofacleaning(propertydetails,feelist,adjust_rate)
    if leather_sofa_fee > 0:
        estimatedfee = estimatedfee + leather_sofa_fee
        fee_details_response.update(leather_sofa_response)
        estimatedduration  = estimatedduration + leather_duration

    mattress_fee, mattress_response = get_estimated_fee_mattresscleaning(propertydetails,feelist)
    if mattress_fee > 0:
        estimatedfee = estimatedfee + mattress_fee
        fee_details_response.update(mattress_response)

    carpet_fee, carpet_response = get_estimated_fee_carpetcleaning(propertydetails,feelist)
    if carpet_fee > 0:
        estimatedfee = estimatedfee + carpet_fee
        fee_details_response.update(carpet_response)

    curtainsdrycleaning_fee, curtainsdrycleaning_response = get_estimated_fee_curtainsdrycleaning(propertydetails,feelist)
    if curtainsdrycleaning_fee > 0:
        estimatedfee = estimatedfee + curtainsdrycleaning_fee
        fee_details_response.update(curtainsdrycleaning_response)

    curtainswaterwashing_fee, curtainswaterwashing_response = get_estimated_fee_curtainswaterwashing(propertydetails,feelist)
    if curtainswaterwashing_fee > 0:
        estimatedfee = estimatedfee + curtainswaterwashing_fee
        fee_details_response.update(curtainswaterwashing_response)

    # Minimum serbvice is 2 hours
    if estimatedfee < 500000:
        estimatedfee = 500000
        minimum_response = {"Minimum Fee Applied": True}
        fee_details_response.update(minimum_response)

    total_fee_response = {"Total Fee": int(estimatedfee), "Estimated Duration": round(estimatedduration,1)}
    fee_details_response.update(total_fee_response)

    if extra_fee_percent > 0.0:
        extra_service_fee_response = {"Extra Service Fee Details": extra_service_fee_details}
        fee_details_response.update(extra_service_fee_response)

    return fee_details_response


def get_estimated_duration(ironingclothes, propertydetails,subscription_schedule_details, servicename):
    estimatedduration = 0.0

    if servicename == "O_Basic":
        estimatedduration  = get_estimated_duration_for_cleaning(ironingclothes, propertydetails)
    elif servicename == "S_Basic":
        if propertydetails != None and json.dumps(propertydetails) != "{}":
            estimatedduration  = get_estimated_duration_for_cleaning(ironingclothes, propertydetails)
        elif subscription_schedule_details != None:
            estimatedduration = subscription_schedule_details.get("workingduration")
        else:
            estimatedduration = 0.0
    elif servicename == "O_DeepHome":
        estimatedduration = get_estimated_duration_for_DeepHome(ironingclothes, propertydetails)

    return math.ceil(estimatedduration)


def get_year(date):
    date_list = str(date).split('-')
    return str(date_list[0])

def extra_fee_special_day_new(bookdate, starttime, feelist):
    """Calculates additional fee based on date & time of booking"""

    fee_detail = {}
    extra_fee = 0.0
    bookdate = str(bookdate)
    year = get_year(bookdate)
    special_day_of_year = _SPECIAL_DAYS.get(year)
    LNY  = special_day_of_year.get("LNY")
    BLNY  = special_day_of_year.get("BLNY")
    ALNY  = special_day_of_year.get("ALNY")
    HOL  = special_day_of_year.get("HOL")
    if bookdate in LNY:
        fee_detail["is_NewYear"] = True
        extra_fee += feelist["LNY"]
        index = 1
    elif bookdate in BLNY:
        fee_detail["is_BeforeNewYear"] = True
        extra_fee += feelist["BLNY"]
        index = 2
    elif bookdate in ALNY:
        fee_detail["is_AfterNewYear"] = True
        extra_fee += feelist["ALNY"]
        index = 3
    elif bookdate in HOL:
        fee_detail["is_Holiday"] = True
        extra_fee += feelist["HOL"]
        index = 4
    elif is_weekend(bookdate):
        fee_detail["is_Weekend"] = True
        extra_fee += feelist["WKD"]
        index = 5
    elif is_OutOfWorkingHour(starttime):
        fee_detail["is_OutOfficeHours"] = True
        extra_fee += feelist["OOH"]
        index = 6
    else:
        index = 0

    return extra_fee, fee_detail, index


def  get_Oneday_Basic_fee_details(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,fee_detail):
    """Get fee of the service"""
    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,service_fee_list)
    final_rate = base_rate * (1 + extra_fee_percent)
    total_fee = final_rate * usedduration

    if owntool == True:
        total_fee += service_fee_list["OwnTools"]

    return int(total_fee), index, final_rate


def  get_O_Basic_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,urgentbooking,fee_detail):
    """Get fee details of the service"""
    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,service_fee_list)
    final_rate = base_rate * (1 + extra_fee_percent)
    total_fee = final_rate * usedduration

    fee_details_response = {}
    if owntool == True:
        total_fee += service_fee_list["OwnTools"]
        extra_service_fee_details["is_OwnTools"] = True
        fee_details_response = {"Total Fee": int(total_fee),"OwnTools Fee":service_fee_list["OwnTools"]}
    else:
        fee_details_response = {"Total Fee": int(total_fee)}

    if urgentbooking:
        urgentbooking_fee = service_fee_list["Urgent"]
        total_fee += urgentbooking_fee
        urgentbooking_fee_response = {"Total Fee": int(total_fee),"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)

    if ironingclothes == True:
        ironingclothes_fee = final_rate * 0.5
        ironingclothes_fee_response = {"Ironing Clothes Fee": int(ironingclothes_fee)}
        fee_details_response.update(ironingclothes_fee_response)

    extra_service_fee_details.update(fee_detail)
    extra_service_fee_response = {"Extra Service Fee Details": extra_service_fee_details}

    if duration == 0:
        estimatedduration_response = {"Estimated Duration": estimatedduration}
        fee_details_response.update(estimatedduration_response)

    fee_details_response.update(extra_service_fee_response)

    return fee_details_response


def  get_O_DeepHome_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,urgentbooking,fee_detail):
    """Get fee details of the DeepHome service"""
    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,service_fee_list)
    final_rate = base_rate * (1 + extra_fee_percent)
    total_fee = final_rate * usedduration

    fee_details_response = {"Total Fee": int(total_fee)}

    if urgentbooking:
        urgentbooking_fee = service_fee_list["Urgent"]
        total_fee += urgentbooking_fee
        urgentbooking_fee_response = {"Total Fee": int(total_fee),"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)

    if ironingclothes == True:
        ironingclothes_fee = final_rate
        ironingclothes_fee_response = {"Ironing Clothes Fee": int(ironingclothes_fee)}
        fee_details_response.update(ironingclothes_fee_response)

    extra_service_fee_details.update(fee_detail)
    extra_service_fee_response = {"Extra Service Fee Details": extra_service_fee_details}

    if duration == 0:
        sugggested_shift = 4
        if estimatedduration != sugggested_shift * int(estimatedduration/sugggested_shift):
            sugggested_shift = 3
        estimatedduration_response = {"Estimated Duration": estimatedduration,"Suggested Number of hours per Shift":sugggested_shift,"Suggest Number of Workers":int(estimatedduration/sugggested_shift)}
        fee_details_response.update(estimatedduration_response)

    fee_details_response.update(extra_service_fee_response)
    return fee_details_response


def get_formated_day(dateTimeInstance):
	dateTimeInstance_List = str(dateTimeInstance).split('-')
	formated_day = date(int(dateTimeInstance_List[0]), int(dateTimeInstance_List[1]), int(dateTimeInstance_List[2]))
	return formated_day


def get_weekday_value(workingdays):
    workingdays_weekday_value = []
    for wday in workingdays:
        for i in range(7):
            if wday == _WORK_DAY_LIST[i]:
                workingdays_weekday_value.append(i)
                break
    return workingdays_weekday_value


def get_number_of_day_before_next_weekday(workingdays_weekday_value):
    number_of_day_before_next_weekday = []
    list_len = len(workingdays_weekday_value)
    for i in range(list_len):
        if i + 1 < list_len:
            number_of_day = workingdays_weekday_value[i+1] - workingdays_weekday_value[i]
        else:
            number_of_day = 7 + workingdays_weekday_value[0] - workingdays_weekday_value[i]
        number_of_day_before_next_weekday.append(number_of_day)
    return number_of_day_before_next_weekday


def get_first_working_date(startdate_formatted,workingdays_weekday_value):
    startdate_formatted_weekday = startdate_formatted.weekday()
    next = True
    while next:
        for i in range(len(workingdays_weekday_value)):
            if startdate_formatted_weekday  < workingdays_weekday_value[i]:
                index = i
                actual_start_date = startdate_formatted + timedelta(days=workingdays_weekday_value[i] - startdate_formatted_weekday)
                next = False
                break
            elif startdate_formatted_weekday  == workingdays_weekday_value[i]:
                index = i
                actual_start_date = startdate_formatted
                next = False
                break
            elif startdate_formatted_weekday  > workingdays_weekday_value[i]:
                continue
        startdate_formatted_weekday = startdate_formatted_weekday - 7

    return index, actual_start_date


def  get_S_Basic_fee_details_response(subscription_schedule_details,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,urgentbooking,fee_detail):
    """Get fee details of the subscription service"""
    fee_details_response = {}
    workingdays = subscription_schedule_details.get("workingdays")
    workingtime = subscription_schedule_details.get("workingtime")
    workingduration = subscription_schedule_details.get("workingduration")
    startdate = subscription_schedule_details.get("startdate")
    enddate = subscription_schedule_details.get("enddate")

    workingdays_weekday_value = get_weekday_value(workingdays)
    number_of_day_before_next_weekday = get_number_of_day_before_next_weekday(workingdays_weekday_value)
    startdate_formatted  = get_formated_day(startdate)
    startdate_formatted_weekday = startdate_formatted.weekday()
    enddate_formatted  = get_formated_day(enddate)

    start_date_index, actual_start_date = get_first_working_date(startdate_formatted,workingdays_weekday_value)
    list_len = len(number_of_day_before_next_weekday)
    process_index = start_date_index
    process_date = actual_start_date
    total_fee = 0
    count = 0
    component_fee = [0,0,0,0,0,0,0]
    component_count = [0,0,0,0,0,0,0]
    while process_date <= enddate_formatted:
        oneday_fee, index, final_rate = get_Oneday_Basic_fee_details(process_date,workingtime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,fee_detail)
        total_fee = total_fee + oneday_fee
        count = count + 1
        component_fee[index] += oneday_fee
        component_count[index] += 1
        process_date = process_date + timedelta(days=number_of_day_before_next_weekday[process_index])
        process_index = process_index + 1
        if process_index == list_len:
            process_index = 0

    total_fee_response = {"Total Fee": total_fee}
    fee_details_response.update(total_fee_response)
    if urgentbooking:
        urgentbooking_fee = service_fee_list["Urgent"]
        total_fee += urgentbooking_fee
        urgentbooking_fee_response = {"Total Fee": int(total_fee),"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)

    total_workdays_response = {"Total Number of Work Days": count}
    fee_details_response.update(total_workdays_response)
    if duration == 0:
        estimatedduration_response = {"Duration per session": estimatedduration}
        fee_details_response.update(estimatedduration_response)
    if owntool == True:
        total_owntool_fee = count * service_fee_list["OwnTools"]
        total_owntool_response = {"Total OwnTools Fee": total_owntool_fee}
        fee_details_response.update(total_owntool_response)
    if ironingclothes == True:
        ironingclothes_fee = count * final_rate * 0.5
        ironingclothes_fee_response = {"Ironing Clothes Fee": int(ironingclothes_fee)}
        fee_details_response.update(ironingclothes_fee_response)
    if count > 0:
        details_fee_type = {}
        for i in range(7):
            if component_count[i] > 0:
                if i == 0:
                    normal_fee_response = {"Normal Fee":{"Total Days": component_count[0], "Sub Total Fee":component_fee[0]}}
                    details_fee_type.update(normal_fee_response)
                elif i == 1:
                    LNY_fee_response = {"Lunar New Year Fee":{"Total Days": component_count[1], "Sub Total Fee":component_fee[1]}}
                    details_fee_type.update(LNY_fee_response)
                elif i == 2:
                    BLNY_fee_response = {"Right Before Lunar New Year Fee":{"Total Days": component_count[2], "Sub Total Fee":component_fee[2]}}
                    details_fee_type.update(BLNY_fee_response)
                elif i == 3:
                    ALNY_fee_response = {"Right After Lunar New Year Fee":{"Total Days": component_count[3], "Sub Total Fee":component_fee[3]}}
                    details_fee_type.update(ALNY_fee_response)
                elif i == 4:
                    HOL_fee_response = {"Nation Holidays Fee":{"Total Days": component_count[4], "Sub Total Fee":component_fee[4]}}
                    details_fee_type.update(HOL_fee_response)
                elif i == 5:
                    WKD_fee_response = {"Weekend Fee":{"Total Days": component_count[5], "Sub Total Fee":component_fee[5]}}
                    details_fee_type.update(WKD_fee_response)
                elif i == 6:
                    OOH_fee_response = {"Out Of Office Hour Fee":{"Total Days": component_count[6], "Sub Total Fee":component_fee[6]}}
                    details_fee_type.update(OOH_fee_response)
        details_fee_type_response = {"Detailed Fees":details_fee_type}
        fee_details_response.update(details_fee_type_response)
        #component_fee_detail = {"component_fee_detail":str(component_fee),"component_count_detail":str(component_count)}
        #fee_details_response.update(component_fee_detail)

    return fee_details_response
