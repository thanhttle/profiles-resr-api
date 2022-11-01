import json
import jsonfield
import datetime
from datetime import date
from datetime import time
import jsonschema
from jsonschema import validate

import math

_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-01-31","2022-02-01","2022-02-02","2022-02-03","2022-02-04","2022-02-05")
_BEFORE_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-01-30","2022-01-29","2022-01-28")
_AFTER_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-02-06","2022-02-07","2022-02-08")
_OTHER_NATIONAL_HOLIDAY_DAYS_2022 = ("2022-01-01","2022-01-02","2022-01-03","2022-04-10","2022-04-11","2022-04-30","2022-05-01","2022-05-02","2022-05-03","2022-09-01","2022-09-02")
_OTHER_NATIONAL_HOLIDAY_NAMES = ("International New Year's Day","New Year's Day Holiday","Day off for International New Year's Day","Hung Kings Festival","Day off for Hung Kings Festival","Reunification Day","International Labor Day","Independence Day Holiday","Independence Day")
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
_FEE_LIST_JSON_KEY = ("name", "value", "from", "to")
_DEFAUT_FEE_LIST = {
    "079": {
        "O_Basic":{
            "I_P4h":66500,
            "I_P3h":69800,
            "I_P2h":83800,
            "II_P4h":69800,
            "II_P3h":73200,
            "II_P2h":87100,
            "III_P4h":73200,
            "III_P3h":76500,
            "III_P2h":90400,
            "OOH": 0.16,
            "WKD":0.21,
            "HOL": 0.32,
            "LNY":2.0,
            "BLNY":1.0,
            "ALNY":1.0,
            "FavMaid":0,
            "OwnTools":30000
        },
        "S_Basic":{
            "I_P4h":66500,
            "I_P3h":69800,
            "I_P2h":83800,
            "II_P4h":69800,
            "II_P3h":73200,
            "II_P2h":87100,
            "III_P4h":73200,
            "III_P3h":76500,
            "III_P2h":90400,
            "OOH": 0.16,
            "WKD":0.21,
            "HOL": 0.32,
            "LNY":2.0,
            "BLNY":1.0,
            "ALNY":1.0,
            "FavMaid":0,
            "OwnTools":30000
        },
        "O_DeepHome":{
            "I_P4h":66500,
            "I_P3h":69800,
            "I_P2h":83800,
            "II_P4h":69800,
            "II_P3h":73200,
            "II_P2h":87100,
            "III_P4h":73200,
            "III_P3h":76500,
            "III_P2h":90400,
            "OOH": 0.16,
            "WKD":0.21,
            "HOL": 0.32,
            "LNY":2.0,
            "BLNY":1.0,
            "ALNY":1.0,
            "FavMaid":0,
            "OwnTools":30000
        },
        "O_Sofa":{
            "I_P4h":66500,
            "I_P3h":69800,
            "I_P2h":83800,
            "II_P4h":69800,
            "II_P3h":73200,
            "II_P2h":87100,
            "III_P4h":73200,
            "III_P3h":76500,
            "III_P2h":90400,
            "OOH": 0.16,
            "WKD":0.21,
            "HOL": 0.32,
            "LNY":2.0,
            "BLNY":1.0,
            "ALNY":1.0,
            "FavMaid":0,
            "OwnTools":30000
        }
    }
}
_FEE_LIST_AVAILABLE = ("O_Basic_079","S_Basic_079","O_DeepHome_079","O_Sofa_079")
_DEFAUT_SERVICE_FEE_DETAILS = {"is_OutOfficeHours":False, "is_Weekend":False, "is_Holiday":False, "is_NewYear":False, "is_BeforeNewYear":False, "is_AfterNewYear":False, "is_OwnTools":False}

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

    return {"base_rate": base_rate,"fee_detail": fee_detail}


def is_weekend(bookdate):
	days = str(bookdate).split('-')
	d = date(int(days[0]), int(days[1]), int(days[2]))

	return d.weekday() > 4


def is_OutOfWorkingHour(starttime):
	timelist = str(starttime).split(":")
	time_formated = time(int(timelist[0]),int(timelist[1]),int(timelist[2]))
	return time_formated < time(8,0,0) or time_formated >= time(17,0,0)


def check_valid_input(city,area,servicename,duration,propertydetails):
    error_messagge = ""
    if city not in _CITY_LIST:
        error_messagge  = error_messagge + "INVALID city code; "
    if area not in _AREA_LIST:
        error_messagge  = error_messagge + "INVALID area code; "
    fee_available = servicename + "_" + city
    if fee_available not in _FEE_LIST_AVAILABLE:
        error_messagge  = error_messagge + "INVALID service code or Fee List for " + fee_available + " NOT yet availabble"
    if duration == 0:
        if json.dumps(propertydetails) == "{}":
            error_messagge  = error_messagge + "Both duration = 0 and propertydetails is empty; " + json.dumps(propertydetails)
        else:
            if servicename.find("Basic") != -1 or servicename.find("DeepHome") != -1:
                if propertydetails["housetype"] == None:
                    housetype = "None"
                else:
                    housetype = propertydetails["housetype"]
                if propertydetails["totalarea"] == None:
                    totalarea = "None"
                else:
                    totalarea = propertydetails["totalarea"]
                if housetype not in _HOUSE_TYPE_LIST:
                    error_messagge  = error_messagge + "INVALID house type in propertydetails; "
                if totalarea not in _TOTAL_AREA_LIST:
                    error_messagge  = error_messagge + "INVALID total area in propertydetails; "
            elif servicename.find("Sofa") != -1:
                if propertydetails.get("withpets") == None:
                    withpets = False
                else:
                    withpets = propertydetails.get("withpets")
                if propertydetails.get("curtainswaterwashing") == None:
                    if propertydetails.get("cottonsofacleaning") == None:
                        if propertydetails.get("leathersofacleaning") == None:
                            if propertydetails.get("mattresscleaning") == None:
                                if propertydetails.get("carpetcleaning") == None:
                                    if propertydetails.get("curtainsdrycleaning") == None:
                                        error_messagge  = error_messagge + "Details for ServideCode " + servicename + " is empty in propertydetails; "
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

    return error_messagge


