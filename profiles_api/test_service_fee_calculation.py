import json
import jsonfield
import datetime
from datetime import date, timedelta
from datetime import time, datetime
import pytz
import jsonschema
from jsonschema import validate

from profiles_api import calculate_location_area as cla

import math

_SPECIAL_DAYS = {
    "2022":{
        "LNY":["2022-01-31","2022-02-01","2022-02-02","2022-02-03","2022-02-04","2022-02-05"],
        "BLNY":["2022-01-30","2022-01-29","2022-01-28"],
        "ALNY":["2022-02-06","2022-02-07","2022-02-08"],
        "HOL":["2022-01-01","2022-01-02","2022-01-03","2022-04-10","2022-04-11","2022-04-30","2022-05-01","2022-05-02","2022-05-03","2022-09-01","2022-09-02","2022-12-31"]
    },
    "2023":{
        "LNY":["2023-01-20","2023-01-21","2023-01-22","2023-01-23","2023-01-24"],
        "BLNY04":["2023-01-16","2023-01-17","2023-01-18","2023-01-19"],
        "BLNY07":["2023-01-13","2023-01-14","2023-01-15"],
        "BLNY10":["2023-01-10","2023-01-11","2023-01-12"],
        "ALNY04":["2023-01-25","2023-01-26","2023-01-27","2023-01-28"],
        "ALNY07":["2023-01-29","2023-01-30","2023-01-31"],
        "HOL":["2023-01-01","2023-01-02","2023-04-29","2023-04-30","2023-05-01","2023-05-02","2023-05-03","2023-09-02","2023-09-03","2023-09-04","2023-12-31"]
    },
    "2024":{
        "LNY":["2024-02-08","2024-02-09","2024-02-10","2024-02-11","2024-02-12"],
        "BLNY04":["2024-02-04","2024-02-05","2024-02-06","2024-02-07"],
        "BLNY07":["2024-02-01","2024-02-02","2024-02-03"],
        "BLNY10":["2024-01-29","2024-01-30","2024-01-31"],
        "ALNY04":["2024-02-13","2024-02-14","2024-02-15","2024-02-16"],
        "ALNY07":["2024-02-17","2024-02-18","2024-02-19"],
        "HOL":["2024-01-01","2024-04-18","2024-04-30","2024-05-01","2024-09-02"]
    },
    "2025":{
        "LNY":["2025-01-27","2025-01-28","2025-01-29","2025-01-30","2025-01-31"],
        "BLNY04":["2025-01-23","2025-01-24","2025-01-25","2025-01-26"],
        "BLNY07":["2025-01-20","2025-01-21","2025-01-22"],
        "BLNY10":["2025-01-17","2025-01-18","2025-01-19"],
        "ALNY04":["2025-02-01","2025-02-02","2025-02-03","2025-02-04"],
        "ALNY07":["2025-02-05","2025-02-06","2025-02-07"],
        "HOL":["2025-01-01","2025-04-07","2025-04-30","2025-05-01","2025-09-02"]
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
_DEFAUT_SERVICE_CODE_LIST = {
    "079":{
        "Basic":["I_P4h","I_P3h","I_P2h","II_P4h","II_P3h","II_P2h","III_P4h","III_P3h","III_P2h","OOH","WKD","HOL","LNY","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","OwnTools","Urgent","Premium","ForeignLang"],
        "DeepHome":["I_P4h","II_P4h","III_P4h","OOH","WKD","HOL","LNY","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","Urgent","ForeignLang"],
        "Sofa":["Cotton1-Seat","Cotton2-Seat","Cotton3-Seat","CottonStool","Leather1-Seat","Leather2-Seat","Leather3-Seat","LeatherRecliner","LeatherStool","OOH","WKD","HOL","LNY","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","Urgent","Premium","ForeignLang"],
    },
    "others":{
        "Basic":["I_P4h","I_P3h","I_P2h","OOH","WKD","HOL","LNY","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","OwnTools","Urgent","Premium","ForeignLang"],
        "DeepHome":["I_P4h","OOH","WKD","HOL","LNY","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","Urgent","ForeignLang"],
        "Sofa":["Cotton1-Seat","Cotton2-Seat","Cotton3-Seat","CottonStool","Leather1-Seat","Leather2-Seat","Leather3-Seat","LeatherRecliner","LeatherStool","OOH","WKD","HOL","LNY","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","BLNY04","BLNY07","BLNY10","ALNY04","ALNY07","Urgent","Premium","ForeignLang"],
    }
}
_HOUSE_TYPE_LIST = ("apartment/single-story house","building/multi-storey house","villa","office","None")
_TOTAL_AREA_LIST = ("< 50m2", "50m2 - 90m2", "90m2 - 140m2", "140m2 - 255m2", "255m2 - 500m2", "500m2 - 1000m2")
_PROPERTY_DETAIL_PRESET = {
    "None":{
        "< 50m2":{
            "estimated duration":{"min":2,"max":16},
            "recommended duration":2,
            "recommended number of workers": 1},
        "50m2 - 90m2":{
            "estimated duration":{"min":2,"max":16},
            "recommended duration":3,
            "recommended number of workers": 1},
        "90m2 - 140m2":{
            "estimated duration":{"min":2,"max":16},
            "recommended duration":4,
            "recommended number of workers": 1},
        "140m2 - 190m2":{
            "estimated duration":{"min":2,"max":16},
            "recommended duration":6,
            "recommended number of workers": 1},
        "190m2 - 255m2":{
            "estimated duration":{"min":2,"max":16},
            "recommended duration":8,
            "recommended number of workers": 2}
    },
    "apartment/single-story house":{
        "140m2 - 200m2":{
            "bedroom":{"min":2,"max":5},
            "bathroom":{"min":1,"max":5},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":5},

        "< 50m2":{
            "bedroom":{"min":0,"max":0},
            "bathroom":{"min":0,"max":0},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":2},
        "50m2 - 90m2":{
            "bedroom":{"min":1,"max":3},
            "bathroom":{"min":1,"max":2},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":3},
        "90m2 - 140m2":{
            "bedroom":{"min":1,"max":4},
            "bathroom":{"min":1,"max":3},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":4},
        "140m2 - 255m2":{
            "bedroom":{"min":2,"max":5},
            "bathroom":{"min":1,"max":5},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":5},
        "> 255m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":6}
    },
    "villa":{
        "255m2 - 500m2":{
            "bedroom":{"min":3,"max":6},
            "bathroom":{"min":3,"max":8},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":8},
        "> 500m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":8},

        "< 140m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":4},
        "140m2 - 255m2":{
            "bedroom":{"min":2,"max":4},
            "bathroom":{"min":1,"max":4},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":5},
        "> 255m2":{
            "bedroom":{"min":3,"max":6},
            "bathroom":{"min":3,"max":8},
            "estimated duration":{"min":2,"max":8},
            "recommended duration":8}
    },
    "office":{
        "255m2 - 500m2":{
            "estimated duration":{"min":5,"max":8},
            "recommended duration":7},
        "> 500m2":{
            "estimated duration":{"min":7,"max":8},
            "recommended duration":8},

        "< 50m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":2},
        "50m2 - 90m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":2},
        "90m2 - 140m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":3},
        "140m2 - 255m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":4},
        "> 255m2":{
            "estimated duration":{"min":2,"max":8},
            "recommended duration":6}
    },
    "building/multi-storey house":{
        "0-Storey":{
            "< 90m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":3},
            "90m2 - 140m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":4},
            "140m2 - 255m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":6},
            "> 255m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8}
        },
        "1-Storey":{
            "< 90m2":{
                "estimated duration":{"min":2,"max":4},
                "recommended duration":3},
            "90m2 - 140m2":{
                "estimated duration":{"min":2,"max":5},
                "recommended duration":4},
            "140m2 - 200m2":{
                "estimated duration":{"min":2,"max":6},
                "recommended duration":5},
            "> 200m2":{
                "estimated duration":{"min":2,"max":7},
                "recommended duration":6}
        },
        "2-Storey":{
            "< 140m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":5},
            "140m2 - 200m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":6},
            "200m2 - 260m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":7},
            "> 260m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8}
        },
        "3-Storey":{
            "< 200m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":6},
            "200m2 - 260m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":7},
            "260m2 - 320m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "> 320m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8}
        },
        "4-Storey":{
            "< 320m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "320m2 - 380m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "380m2 - 440m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "> 440m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8}
        },
        "5-Storey":{
            "< 380m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "380m2 - 440m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "440m2 - 500m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "> 500m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8}
        },
        "6-Storey":{
            "< 440m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "440m2 - 500m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8},
            "> 500m2":{
                "estimated duration":{"min":2,"max":8},
                "recommended duration":8}
        },
    },
}
_PROPERTY_DEEPHOME_PRESET = {
    "None":{
        "< 50m2":{
            "estimated duration":{"min":6,"max":32},
            "recommended duration":6,
            "recommended number of workers": 1},
        "50m2 - 90m2":{
            "estimated duration":{"min":6,"max":32},
            "recommended duration":8,
            "recommended number of workers": 2},
        "90m2 - 140m2":{
            "estimated duration":{"min":6,"max":32},
            "recommended duration":12,
            "recommended number of workers": 3},
        "140m2 - 190m2":{
            "estimated duration":{"min":6,"max":32},
            "recommended duration":16,
            "recommended number of workers": 4},
        "190m2 - 255m2":{
            "estimated duration":{"min":6,"max":32},
            "recommended duration":20,
            "recommended number of workers": 5}
    },
    "apartment/single-story house":{
        "140m2 - 200m2":{
            "bedroom":{"min":2,"max":5},
            "bathroom":{"min":1,"max":5},
            "livingroom":{"min":1,"max":2},
            "kitchen":{"min":1,"max":3},
            "estimated duration":{"min":6,"max":36},
            "recommended duration":16},

        "< 50m2":{
            "bedroom":{"min":0,"max":0},
            "bathroom":{"min":0,"max":0},
            "livingroom":{"min":0,"max":0},
            "kitchen":{"min":0,"max":0},
            "estimated duration":{"min":6,"max":36},
            "recommended duration":6},
        "50m2 - 90m2":{
            "bedroom":{"min":1,"max":3},
            "bathroom":{"min":1,"max":2},
            "livingroom":{"min":1,"max":1},
            "kitchen":{"min":1,"max":1},
            "estimated duration":{"min":6,"max":36},
            "recommended duration":8},
        "90m2 - 140m2":{
            "bedroom":{"min":1,"max":4},
            "bathroom":{"min":1,"max":3},
            "livingroom":{"min":1,"max":1},
            "kitchen":{"min":1,"max":2},
            "estimated duration":{"min":6,"max":36},
            "recommended duration":12},
        "140m2 - 255m2":{
            "bedroom":{"min":2,"max":5},
            "bathroom":{"min":1,"max":5},
            "livingroom":{"min":1,"max":2},
            "kitchen":{"min":1,"max":3},
            "estimated duration":{"min":6,"max":36},
            "recommended duration":16},
        "> 255m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":24},
    },
    "villa":{
        "255m2 - 500m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":32},
        "> 500m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":36},

        "< 140m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":12},
        "140m2 - 255m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":16},
        "> 255m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":24}
    },
    "office":{
        "255m2 - 500m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":28},
        "> 500m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":32},

        "< 50m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":6},
        "50m2 - 90m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":8},
        "90m2 - 140m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":12},
        "140m2 - 255m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":16},
        "> 255m2":{
            "estimated duration":{"min":6,"max":36},
            "recommended duration":24}
    },
    "building/multi-storey house":{
        "0-Storey":{
            "< 90m2":{
                "estimated duration":{"min":6,"max":36},
                "recommended duration":8},
            "90m2 - 140m2":{
                "estimated duration":{"min":6,"max":36},
                "recommended duration":12},
            "140m2 - 255m2":{
                "estimated duration":{"min":6,"max":36},
                "recommended duration":18},
            "> 255m2":{
                "estimated duration":{"min":6,"max":36},
                "recommended duration":18},
        },
        "1-Storey":{
            "< 90m2":{
                "estimated duration":{"min":8,"max":10},
                "recommended duration":8},
            "90m2 - 140m2":{
                "estimated duration":{"min":10,"max":14},
                "recommended duration":12},
            "140m2 - 200m2":{
                "estimated duration":{"min":14,"max":18},
                "recommended duration":16},
            "> 200m2":{
                "estimated duration":{"min":18,"max":22},
                "recommended duration":20}
        },
        "2-Storey":{
            "< 140m2":{
                "estimated duration":{"min":10,"max":14},
                "recommended duration":12},
            "140m2 - 200m2":{
                "estimated duration":{"min":14,"max":18},
                "recommended duration":16},
            "200m2 - 260m2":{
                "estimated duration":{"min":18,"max":22},
                "recommended duration":20},
            "> 260m2":{
                "estimated duration":{"min":22,"max":26},
                "recommended duration":24}
        },
        "3-Storey":{
            "< 200m2":{
                "estimated duration":{"min":14,"max":18},
                "recommended duration":16},
            "200m2 - 260m2":{
                "estimated duration":{"min":18,"max":22},
                "recommended duration":20},
            "260m2 - 320m2":{
                "estimated duration":{"min":22,"max":26},
                "recommended duration":24},
            "> 320m2":{
                "estimated duration":{"min":26,"max":30},
                "recommended duration":28}
        },
        "4-Storey":{
            "< 320m2":{
                "estimated duration":{"min":22,"max":26},
                "recommended duration":24},
            "320m2 - 380m2":{
                "estimated duration":{"min":26,"max":30},
                "recommended duration":28},
            "380m2 - 440m2":{
                "estimated duration":{"min":30,"max":34},
                "recommended duration":32},
            "> 440m2":{
                "estimated duration":{"min":34,"max":38},
                "recommended duration":36}
        },
        "5-Storey":{
            "< 380m2":{
                "estimated duration":{"min":26,"max":30},
                "recommended duration":28},
            "380m2 - 440m2":{
                "estimated duration":{"min":30,"max":34},
                "recommended duration":32},
            "440m2 - 500m2":{
                "estimated duration":{"min":34,"max":38},
                "recommended duration":36},
            "> 500m2":{
                "estimated duration":{"min":36,"max":44},
                "recommended duration":40}
        },
        "6-Storey":{
            "< 440m2":{
                "estimated duration":{"min":30,"max":34},
                "recommended duration":32},
            "440m2 - 500m2":{
                "estimated duration":{"min":34,"max":38},
                "recommended duration":36},
            "> 500m2":{
                "estimated duration":{"min":36,"max":44},
                "recommended duration":40}
        },
    },
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
DUR_FOR_NORMAL_ROOM = 0.5
DUR_FOR_BIG_ROOM = 0.8
DUR_FOR_NORMAL_BATHROOM = 0.3
DUR_FOR_BIG_BATHROOM = 0.4
DUR_FOR_IRONINGCLOTHES = 0.5
DUR_FOR_HANDWASHCLOTHES = 0.5
DUR_FOR_WITHPETS = 0.5
_SERVICE_TYPE_FACTORS = {
    "O_Basic": 1,
    "S_Basic": 1,
    "O_DeepHome": 3
}

