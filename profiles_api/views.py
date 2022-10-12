from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from profiles_api import serializers
from profiles_api import models
from profiles_api import permissions

import json
import jsonfield
import datetime
from datetime import date
from datetime import time

_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-01-31","2022-02-01","2022-02-02","2022-02-03","2022-02-04","2022-02-05")
_BEFORE_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-01-30","2022-01-29","2022-01-28")
_AFTER_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-02-06","2022-02-07","2022-02-08")
_OTHER_NATIONAL_HOLIDAY_DAYS_2022 = ("2022-01-01","2022-01-02","2022-01-03","2022-04-10","2022-04-11","2022-04-30","2022-05-01","2022-05-02","2022-05-03","2022-09-01","2022-09-02")
_OTHER_NATIONAL_HOLIDAY_NAMES = ("International New Year's Day","New Year's Day Holiday","Day off for International New Year's Day","Hung Kings Festival","Day off for Hung Kings Festival","Reunification Day","International Labor Day","Independence Day Holiday","Independence Day")
_CITY_LIST = ('001','079','048','031','092','001','002','004','006','008','010',
'011','012','014','015','017','019','019','020','022','024','025','026','027',
'030','033','034','035','036','037','038','040','042','044','045','046','049',
'051','052','054','056','058','060','062','064','064','066','067','068','070',
'072','074','075','077','080','082','083','084','086','087','089','091','093',
'095','094','096')
_AREA_LIST = ('I','II','III')
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
        }
    }
}
_Fee_List_Available = ("O_Basic_079","S_Basic_079")
_DEFAUT_SERVICE_FEE_DETAILS = {"is_OutOfficeHours":False, "is_Weekend":False, "is_Holiday":False, "is_NewYear":False, "is_BeforeNewYear":False, "is_AfterNewYear":False, "is_OwnTools":False}

class HelloApiView(APIView):
    """Test API View"""
    serializer_class = serializers.HelloSerializer

    def get(self, request, format=None):
        """Returns a list of APIView features"""
        an_apiview = [
            'Uses HTTP methods as function (get, post, patch, put, delete)',
            'Is similar to a traditional Django View',
            'Gives you the most control over you application logic',
            'Is mapped manually to URLs',
        ]

        return Response({'message': 'Hello!', 'an_apiview': an_apiview})

    def post(self, request):
        """Create a hello message with our name"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'Hello {name}'
            return Response({'message': message})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, pk=None):
        """"Handle updating an object"""
        return Response({'method': 'PUT'})

    def patch(self, request, pk=None):
        """Handle a partial update of an object"""
        return Response({'method': 'PATCH'})

    def delete(self, request, pk=None):
        """Delete an object"""
        return Response({'method': 'DELETE'})


class HelloViewSet(viewsets.ViewSet):
    """Test API ViewSet"""
    serializer_class = serializers.HelloSerializer

    def list(self, request):
        """Return a hello message"""
        a_viewset = [
            'Uses actions (list, create,retrieve, update, partial_update)',
            'Automatically maps to URLs using Routers',
            'Provides more functionality with less code',
        ]

        return Response({'message': 'Hello!', 'a_viewset': a_viewset})

    def create(self, request):
        """Create a new hello message"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            message = f'HelloHello {name}!'
            fee_detail = {}
            fee_detail["is_AfterNewYear"] = True
            return Response({'message': message,"extra_service_fee_details":fee_detail})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, pk=None):
        """Handle getting an object by its ID"""
        return Response({'http_method': 'GET'})

    def update(self, request, pk=None):
        """Handle updating an object"""
        return Response({'http_method': 'PUT'})

    def partial_update(self, request, pk=None):
        """Handle updating part of an object"""
        return Response({'http_method': 'PATCH'})

    def destroy(self, request, pk=None):
        """Handle removing an object"""
        return Response({'http_method': 'DELETE'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """Handle creating and updating profiles"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.UpdateOwnProfile,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'email',)


