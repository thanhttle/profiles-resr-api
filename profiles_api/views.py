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
import datetime
from datetime import date
from datetime import time

_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-01-31","2022-02-01","2022-02-02","2022-02-03","2022-02-04","2022-02-05")
_BEFORE_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-01-30","2022-01-29","2022-01-28")
_AFTER_LUNAR_NEW_YEAR_DAYS_2022 = ("2022-02-06","2022-02-07","2022-02-08")
_OTHER_NATIONAL_HOLIDAY_DAYS_2022 = ("2022-01-01","2022-01-02","2022-01-03","2022-04-10","2022-04-11","2022-04-30","2022-05-01","2022-05-02","2022-05-03","2022-09-01","2022-09-02")
_OTHER_NATIONAL_HOLIDAY_NAMES = ("International New Year's Day","New Year's Day Holiday","Day off for International New Year's Day","Hung Kings Festival","Day off for Hung Kings Festival","Reunification Day","International Labor Day","Independence Day Holiday","Independence Day")

_DEFAUT_FEE_LIST = {"BaseRateHCM":66500, "3h_slot":0.05, "2h_slot":0.26, "OutOfficeHours": 0.16, "Weekend":0.21, "Holiday": 0.32, "NewYear":2.0, "BeforeNewYear":1.0, "AfterNewYear":1.0, "FavoriteMaid":0, "OwnTools":30000, "Area01":0, "Area02":0, "Area03":0, "BaseRateDN":55000, "BaseRateHN":66500}
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
        ""Handle updating an object""
        return Response({'method': 'PUT'})

    def patch(self, request, pk=None):
        ""Handle a partial update of an object
        return Response({'method': 'PATCH'})

    def delete(self, request, pk=None):
        "Delete an object""
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
def get_base_rate(city,feelist):
	""" return base rate for city"""

	if city == "Ho Chi Minh":
		base_rate = feelist["BaseRateHCM"]
	elif city == "Ha Noi":
		base_rate = feelist["BaseRateHN"]
	elif city == "Da Nang":
		base_rate = feelist["BaseRateDN"]
	else:
		base_rate = 0

	return base_rate


def is_weekend(bookdate):
	days = str(bookdate).split('-')
	d = date(int(days[0]), int(days[1]), int(days[2]))

	return d.weekday() > 4


def is_OutOfWorkingHour(starttime):
	timelist = str(starttime).split(":")
	time_formated = time(int(timelist[0]),int(timelist[1]),int(timelist[2]))
	return time_formated < time(8,0,0) or time_formated >= time(17,0,0)


def extra_fee_special_day(bookdate, starttime, duration, feelist):
	"""Calculates additional fee based on date & time of booking"""
	fee_detail = {}
	extra_fee = 0.0
	if bookdate in _LUNAR_NEW_YEAR_DAYS_2022:
		fee_detail["is_NewYear"] = True
		extra_fee += feelist["NewYear"]
	elif bookdate in _BEFORE_LUNAR_NEW_YEAR_DAYS_2022:
		fee_detail["is_BeforeNewYear"] = True
		extra_fee += feelist["BeforeNewYear"]
	elif bookdate in _AFTER_LUNAR_NEW_YEAR_DAYS_2022:
		fee_detail["is_AfterNewYear"] = True
		extra_fee += feelist["AfterNewYear"]
	elif bookdate in _OTHER_NATIONAL_HOLIDAY_DAYS_2022:
		fee_detail["is_Holiday"] = True
		extra_fee += feelist["Holiday"]
	elif is_weekend(bookdate):
		fee_detail["is_Weekend"] = True
		extra_fee += feelist["Weekend"]
	elif is_OutOfWorkingHour(starttime):
		fee_detail["is_OutOfficeHours"] = True
		extra_fee += feelist["OutOfficeHours"]

	if duration == 2:
		extra_fee += feelist["2h_slot"]
		fee_detail["is_2h_slot"] = True
	if duration == 3:
		extra_fee += feelist["3h_slot"]
		fee_detail["is_3h_slot"] = True

	return {"extra_fee_percent": extra_fee,"extra_service_fee_details":fee_detail}


class One_Off_Fee_View(viewsets.ModelViewSet):
    queryset = models.One_Off_Fee.objects.all()
    serializer_class = serializers.One_Off_Fee_Serializer

    def create(self,request):
        """Create a fee calculation """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            city = serializer.validated_data.get("city")
            area = serializer.validated_data.get("area")
            bookdate = serializer.validated_data.get("bookdate")
            starttime = serializer.validated_data.get("starttime")
            duration = serializer.validated_data.get("duration")
            owntool = serializer.validated_data.get("owntool")
            feelistStr = serializer.validated_data.get("feelist")
            feelist = json.loads(feelistStr)

            base_rate = get_base_rate(city, feelist)
            if base_rate == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            extra_fee = extra_fee_special_day(bookdate,starttime,duration,feelist)
            total_fee = base_rate * duration * (1 + extra_fee["extra_fee_percent"])
            extra_service_fee_details = extra_fee["extra_service_fee_details"]

            if owntool == True:
                total_fee += feelist["OwnTools"]
                extra_service_fee_details["is_OwnTools"] = True

            return Response({"Total Fee": total_fee, "Extra Service Fee Details": extra_service_fee_details})
        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)


        """
	def create(self, request):
        Create a new hello message
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            city = serializer.validated_data.get("city")
            area = serializer.validated_data.get("area")
			bookdate = serializer.validated_data.get("bookdate")
			starttime = serializer.validated_data.get("starttime")
			duration = serializer.validated_data.get("duration")
			owntool = serializer.validated_data.get("owntool")
            feelistInput = serializer.validated_data.get("feelist")
            feelist = json.loads(feelistInput)

			base_rate = get_base_rate(city, feelist)
			if base_rate == 0:
				return Response(status=status.HTTP_400_BAD_REQUEST)

			extra_fee = extra_fee_special_day(bookdate,starttime,duration,feelist)
			total_fee = base_rate * duration * (1 + extra_fee["extra_fee_percent"])
			extra_service_fee_details = extra_fee["extra_service_fee_details"]

			if owntool == True:
				total_fee += feelist["OwnTools"]
				extra_service_fee_details["is_OwnTools"] = True

			message = {
				"city": "Ho Chi Minh",
				"area": "Area06",
				"bookdate": "2022-10-03",
				"starttime": "18:00:00",
				"duration": 3,
				"owntool": owntool,
				"feelist": {"BaseRateHCM":66500, "3h_slot":0.05, "2h_slot":0.26, "OutOfficeHours": 0.16, "Weekend":0.21, "Holiday": 0.32, "NewYear":2.0, "BeforeNewYear":1.0, "AfterNewYear":1.0, "FavoriteMaid":0, "OwnTools":30000, "Area01":0, "Area02":0, "Area03":0, "BaseRateDN":55000, "BaseRateHN":66500}
			}

			return Response({"Total Fee": total_fee, "Extra Service Fee Details": extra_service_fee_details})
		else:
			return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)
"""