_FEE_LIST_AVAILABLE = ("O_Basic_079","S_Basic_079","O_DeepHome_079","O_Sofa_079","O_Basic_048","S_Basic_048","O_DeepHome_048","O_Sofa_048")
#_DEFAUT_SERVICE_FEE_DETAILS = {"is_OutOfficeHours":False, "is_Weekend":False, "is_Holiday":False, "is_NewYear":False, "is_BeforeNewYear":False, "is_AfterNewYear":False, "is_OwnTools":False}
_WORK_DAY_LIST = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
_SPECIAL_FEE_NAMES = ["Normal Fee","Lunar New Year Fee","1-4 Days Before Lunar New Year Fee",
    "5-7 Days Before Lunar New Year Fee","8-10 Days Before Lunar New Year Fee",
    "1-4 Days After Lunar New Year Fee","5-7 Days After Lunar New Year Fee",
    "Nation Holidays Fee","Weekend Fee","Out Of Office Hour Fee"]

def get_servicecode_details(servicecode,locationdetails):
    district_found = "unknown"
    area = "unknown"
    city = "unknown"
    servicecodelist = servicecode.split("_")
    servicename = servicecodelist[0] + "_" + servicecodelist[1]
    if len(servicecodelist) > 2:
        city = servicecodelist[2]
    if len(servicecodelist) > 3:
        area = servicecodelist[3]
    if locationdetails != None:
        if locationdetails.get("citycode") != None:
            city = locationdetails.get("citycode")
        if locationdetails.get("district") != None:
            district_found = locationdetails.get("district").strip()
            district_found = ' '.join(district_found.split())
        elif locationdetails.get("formatted_address") != None:
            district_found = cla.get_district_from_address(locationdetails.get("formatted_address"))

        if city == "079":
            area, district_found = cla.get_area_from_district(district_found,locationdetails.get("formatted_address"))
        else:
            area = "I"

    return servicename, city, area, district_found