def get_estimated_duration(ironingclothes, propertydetails):
    estimatedduration = 0.0;

    if propertydetails.get("housetype") != None:
        """Estimation for Cleaning Service"""
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

    if propertydetails.get("cottonsofacleaning") != None:
        cottonsofacleaning = propertydetails.get("cottonsofacleaning")
        if cottonsofacleaning.get("1-seatsofa") == None:
            one_seatsofa = 0
        else:
            one_seatsofa = cottonsofacleaning.get("1-seatsofa")
        if cottonsofacleaning.get("2-seatsofa") == None:
            two_seatsofa = 0
        else:
            two_seatsofa = cottonsofacleaning.get("2-seatsofa")
        if cottonsofacleaning.get("3-seatsofa") == None:
            three_seatsofa = 0
        else:
            three_seatsofa = cottonsofacleaning.get("3-seatsofa")
        estimatedduration = estimatedduration + one_seatsofa / 3.0
        estimatedduration = estimatedduration + two_seatsofa * 0.5
        estimatedduration = estimatedduration + 2.0 * three_seatsofa / 3

    if propertydetails.get("leathersofacleaning") != None:
        leathersofacleaning = propertydetails.get("leathersofacleaning")
        if leathersofacleaning.get("1-seatsofa") == None:
            one_seatsofa = 0
        else:
            one_seatsofa = leathersofacleaning.get("1-seatsofa")
        if leathersofacleaning.get("2-seatsofa") == None:
            two_seatsofa = 0
        else:
            two_seatsofa = leathersofacleaning.get("2-seatsofa")
        if leathersofacleaning.get("3-seatsofa") == None:
            three_seatsofa = 0
        else:
            three_seatsofa = leathersofacleaning.get("3-seatsofa")
        estimatedduration = estimatedduration + one_seatsofa * 0.5
        estimatedduration = estimatedduration + 2.0 * two_seatsofa / 3
        estimatedduration = estimatedduration + 5.0 * three_seatsofa / 6

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
        estimatedduration = estimatedduration + less_than_onefive * 0.5
        estimatedduration = estimatedduration + 2.0 * onefive_to_oneeight / 3
        estimatedduration = estimatedduration + 5.0 * more_than_oneeight / 6

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
        estimatedduration = estimatedduration + less_than_onefive * 0.5
        estimatedduration = estimatedduration + 2.0 * onefive_to_oneeight / 3

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
        estimatedduration = estimatedduration + numberoffbedroom * 0.5
        estimatedduration = estimatedduration + numberofflivingroom * 0.5

    if propertydetails.get("curtainswaterwashing") != None:
        curtainswaterwashing = propertydetails.get("curtainswaterwashing")
        if curtainswaterwashing == "< 10kg":
            estimate = 2
        elif curtainswaterwashing == "10kg – 15kg":
            estimate = 3
        else:
            num = int(curtainswaterwashing.strip("kg"))
            estimate = 4 + (num - 15)/5
        estimatedduration = estimatedduration + estimate

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


def extra_fee_special_day(bookdate, starttime, feelist):
	"""Calculates additional fee based on date & time of booking"""
	fee_detail = {}
	extra_fee = 0.0
	if bookdate in _LUNAR_NEW_YEAR_DAYS_2022:
		fee_detail["is_NewYear"] = True
		extra_fee += feelist["LNY"]
	elif bookdate in _BEFORE_LUNAR_NEW_YEAR_DAYS_2022:
		fee_detail["is_BeforeNewYear"] = True
		extra_fee += feelist["BLNY"]
	elif bookdate in _AFTER_LUNAR_NEW_YEAR_DAYS_2022:
		fee_detail["is_AfterNewYear"] = True
		extra_fee += feelist["ALNY"]
	elif bookdate in _OTHER_NATIONAL_HOLIDAY_DAYS_2022:
		fee_detail["is_Holiday"] = True
		extra_fee += feelist["HOL"]
	elif is_weekend(bookdate):
		fee_detail["is_Weekend"] = True
		extra_fee += feelist["WKD"]
	elif is_OutOfWorkingHour(starttime):
		fee_detail["is_OutOfficeHours"] = True
		extra_fee += feelist["OOH"]

	return {"extra_fee_percent": extra_fee,"extra_service_fee_details":fee_detail}
