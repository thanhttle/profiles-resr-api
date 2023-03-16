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
from profiles_api import service_fee_calculation as sfc
from profiles_api import test_service_fee_calculation as test_sfc
from profiles_api import service_fee_list_calculation as sflc

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


class Test_One_Off_Fee_View(viewsets.ModelViewSet):
    queryset = models.Test_One_Off_Fee.objects.all()
    serializer_class = serializers.Test_One_Off_Fee_Serializer

    def create(self,request):
        """Create a fee calculation """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            servicecode = serializer.validated_data.get("servicecode")
            bookdate = serializer.validated_data.get("bookdate")
            starttime = serializer.validated_data.get("starttime")
            duration = serializer.validated_data.get("duration")
            owntool = serializer.validated_data.get("owntool")
            ironingclothes = serializer.validated_data.get("ironingclothes")
            urgentbooking = serializer.validated_data.get("urgentbooking")
            locationdetails = serializer.validated_data.get("locationdetails")
            propertydetails = serializer.validated_data.get("propertydetails")
            subscription_schedule_details = serializer.validated_data.get("subscription_schedule_details")
            extra_hours_request = serializer.validated_data.get("extra_hours_request")
            premiumservices = serializer.validated_data.get("premiumservices")
            foreignlanguage = serializer.validated_data.get("foreignlanguage")
            handwashclothes = serializer.validated_data.get("handwashclothes")
            numberofworkers = serializer.validated_data.get("numberofworkers")

            feedatalist = models.Service_Fee_List.objects.values()

            if extra_hours_request != None:
                servicename, city, area, base_code, error_messagge = test_sfc.check_valid_extra_hours_request(servicecode,extra_hours_request)
                if len(error_messagge) > 0:
                    content = {'error message': "extra_hours_request: " + error_messagge}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                #city_fee_list = test_sfc._DEFAUT_FEE_LIST[city]
                city_fee_list,feelist_found = test_sfc.get_active_city_fee_list(feedatalist,city)
                if not feelist_found:
                    content = {'error message': 'could not get fee_list for city: ' + city}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                service_fee_list = city_fee_list[servicename]
                fee_details_response = test_sfc.get_extra_hours_request(servicecode,extra_hours_request,service_fee_list)

            else:
                servicename, city, area, district_found = test_sfc.get_servicecode_details(servicecode,locationdetails)
                if duration == None:
                    duration =  0
                if numberofworkers == None:
                    numberofworkers = 1

                error_messagge = test_sfc.check_valid_input(city,area,servicename,duration,propertydetails,subscription_schedule_details)
                #error_messagge = error_messagge + test_sfc.check_validBookingTime(bookdate, starttime)
                if len(error_messagge) > 0:
                    content = {'error message': error_messagge}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                #city_fee_list = test_sfc._DEFAUT_FEE_LIST[city]
                city_fee_list,feelist_found = test_sfc.get_active_city_fee_list(feedatalist,city)
                if not feelist_found:
                    content = {'error message': 'could not get fee_list for city: ' + city}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                service_fee_list = city_fee_list[servicename]
                usedduration = duration
                estimatedduration = 0
                dur_min = 0
                dur_max = 0
                used_numberofworkers = numberofworkers
                recommended_no_of_workers = 1

                if servicename == "O_Sofa":
                    fee_details_response = test_sfc.get_estimated_fee_sofacleaning(bookdate,starttime,propertydetails,urgentbooking,service_fee_list)
                    servicecode_used = servicename + "_" + city
                    servicecode_response = {"Service Code Used": servicecode_used,"District":district_found}
                    fee_details_response.update(servicecode_response)
                else:
                    extra_services = {
                        "ironingclothes":False,
                        "handwashclothes":False}
                    if ironingclothes:
                        extra_services.update({"ironingclothes":True})
                    if handwashclothes:
                        extra_services.update({"handwashclothes":True})
                    if duration == 0:
                        estimatedduration = test_sfc.get_estimated_duration(extra_services,propertydetails,subscription_schedule_details,servicename)
                        if estimatedduration == 0:
                            content = {'error message': 'could not estimate duration'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                        usedduration = estimatedduration
                    if duration == -1:
                        dur_min, estimatedduration, dur_max, recommended_no_of_workers = test_sfc.get_estimated_duration_new(extra_services,propertydetails,subscription_schedule_details,servicename)
                        if estimatedduration == 0:
                            content = {'error message': 'could not estimate duration'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                        usedduration = estimatedduration
                        used_numberofworkers = recommended_no_of_workers
                    base_rate, fee_detail, basename = test_sfc.get_base_rate(area,usedduration,service_fee_list)
                    servicecode_used = servicename + "_" + city + "_" + basename
                    if base_rate == 0:
                        content = {'error message': 'could not get base rate' + str(estimatedduration)}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)

                    if servicename == "O_Basic":
                        fee_details_response = test_sfc.get_O_Basic_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail,used_numberofworkers)
                    elif servicename == "S_Basic":
                        fee_details_response = test_sfc.get_S_Basic_fee_details_response(subscription_schedule_details,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail,used_numberofworkers)
                    elif servicename == "O_DeepHome":
                        fee_details_response = test_sfc.get_O_DeepHome_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail,used_numberofworkers)
                    else :
                        fee_details_response = {}

                    servicecode_response = {"Service Code Used": servicecode_used,"District":district_found}
                    fee_details_response.update(servicecode_response)

                    if dur_min > 0 and dur_max > 0:
                        duration_minmax_response = {"Minimum Duration":dur_min,"Maximum Duration":dur_max}
                        fee_details_response.update(duration_minmax_response)

            if foreignlanguage:
                feename = "Foreign Language Fee"
                feelistkey = "ForeignLang"
                fee_details_response = test_sfc.get_compound_extra_fee(fee_details_response,feename,service_fee_list,feelistkey)

            if premiumservices and servicename != "O_DeepHome":
                feename = "Preminum Service Fee"
                feelistkey = "Premium"
                fee_details_response = test_sfc.get_compound_extra_fee(fee_details_response,feename,service_fee_list,feelistkey)

            return Response(fee_details_response)

        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)

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
            ironingclothes = serializer.validated_data.get("ironingclothes")
            urgentbooking = serializer.validated_data.get("urgentbooking")
            locationdetails = serializer.validated_data.get("locationdetails")
            propertydetails = serializer.validated_data.get("propertydetails")
            subscription_schedule_details = serializer.validated_data.get("subscription_schedule_details")
            extra_hours_request = serializer.validated_data.get("extra_hours_request")
            premiumservices = serializer.validated_data.get("premiumservices")
            foreignlanguage = serializer.validated_data.get("foreignlanguage")
            handwashclothes = serializer.validated_data.get("handwashclothes")

            feedatalist = models.Service_Fee_List.objects.values()

            if extra_hours_request != None:
                servicename, city, area, base_code, error_messagge = sfc.check_valid_extra_hours_request(servicecode,extra_hours_request)
                if len(error_messagge) > 0:
                    content = {'error message': "extra_hours_request: " + error_messagge}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                #city_fee_list = sfc._DEFAUT_FEE_LIST[city]
                city_fee_list,feelist_found = sfc.get_active_city_fee_list(feedatalist,city)
                if not feelist_found:
                    content = {'error message': 'could not get fee_list for city: ' + city}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                service_fee_list = city_fee_list[servicename]
                fee_details_response = sfc.get_extra_hours_request(servicecode,extra_hours_request,service_fee_list)

            else:
                servicename, city, area, district_found = sfc.get_servicecode_details(servicecode,locationdetails)
                if duration == None:
                    duration =  0

                error_messagge = sfc.check_valid_input(city,area,servicename,duration,propertydetails,subscription_schedule_details)
                #error_messagge = error_messagge + sfc.check_validBookingTime(bookdate, starttime)
                if len(error_messagge) > 0:
                    content = {'error message': error_messagge}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                #city_fee_list = sfc._DEFAUT_FEE_LIST[city]
                city_fee_list,feelist_found = sfc.get_active_city_fee_list(feedatalist,city)
                if not feelist_found:
                    content = {'error message': 'could not get fee_list for city: ' + city}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                service_fee_list = city_fee_list[servicename]
                usedduration = duration
                estimatedduration = 0
                dur_min = 0
                dur_max = 0

                if servicename == "O_Sofa":
                    fee_details_response = sfc.get_estimated_fee_sofacleaning(bookdate,starttime,propertydetails,urgentbooking,service_fee_list)
                    servicecode_used = servicename + "_" + city
                    servicecode_response = {"Service Code Used": servicecode_used,"District":district_found}
                    fee_details_response.update(servicecode_response)
                else:
                    extra_services = {
                        "ironingclothes":False,
                        "handwashclothes":False}
                    if ironingclothes:
                        extra_services.update({"ironingclothes":True})
                    if handwashclothes:
                        extra_services.update({"handwashclothes":True})
                    if duration == 0:
                        estimatedduration = sfc.get_estimated_duration(extra_services,propertydetails,subscription_schedule_details,servicename)
                        if estimatedduration == 0:
                            content = {'error message': 'could not estimate duration'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                        usedduration = estimatedduration
                    if duration == -1:
                        dur_min, estimatedduration, dur_max = sfc.get_estimated_duration_new(extra_services,propertydetails,subscription_schedule_details,servicename)
                        if estimatedduration == 0:
                            content = {'error message': 'could not estimate duration'}
                            return Response(content, status=status.HTTP_400_BAD_REQUEST)
                        usedduration = estimatedduration
                    base_rate, fee_detail, basename = sfc.get_base_rate(area,usedduration,service_fee_list)
                    servicecode_used = servicename + "_" + city + "_" + basename
                    if base_rate == 0:
                        content = {'error message': 'could not get base rate' + str(estimatedduration)}
                        return Response(content, status=status.HTTP_400_BAD_REQUEST)

                    if servicename == "O_Basic":
                        fee_details_response = sfc.get_O_Basic_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail)
                    elif servicename == "S_Basic":
                        fee_details_response = sfc.get_S_Basic_fee_details_response(subscription_schedule_details,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail)
                    elif servicename == "O_DeepHome":
                        #fee_details_response  = {"owntool":str(owntool),"ironingclothes":str(ironingclothes),"fee_detail":str(fee_detail)}
                        fee_details_response = sfc.get_O_DeepHome_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,extra_services,urgentbooking,fee_detail)
                    else :
                        fee_details_response = {}

                    servicecode_response = {"Service Code Used": servicecode_used,"District":district_found}
                    fee_details_response.update(servicecode_response)

                    if dur_min > 0 and dur_max > 0:
                        duration_minmax_response = {"Minimum Duration":dur_min,"Maximum Duration":dur_max}
                        fee_details_response.update(duration_minmax_response)

            if foreignlanguage:
                feename = "Foreign Language Fee"
                feelistkey = "ForeignLang"
                fee_details_response = sfc.get_compound_extra_fee(fee_details_response,feename,service_fee_list,feelistkey)

            if premiumservices and servicename != "O_DeepHome":
                feename = "Preminum Service Fee"
                feelistkey = "Premium"
                fee_details_response = sfc.get_compound_extra_fee(fee_details_response,feename,service_fee_list,feelistkey)

            return Response(fee_details_response)

        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)