# Service Fee calculation
def get_base_rate(area, duration, feelist):
    fee_detail = {}
    base_rate = 0
    basename = ""
    if duration == 2:
        basename = area + "_" + "P2h"
        fee_detail["is_P2h"] = True
    elif duration == 3:
        basename = area + "_" + "P3h"
        fee_detail["is_P3h"] = True
    elif duration >= 4:
        basename = area + "_" + "P4h"
    else:
        return 0,fee_detail,basename
    base_rate = feelist[basename]

    #return {"base_rate": base_rate,"fee_detail": fee_detail}
    return base_rate, fee_detail, basename


def is_weekend(bookdate):
	days = str(bookdate).split('-')
	d = date(int(days[0]), int(days[1]), int(days[2]))

	return d.weekday() > 4


def is_OutOfWorkingHour(starttime, duration):
    is_OOH = False
    percent_OOH = 1.0
    hour_outOfWorkingHour = 0
    timelist = str(starttime).split(":")
    if duration > 0:
        for i in range(duration):
            time_formated = time((int(timelist[0])+i)%24,int(timelist[1]),int(timelist[2]))
            if time_formated < time(8,0,0) or time_formated >= time(18,0,0):
                hour_outOfWorkingHour = hour_outOfWorkingHour + 1
        if hour_outOfWorkingHour > 0:
            is_OOH = True
            percent_OOH = hour_outOfWorkingHour / duration
    else:
        time_formated = time(int(timelist[0]),int(timelist[1]),int(timelist[2]))
        is_OOH = time_formated < time(8,0,0) or time_formated >= time(18,0,0)

    return is_OOH, percent_OOH, hour_outOfWorkingHour