class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileFeedViewSet(viewsets.ModelViewSet):
    """Handles creating, reading and updating profile feed items"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ProfileFeedItemSerializer
    queryset = models.ProfileFeedItem.objects.all()
    permission_classes = (permissions.UpdateOwnStatus, IsAuthenticated)

    def perform_create(self, serializer):
        """Sets the user profile to the logged in user"""
        serializer.save(user_profile=self.request.user)


# One_Off_Fee calculation
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
    if fee_available not in _Fee_List_Available:
        error_messagge  = error_messagge + "INVALID service code or Fee List for " + fee_available + " NOT yet availabble"
    if duration == 0 and json.dumps(propertydetails) == "{}":
        error_messagge  = error_messagge + "Both duration = 0 and propertydetails is empty; " + json.dumps(propertydetails)
    return error_messagge


def get_estimated_duration(propertydetails):
    housetype = propertydetails["housetype"]
    numberoffloors = propertydetails["numberoffloors"]
    numberoffbedroom = propertydetails["numberoffbedroom"]
    numberoffbathroom = propertydetails["numberoffbathroom"]
    totalarea = propertydetails["totalarea"]
    withpets = propertydetails["withpets"]
    ironingclothes = propertydetails["ironingclothes"]

    estimatedduration = numberoffbedroom * 0.5
    estimatedduration = estimatedduration + numberoffbathroom * 0.3
    if housetype == "building/multi-storey house":
        estimatedduration = estimatedduration + 0.5
    if withpets:
        estimatedduration = estimatedduration + 0.5
    if ironingclothes:
        estimatedduration = estimatedduration + 0.5

    # Check min for estimatedduration
    if estimatedduration < 4.0 and totalarea == "140 - 255 m2":
        estimatedduration = 4.0
    elif estimatedduration < 3.0 and totalarea == "90 - 140 m2":
        estimatedduration = 3.0
    elif estimatedduration < 3.0 and housetype == "villa":
        estimatedduration = 3.0
    elif estimatedduration < 3.0 and numberoffbedroom >= 3:
        estimatedduration = 3.0
    elif estimatedduration < 2.0:
        estimatedduration = 2.0

    # Check max for estimatedduration
    if estimatedduration > 3.0 and (totalarea == "<50 m2" or totalarea == "90 - 140 m2"):
        estimatedduration = 3.0

    return int(estimatedduration)


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


class One_Off_Fee_View(viewsets.ModelViewSet):
    queryset = models.One_Off_Fee.objects.all()
    serializer_class = serializers.One_Off_Fee_Serializer

    def create(self,request):
        """Create a fee calculation """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            servicecode = serializer.validated_data.get("servicecode")
            bookdate = serializer.validated_data.get("bookdate")
            starttime = serializer.validated_data.get("starttime")
            duration = serializer.validated_data.get("duration")
            owntool = serializer.validated_data.get("owntool")
            propertydetails = serializer.validated_data.get("propertydetails")

            servicecodelist = servicecode.split("_")
            city = servicecodelist[2]
            area = servicecodelist[3]
            servicename = servicecodelist[0] + "_" + servicecodelist[1]
            error_messagge = check_valid_input(city,area,servicename,duration,propertydetails)
            if len(error_messagge) > 0:
                content = {'error message': error_messagge}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            city_fee_list = _DEFAUT_FEE_LIST[city]
            service_fee_list = city_fee_list[servicename]
            usedduration = duration

            if duration == 0:
                estimatedduration = get_estimated_duration(propertydetails)
                usedduration = estimatedduration
            fee_details = get_base_rate(area,usedduration,service_fee_list)
            base_rate = fee_details["base_rate"]
            fee_detail = fee_details["fee_detail"]
            if base_rate == 0:
                content = {'error message': 'could not get base rate'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            extra_fee = extra_fee_special_day(bookdate,starttime,service_fee_list)
            total_fee = base_rate * usedduration * (1 + extra_fee["extra_fee_percent"])
            extra_service_fee_details = extra_fee["extra_service_fee_details"]

            if owntool == True:
                total_fee += service_fee_list["OwnTools"]
                extra_service_fee_details["is_OwnTools"] = True

            extra_service_fee_details.update(fee_detail)

            if duration == 0:
                return Response({"Total Fee": total_fee, "Estimated Duration": estimatedduration, "Extra Service Fee Details": extra_service_fee_details})
            else:
                return Response({"Total Fee": total_fee, "Extra Service Fee Details": extra_service_fee_details})
        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)