class Service_Fee_List_ViewSet(viewsets.ModelViewSet):
    """Handles creating, reading Service Fee List Items"""
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.Service_Fee_List_Serializer
    queryset = models.Service_Fee_List.objects.all()

    def create(self,request):
        """Create a fee list """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            from_date = serializer.validated_data.get("from_date")
            to_date = serializer.validated_data.get("to_date")
            fee_list = serializer.validated_data.get("fee_list")
            active = serializer.validated_data.get("active")
            feedatalist = models.Service_Fee_List.objects.values()
            error_msg, jsondata_valid = sflc.validate_Json_key(fee_list)
            if not jsondata_valid:
                content = {'error message': error_msg}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            fee_list_duplication, error_msg = sflc.check_fee_list_duplication(fee_list,feedatalist, -1)
            if fee_list_duplication:
                content = {'error message': 'Match active fee list city: ' + error_msg + ' Please deactivate current active fee list.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)


            serializer.save()
            return Response(serializer.data)

        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)


    def destroy(self, request, *args, **kwargs):
        """Handle deleting an object"""
        content = {'error message': 'http_method PUT is NOT allowed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
        """Handle updating an object"""
        content = {'error message': 'http_method PUT is NOT allowed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, *args, **kwargs):
        """Handle updating part of an object"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            from_date = serializer.validated_data.get("from_date")
            to_date = serializer.validated_data.get("to_date")
            fee_list = serializer.validated_data.get("fee_list")
            active = serializer.validated_data.get("active")
            feedatalist = models.Service_Fee_List.objects.values()

            fee_item = self.get_object()
            data = request.data

            # Not allow to update fee_list, from_date
            if fee_list != None or from_date != None:
                content = {'error message': "NOT allow to update from_date or fee_list data: "}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            # to_date must be later than from_date
            if to_date != None and sflc.from_later_than_to(fee_item.from_date,to_date):
                content = {'error message': "to_date must be LATER than from_date! "}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            fee_item.to_date = data.get("to_date",fee_item.to_date)

            # updating active to true is allowed if not duplicated
            fee_list_duplication = False
            if active == True and fee_item.active == False:
                fee_list_duplication, error_msg = sflc.check_fee_list_duplication(fee_item.fee_list,feedatalist, fee_item.id)
            if fee_list_duplication:
                content = {'error message': 'Match active fee list: ' + error_msg}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            fee_item.active = data.get("active",fee_item.active)
            fee_item.save()
            #serializer.save()

            serializer = serializers.Service_Fee_List_Serializer(fee_item)
            return Response(serializer.data)

        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)