def is_UrgentBooking(bookdate, starttime):
    days = str(bookdate).split('-')
    timelist = str(starttime).split(":")
    BDateTime = datetime(int(days[0]), int(days[1]), int(days[2]),int(timelist[0]),int(timelist[1]),int(timelist[2]))

    localisedDatetime = datetime.now(pytz.timezone('Asia/Saigon'))
    now_now = datetime(localisedDatetime.year,localisedDatetime.month,localisedDatetime.day,localisedDatetime.hour,localisedDatetime.minute,localisedDatetime.second)
    if localisedDatetime.hour < 22:
        now_plus2h = datetime(localisedDatetime.year,localisedDatetime.month,localisedDatetime.day,localisedDatetime.hour+2,localisedDatetime.minute,localisedDatetime.second)
    else:
        now_plus2h = datetime(localisedDatetime.year,localisedDatetime.month,localisedDatetime.day+1,localisedDatetime.hour-22,localisedDatetime.minute,localisedDatetime.second)

    return (now_now <= BDateTime and BDateTime < now_plus2h)


def check_validBookingTime(bookdate, starttime):
    error_messagge = ""
    days = str(bookdate).split('-')
    timelist = str(starttime).split(":")
    BDateTime = datetime(int(days[0]), int(days[1]), int(days[2]),int(timelist[0]),int(timelist[1]),int(timelist[2]))

    localisedDatetime = datetime.now(pytz.timezone('Asia/Saigon'))
    now = datetime(localisedDatetime.year,localisedDatetime.month,localisedDatetime.day,localisedDatetime.hour,localisedDatetime.minute,localisedDatetime.second)

    if BDateTime <= now:
        error_messagge = "INVALID input: booking time must be later than current time! "

    return error_messagge


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
            if propertydetails.get("housetype") == None:
                housetype = "None"
            else:
                housetype = propertydetails.get("housetype")
            if propertydetails.get("totalarea") == None:
                totalarea = "None"
            else:
                totalarea = propertydetails.get("totalarea")
            if housetype not in _HOUSE_TYPE_LIST:
                error_propertydetails = True
                error_messagge_propertydetails  = "INVALID house type in propertydetails; "

            # Check corect totalarea for new fee Estimation (min, recommendation, max)
            if duration == -1 :
                totalarea_key_found = False
                if servicename == "O_DeepHome":
                    property_details_preset = _PROPERTY_DEEPHOME_PRESET.get(housetype)
                else:
                    property_details_preset = _PROPERTY_DETAIL_PRESET.get(housetype)

                if housetype == "building/multi-storey house":
                    if propertydetails.get("numberoffloors") == None:
                        numberoffloors = 0
                    else:
                        numberoffloors = propertydetails.get("numberoffloors")
                    if numberoffloors > 6:
                        error_propertydetails = True
                        error_messagge_propertydetails  = error_messagge_propertydetails  + "INVALID number of floors: " + str(numberoffloors) + " of building/multi-storey house in propertydetails; "

                    floor_key = str(numberoffloors) + "-Storey"
                    property_details_preset = property_details_preset.get(floor_key)

                if error_propertydetails == False:
                    for totalarea_key in property_details_preset.keys():
                        if totalarea == totalarea_key:
                            totalarea_key_found = True
                            break
                    if totalarea_key_found == False:
                        error_propertydetails = True
                        if housetype == "None" and totalarea  == "> 255m2":
                            error_messagge_propertydetails  = error_messagge_propertydetails  + "For > 255m2 total area, CS will contact customer for more detailed pricing!; "
                        else:
                            error_messagge_propertydetails  = error_messagge_propertydetails  + "INVALID total area " + totalarea + " (DURATION -1) in propertydetails + housetype " + housetype + str(property_details_preset)+ " ; "
            else :
                if totalarea not in _TOTAL_AREA_LIST:
                    error_propertydetails = True
                    error_messagge_propertydetails  = error_messagge_propertydetails  + "INVALID total area in propertydetails; "

    if servicename == "O_Basic" or servicename == "O_DeepHome":
        if duration == 0:
            if error_propertydetails == True:
                error_messagge  = error_messagge + "Duration = 0 and " + error_messagge_propertydetails
        elif duration == -1:
            if error_propertydetails == True:
                error_messagge  = error_messagge + error_messagge_propertydetails
        elif duration < 6 and servicename == "O_DeepHome":
            error_messagge  = error_messagge + "Minimun duration for DeepHome Service is 6 hours; "
        elif duration < 2 and servicename == "O_Basic":
            error_messagge  = error_messagge + "Minimun duration for Basic Service is 2 hours; "

    elif servicename == "S_Basic":
        if duration == -1:
            if error_propertydetails == True:
                error_messagge  = error_messagge + error_messagge_propertydetails
        if subscription_schedule_details == None or json.dumps(subscription_schedule_details) == "{}":
            error_messagge  = error_messagge + "Subscription Service requires subscription_schedule_details. It's " + json.dumps(subscription_schedule_details)  + "; "
        else:
            if subscription_schedule_details.get("workingdays") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: working_ays empty;  "
            if subscription_schedule_details.get("workingtime") == None:
                error_messagge  = error_messagge + "subscription_schedule_details: workingtime empty;  "
            if subscription_schedule_details.get("workingduration") == None:
                if error_propertydetails == True:
                    error_messagge  = error_messagge + "subscription_schedule_details: workingduration is required when propertydetails empty or error;  "
            else:
                workingduration = subscription_schedule_details.get("workingduration")
                if workingduration == 0  or workingduration == -1:
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


def get_estimated_duration_for_cleaning(extra_services, propertydetails):
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

    # EXTRA services
    ironingclothes = extra_services.get("ironingclothes")
    handwashclothes = extra_services.get("handwashclothes")
    if ironingclothes:
        estimatedduration = estimatedduration + DUR_FOR_IRONINGCLOTHES
    if handwashclothes:
        estimatedduration = estimatedduration + DUR_FOR_HANDWASHCLOTHES

    # Minimum serbvice is 2 hours
    if estimatedduration < 2.0:
        estimatedduration = 2.0

    return math.ceil(estimatedduration)

def get_estimated_duration_for_DeepHome(extra_services, propertydetails):
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

    # EXTRA services
    ironingclothes = extra_services.get("ironingclothes")
    handwashclothes = extra_services.get("handwashclothes")
    if ironingclothes:
        estimatedduration = estimatedduration + DUR_FOR_IRONINGCLOTHES
    if handwashclothes:
        estimatedduration = estimatedduration + DUR_FOR_HANDWASHCLOTHES

    # Minimum serbvice is 6 hours
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

    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,feelist,0)
    adjust_rate = 1 + extra_fee_percent

    if urgentbooking == None:
        urgentbooking = is_UrgentBooking(bookdate,starttime)
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

    # Minimum serbvice is 500000 vnd and 0.5 hours
    if estimatedfee < 500000:
        estimatedfee = 500000
        minimum_response = {"Minimum Fee Applied": True}
        fee_details_response.update(minimum_response)

    if estimatedduration < 0.5:
        estimatedduration = 0.5

    total_fee_response = {"Total Fee": int(estimatedfee), "Estimated Duration": round(estimatedduration,1)}
    fee_details_response.update(total_fee_response)

    if extra_fee_percent > 0.0:
        extra_service_fee_response = {"Extra Service Fee Details": extra_service_fee_details}
        fee_details_response.update(extra_service_fee_response)

    return fee_details_response


def get_estimated_duration(extra_services, propertydetails,subscription_schedule_details, servicename):
    estimatedduration = 0.0

    if servicename == "O_Basic":
        estimatedduration  = get_estimated_duration_for_cleaning(extra_services, propertydetails)
    elif servicename == "S_Basic":
        if propertydetails != None and json.dumps(propertydetails) != "{}":
            estimatedduration  = get_estimated_duration_for_cleaning(extra_services, propertydetails)
        elif subscription_schedule_details != None:
            estimatedduration = subscription_schedule_details.get("workingduration")
        else:
            estimatedduration = 0.0
    elif servicename == "O_DeepHome":
        estimatedduration = get_estimated_duration_for_DeepHome(extra_services, propertydetails)

    return math.ceil(estimatedduration)


def get_year(date):
    date_list = str(date).split('-')
    return str(date_list[0])

def extra_fee_special_day_new(bookdate, starttime, feelist, duration):
    """Calculates additional fee based on date & time of booking"""

    fee_detail = {}
    extra_fee = 0.0
    bookdate = str(bookdate)
    year = get_year(bookdate)
    special_day_of_year = _SPECIAL_DAYS.get(year)
    LNY  = special_day_of_year.get("LNY")
    BLNY04  = special_day_of_year.get("BLNY04")
    BLNY07  = special_day_of_year.get("BLNY07")
    BLNY10  = special_day_of_year.get("BLNY10")
    ALNY04  = special_day_of_year.get("ALNY04")
    ALNY07  = special_day_of_year.get("ALNY07")
    HOL  = special_day_of_year.get("HOL")
    if bookdate in LNY:
        fee_detail["is_NewYear"] = True
        extra_fee += feelist["LNY"]
        index = 1
    elif bookdate in BLNY04:
        fee_detail["is_BeforeNewYear04Days"] = True
        extra_fee += feelist["BLNY04"]
        index = 2
    elif bookdate in BLNY07:
        fee_detail["is_BeforeNewYear07Days"] = True
        extra_fee += feelist["BLNY07"]
        index = 3
    elif bookdate in BLNY10:
        fee_detail["is_BeforeNewYear10Days"] = True
        extra_fee += feelist["BLNY10"]
        index = 4
    elif bookdate in ALNY04:
        fee_detail["is_AfterNewYear04Days"] = True
        extra_fee += feelist["ALNY04"]
        index = 5
    elif bookdate in ALNY07:
        fee_detail["is_AfterNewYear07Days"] = True
        extra_fee += feelist["ALNY07"]
        index = 6
    elif bookdate in HOL:
        fee_detail["is_Holiday"] = True
        extra_fee += feelist["HOL"]
        index = 7
    elif is_weekend(bookdate):
        fee_detail["is_Weekend"] = True
        extra_fee += feelist["WKD"]
        index = 8
    else:
        is_OOH, percent_OOH, hour_outOfWorkingHour = is_OutOfWorkingHour(starttime, duration)
        if is_OOH:
            fee_detail["is_OutOfficeHours"] = True
            if hour_outOfWorkingHour > 0:
                fee_detail["OutOfficeHours"] = hour_outOfWorkingHour
            extra_fee += feelist["OOH"] * percent_OOH
            index = 9
        else:
            index = 0

    return extra_fee, fee_detail, index


def  get_Oneday_Basic_fee_details(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,fee_detail,numberofworkers):
    """Get fee of the service"""
    workingduration = int(usedduration/numberofworkers)
    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,service_fee_list,workingduration)
    final_rate = base_rate * (1 + extra_fee_percent)
    total_fee = final_rate * usedduration

    if owntool == True:
        total_fee += service_fee_list["OwnTools"]

    return int(total_fee), index, final_rate, extra_service_fee_details


def  get_O_Basic_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail,numberofworkers):
    """Get fee details of the service"""
    workingduration = int(usedduration/numberofworkers)
    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,service_fee_list,workingduration)
    final_rate = base_rate * (1 + extra_fee_percent)
    total_fee = final_rate * usedduration

    fee_details_response = {"Total Fee": int(total_fee)}
    if owntool == True:
        total_fee += service_fee_list["OwnTools"]
        extra_service_fee_details["is_OwnTools"] = True
        owntool_fee_response = {"Total Fee": int(total_fee),"OwnTools Fee":service_fee_list["OwnTools"]}
        fee_details_response.update(owntool_fee_response)

    if urgentbooking == None:
        urgentbooking = is_UrgentBooking(bookdate,starttime)
    if urgentbooking:
        urgentbooking_fee = service_fee_list["Urgent"]
        total_fee += urgentbooking_fee
        urgentbooking_fee_response = {"Total Fee": int(total_fee),"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)


    # Extra Services
    ironingclothes = extra_services.get("ironingclothes")
    handwashclothes = extra_services.get("handwashclothes")
    if ironingclothes == True:
        ironingclothes_fee = final_rate * DUR_FOR_IRONINGCLOTHES
        ironingclothes_fee_response = {"Ironing Clothes Fee": int(ironingclothes_fee)}
        fee_details_response.update(ironingclothes_fee_response)
    if handwashclothes:
        handwashclothes_fee = final_rate * DUR_FOR_HANDWASHCLOTHES
        handwashclothes_fee_response = {"Hand-Washing Clothes Fee": int(handwashclothes_fee)}
        fee_details_response.update(handwashclothes_fee_response)

    extra_service_fee_details.update(fee_detail)
    extra_service_fee_response = {"Extra Service Fee Details": extra_service_fee_details}

    if duration == 0 or duration == -1:
        estimatedduration_response = {"Estimated Duration": estimatedduration,"Number of Workers":numberofworkers,"Number of hours per Shift":int(estimatedduration/numberofworkers)}
    else:
        estimatedduration_response = {"Duration": duration,"Number of Workers":numberofworkers,"Number of hours per Shift":int(duration/numberofworkers)}
    fee_details_response.update(estimatedduration_response)

    fee_details_response.update(extra_service_fee_response)

    return fee_details_response


def  get_O_DeepHome_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail,numberofworkers):
    """Get fee details of the DeepHome service"""
    workingduration = int(usedduration/numberofworkers)
    extra_fee_percent, extra_service_fee_details, index = extra_fee_special_day_new(bookdate,starttime,service_fee_list,workingduration)
    final_rate = base_rate * (1 + extra_fee_percent)
    total_fee = final_rate * usedduration

    fee_details_response = {"Total Fee": int(total_fee)}

    if urgentbooking == None:
        urgentbooking = is_UrgentBooking(bookdate,starttime)
    if urgentbooking:
        urgentbooking_fee = service_fee_list["Urgent"]
        total_fee += urgentbooking_fee
        urgentbooking_fee_response = {"Total Fee": int(total_fee),"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)

    # Extra Services
    ironingclothes = extra_services.get("ironingclothes")
    handwashclothes = extra_services.get("handwashclothes")
    if ironingclothes == True:
        ironingclothes_fee = final_rate * DUR_FOR_IRONINGCLOTHES
        ironingclothes_fee_response = {"Ironing Clothes Fee": int(ironingclothes_fee)}
        fee_details_response.update(ironingclothes_fee_response)
    if handwashclothes:
        handwashclothes_fee = final_rate * DUR_FOR_HANDWASHCLOTHES
        handwashclothes_fee_response = {"Hand-Washing Clothes Fee": int(handwashclothes_fee)}
        fee_details_response.update(handwashclothes_fee_response)

    extra_service_fee_details.update(fee_detail)
    extra_service_fee_response = {"Extra Service Fee Details": extra_service_fee_details}

    if duration == 0 or duration == -1:
        estimatedduration_response = {"Estimated Duration": estimatedduration,"Number of Workers":numberofworkers,"Number of hours per Shift":int(estimatedduration/numberofworkers)}
    else:
        estimatedduration_response = {"Duration": duration,"Number of Workers":numberofworkers,"Number of hours per Shift":int(duration/numberofworkers)}
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


def  get_S_Basic_fee_details_response(subscription_schedule_details,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail,numberofworkers):
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
    component_fee = [0,0,0,0,0,0,0,0,0,0]
    component_count = [0,0,0,0,0,0,0,0,0,0]

    ironingclothes = extra_services.get("ironingclothes")
    handwashclothes = extra_services.get("handwashclothes")
    Day_by_Day_Fee_Response = []
    while process_date <= enddate_formatted:
        oneday_fee, index, final_rate, extra_service_fee_details = get_Oneday_Basic_fee_details(process_date,workingtime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,fee_detail,numberofworkers)
        one_day_fee_response = {"Date":str(process_date),"Fee_Type":_SPECIAL_FEE_NAMES[index],"Session Fee":oneday_fee}
        if index == 9:
            one_day_fee_response.update({"OutOfficeHours":extra_service_fee_details.get("OutOfficeHours")})
        if owntool == True:
            one_day_fee_response.update({"OwnTools Fee":service_fee_list["OwnTools"]})
        if ironingclothes == True:
            ironingclothes_fee = final_rate * DUR_FOR_IRONINGCLOTHES
            one_day_fee_response.update({"Ironing Clothes Fee": int(ironingclothes_fee)})
        if handwashclothes == True:
            handwashclothes_fee = final_rate * DUR_FOR_HANDWASHCLOTHES
            one_day_fee_response.update({"Hand-Washing Clothes Fee": int(handwashclothes_fee)})
        Day_by_Day_Fee_Response.append(one_day_fee_response)
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
    if urgentbooking == None:
        urgentbooking = is_UrgentBooking(actual_start_date,workingtime)
    if urgentbooking:
        urgentbooking_fee = service_fee_list["Urgent"]
        total_fee += urgentbooking_fee
        urgentbooking_fee_response = {"Total Fee": int(total_fee),"Urgent Booking Fee": int(urgentbooking_fee)}
        fee_details_response.update(urgentbooking_fee_response)

    total_workdays_response = {"Total Number of Work Days": count}
    fee_details_response.update(total_workdays_response)
    if duration == 0 or duration == -1:
        estimatedduration_response = {"Duration per session": estimatedduration, "Number of Workers per session":numberofworkers,"Number of working hours per worker per session":int(estimatedduration/numberofworkers)}
        fee_details_response.update(estimatedduration_response)
    if owntool == True:
        total_owntool_fee = count * service_fee_list["OwnTools"]
        total_owntool_response = {"Total OwnTools Fee": total_owntool_fee}
        fee_details_response.update(total_owntool_response)

    # Extra Services
    if ironingclothes == True:
        ironingclothes_fee = count * final_rate * DUR_FOR_IRONINGCLOTHES
        ironingclothes_fee_response = {"Total Ironing Clothes Fee": int(ironingclothes_fee)}
        fee_details_response.update(ironingclothes_fee_response)
    if handwashclothes:
        handwashclothes_fee = count * final_rate * DUR_FOR_HANDWASHCLOTHES
        handwashclothes_fee_response = {"Total Hand-Washing Clothes Fee": int(handwashclothes_fee)}
        fee_details_response.update(handwashclothes_fee_response)

    if count > 0:
        details_fee_type = {}
        for i in range(10):
            if component_count[i] > 0:
                if i == 0:
                    normal_fee_response = {"Normal Fee":{"Total Days": component_count[0], "Sub Total Fee":component_fee[0]}}
                    details_fee_type.update(normal_fee_response)
                elif i == 1:
                    LNY_fee_response = {"Lunar New Year Fee":{"Total Days": component_count[1], "Sub Total Fee":component_fee[1]}}
                    details_fee_type.update(LNY_fee_response)
                elif i == 2:
                    BLNY04_fee_response = {"1-4 Days Before Lunar New Year Fee":{"Total Days": component_count[2], "Sub Total Fee":component_fee[2]}}
                    details_fee_type.update(BLNY04_fee_response)
                elif i == 3:
                    BLNY07_fee_response = {"5-7 Days Before Lunar New Year Fee":{"Total Days": component_count[3], "Sub Total Fee":component_fee[3]}}
                    details_fee_type.update(BLNY07_fee_response)
                elif i == 4:
                    BLNY10_fee_response = {"8-10 Days Before Lunar New Year Fee":{"Total Days": component_count[4], "Sub Total Fee":component_fee[4]}}
                    details_fee_type.update(BLNY10_fee_response)
                elif i == 5:
                    ALNY04_fee_response = {"1-4 Days After Lunar New Year Fee":{"Total Days": component_count[5], "Sub Total Fee":component_fee[5]}}
                    details_fee_type.update(ALNY04_fee_response)
                elif i == 6:
                    ALNY07_fee_response = {"5-7 Days After Lunar New Year Fee":{"Total Days": component_count[6], "Sub Total Fee":component_fee[6]}}
                    details_fee_type.update(ALNY07_fee_response)
                elif i == 7:
                    HOL_fee_response = {"Nation Holidays Fee":{"Total Days": component_count[7], "Sub Total Fee":component_fee[7]}}
                    details_fee_type.update(HOL_fee_response)
                elif i == 8:
                    WKD_fee_response = {"Weekend Fee":{"Total Days": component_count[8], "Sub Total Fee":component_fee[8]}}
                    details_fee_type.update(WKD_fee_response)
                elif i == 9:
                    OOH_fee_response = {"Out Of Office Hour Fee":{"Total Days": component_count[9], "Sub Total Fee":component_fee[9]}}
                    details_fee_type.update(OOH_fee_response)
        details_fee_type_response = {"Detailed Fees":details_fee_type}
        fee_details_response.update(details_fee_type_response)
        Day_by_Day_Fee =  {"Day_by_Day_Fee":Day_by_Day_Fee_Response}
        fee_details_response.update(Day_by_Day_Fee)
        #component_fee_detail = {"component_fee_detail":str(component_fee),"component_count_detail":str(component_count)}
        #fee_details_response.update(component_fee_detail)

    return fee_details_response


def get_estimated_duration_for_cleaning_new(extra_services, propertydetails,servicename):
    """Estimation for Cleaning Service"""
    estimatedduration = 0.0

    if propertydetails.get("housetype") != None:
        housetype = propertydetails.get("housetype")
    else:
        housetype = "None"

    if propertydetails.get("numberoffloors") == None:
        numberoffloors = 0
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
    if numberofflivingroom < 1 and housetype != "office":
        numberofflivingroom = 1

    if propertydetails.get("numberoffkitchen") == None:
        numberoffkitchen = 0
    else:
        numberoffkitchen = propertydetails.get("numberoffkitchen")
    if numberoffkitchen < 1 and housetype != "office":
        numberoffkitchen = 1

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

    if propertydetails.get("withpets") == None:
        withpets = False
    else:
        withpets = propertydetails.get("withpets")

    service_type_factor = _SERVICE_TYPE_FACTORS.get(servicename)

    if housetype == "villa":
        dur_for_room = DUR_FOR_BIG_ROOM * service_type_factor
        dur_for_bathroom = DUR_FOR_NORMAL_BATHROOM * service_type_factor
    else:
        dur_for_room = DUR_FOR_NORMAL_ROOM * service_type_factor
        dur_for_bathroom = DUR_FOR_BIG_BATHROOM * service_type_factor

    estimatedduration = estimatedduration + numberoffbedroom * dur_for_room
    estimatedduration = estimatedduration + numberofflivingroom * dur_for_room
    estimatedduration = estimatedduration + numberoffkitchen * dur_for_room
    estimatedduration = estimatedduration + numberoffofficeroom * dur_for_room
    estimatedduration = estimatedduration + numberoffbathroom * dur_for_bathroom


    # Check min for estimatedduration
    if servicename == "O_DeepHome":
        property_details_preset = _PROPERTY_DEEPHOME_PRESET.get(housetype)
    else:
        property_details_preset = _PROPERTY_DETAIL_PRESET.get(housetype)
    if housetype == "building/multi-storey house":
        floor_key = str(numberoffloors) + "-Storey"
        property_details_preset = property_details_preset.get(floor_key)
    number_of_rooms_preset = property_details_preset.get(totalarea)
    estimated_duration_preset = number_of_rooms_preset.get("estimated duration")
    estimated_duration_min = estimated_duration_preset.get("min")
    estimated_duration_max = estimated_duration_preset.get("max")
    estimated_duration_recommended = number_of_rooms_preset.get("recommended duration")
    recommended_no_of_workers = number_of_rooms_preset.get("recommended number of workers")
    if recommended_no_of_workers == None:
        recommended_no_of_workers = 1

    if totalarea == "< 50m2":
        estimatedduration = estimated_duration_recommended

    if estimatedduration < estimated_duration_recommended:
        estimatedduration = estimated_duration_recommended

    if estimatedduration > estimated_duration_max:
        estimatedduration = estimated_duration_max

    # Extra Services
    ironingclothes = extra_services.get("ironingclothes")
    handwashclothes = extra_services.get("handwashclothes")
    if ironingclothes:
        estimatedduration = estimatedduration + DUR_FOR_IRONINGCLOTHES
    if handwashclothes:
        estimatedduration = estimatedduration + DUR_FOR_HANDWASHCLOTHES
    if withpets:
        estimatedduration = estimatedduration + DUR_FOR_WITHPETS * service_type_factor

    estimatedduration = math.ceil(estimatedduration)

    if estimatedduration > estimated_duration_max:
        estimatedduration = estimated_duration_max

    return estimated_duration_min, estimatedduration, estimated_duration_max, recommended_no_of_workers


def get_estimated_duration_new(extra_services, propertydetails,subscription_schedule_details, servicename):
    estimatedduration = 0.0
    dur_min = 0.0
    dur_max = 0.0

    if servicename == "O_Basic" or servicename == "O_DeepHome":
        dur_min, estimatedduration, dur_max, recommended_no_of_workers = get_estimated_duration_for_cleaning_new(extra_services, propertydetails,servicename)
    elif servicename == "S_Basic":
        if propertydetails != None and json.dumps(propertydetails) != "{}":
            dur_min, estimatedduration, dur_max, recommended_no_of_workers  = get_estimated_duration_for_cleaning_new(extra_services, propertydetails,servicename)
        elif subscription_schedule_details != None:
            estimatedduration = subscription_schedule_details.get("workingduration")
            dur_min = estimatedduration
            dur_max = estimatedduration
        else:
            estimatedduration = 0.0
            dur_min = estimatedduration
            dur_max = estimatedduration

    return dur_min, estimatedduration, dur_max, recommended_no_of_workers


def get_used_servicecode_details(servicecode):
    error_messagge = ""
    servicecodelist = servicecode.split("_")
    servicename = servicecodelist[0] + "_" + servicecodelist[1]

    if servicename == "O_Sofa":
        error_messagge  = "Request extra hours for Sofa Cleaning in NOT availabble at present! "
    elif len(servicecodelist) != 5:
        error_messagge = "Incorrect Service Code was used! "
    if len(error_messagge) > 0:
        return "","","","",error_messagge

    city = servicecodelist[2]
    area = servicecodelist[3]
    base_code = servicecodelist[4]

    return servicename, city, area, base_code, error_messagge


def check_valid_extra_hours_request(servicecode,extra_hours_request):
    error_messagge = ""
    servicename = ""
    city = ""
    area = ""
    base_code = ""
    allowed_base_codes = {
        "O_Basic":['P2h','P3h','P4h'],
        "S_Basic":['P2h','P3h','P4h'],
        "O_DeepHome":['P4h']
    }

    if servicecode != None:
        servicename, city, area, base_code, error_messagge = get_used_servicecode_details(servicecode)
        if len(error_messagge) > 0:
            return servicename, city, area, base_code, error_messagge

        if city not in _CITY_LIST:
            error_messagge  = "Incorrect Service Code (city: " + city + ") was used! "
        if area not in _AREA_LIST:
            error_messagge  = "Incorrect Service Code (area: " + area + ") was used! "
        fee_available = servicename + "_" + city
        if fee_available not in _FEE_LIST_AVAILABLE:
            error_messagge  = "Incorrect Service Code (service fee: " + fee_available + ") was used! "
        if base_code not in allowed_base_codes.get(servicename):
            error_messagge  = "Incorrect Service Code (base_code: " + base_code + ") was used!"
    else:
        error_messagge = error_messagge + "Service Code is required!;  "

    if extra_hours_request.get("extra_duration") != None:
        extra_duration = extra_hours_request.get("extra_duration")
        if extra_duration < 1 or extra_duration > 8:
            error_messagge = error_messagge + "extra_duration must be > 0 and <= 8;  "
    else:
        error_messagge = error_messagge + "extra_duration is required!;  "

    return servicename, city, area, base_code, error_messagge


def extra_fee_extra_hours_request(Extra_Service_Fee_Details, feelist):
    """Calculates additional fee for extra hours request"""

    extra_fee = 0.0
    if Extra_Service_Fee_Details.get("is_NewYear") == True:
        extra_fee += feelist["LNY"]
    elif Extra_Service_Fee_Details.get("is_BeforeNewYear04Days") == True:
        extra_fee += feelist["BLNY04"]
    elif Extra_Service_Fee_Details.get("is_BeforeNewYear07Days") == True:
        extra_fee += feelist["BLNY07"]
    elif Extra_Service_Fee_Details.get("is_BeforeNewYear10Days") == True:
        extra_fee += feelist["BLNY10"]
    elif Extra_Service_Fee_Details.get("is_AfterNewYear04Days") == True:
        extra_fee += feelist["ALNY04"]
    elif Extra_Service_Fee_Details.get("is_AfterNewYear07Days") == True:
        extra_fee += feelist["ALNY07"]
    elif Extra_Service_Fee_Details.get("is_Holiday") == True:
        extra_fee += feelist["HOL"]
    elif Extra_Service_Fee_Details.get("is_Weekend") == True:
        extra_fee += feelist["WKD"]
    elif Extra_Service_Fee_Details.get("is_OutOfficeHours") == True:
        extra_fee += feelist["OOH"]

    return extra_fee


def get_new_base_code(base_code,extra_duration):
    if extra_duration <= 2:
        new_base_code = "P2h"
    elif extra_duration == 3:
        new_base_code = "P3h"
    else:
        new_base_code = "P4h"
    return new_base_code


def get_extra_hours_request(servicecode, extra_hours_request,service_fee_list):
    error_messagge = ""
    fee_details_response = {}

    extra_duration = extra_hours_request.get("extra_duration")
    servicename, city, area, base_code, error_messagge = get_used_servicecode_details(servicecode)

    if servicename != "O_DeepHome":
        new_base_code = get_new_base_code(base_code,extra_duration)
    else:
        new_base_code = "P4h"
    basename = area + "_" + new_base_code
    base_rate = service_fee_list[basename]

    extra_fee = 0.0
    if extra_hours_request.get("Extra Service Fee Details") != None:
        Extra_Service_Fee_Details = extra_hours_request.get("Extra Service Fee Details")
        extra_fee = extra_fee_extra_hours_request(Extra_Service_Fee_Details, service_fee_list)

    final_rate = base_rate * (1 + extra_fee)
    total_fee = final_rate * extra_duration

    servicecode_used = servicename + "_" + city + "_" + basename
    fee_details_response = {"Total Fee": int(total_fee), "Service Code Used": servicecode_used, "Extra Service Fee Details":Extra_Service_Fee_Details}

    return fee_details_response


def get_compound_extra_fee(fee_details_response,feename,feelist,feelistkey):
    extra_fee_percent = feelist.get(feelistkey)
    for key in fee_details_response.keys():
        if key == "Total Fee":
            total_fee = fee_details_response.get("Total Fee")
            compound_fee = round(total_fee * extra_fee_percent,-2)
            new_total_fee = total_fee + compound_fee
            new_fee_details_response = fee_details_response
            compound_fee_response = {"Total Fee": new_total_fee, feename: compound_fee}
            new_fee_details_response.update(compound_fee_response)
            return new_fee_details_response


def get_active_city_fee_list(feedatalist, city):
    #feedatalist.reverse()
    fee_list = {}
    fee_found = False
    for this_item in reversed(feedatalist):
        if this_item.get("active"):
            all_fee_list = this_item.get("fee_list")
            for key in all_fee_list.keys():
                if key == city:
                    return all_fee_list.get(city),True

    return fee_list, fee_found
