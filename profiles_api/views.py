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
            propertydetails = serializer.validated_data.get("propertydetails")
            subscription_schedule_details = serializer.validated_data.get("subscription_schedule_details")

            if duration == None:
                duration =  0

            servicename, city, area = test_sfc.get_servicecode_details(servicecode)
            error_messagge = test_sfc.check_valid_input(city,area,servicename,duration,propertydetails,subscription_schedule_details)
            if len(error_messagge) > 0:
                content = {'error message': error_messagge}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            city_fee_list = test_sfc._DEFAUT_FEE_LIST[city]
            service_fee_list = city_fee_list[servicename]
            usedduration = duration
            estimatedduration = 0

            if servicename == "O_Sofa":
                fee_details_response = test_sfc.get_estimated_fee_sofacleaning(bookdate,starttime,propertydetails,urgentbooking,service_fee_list)
                return Response(fee_details_response)

            if duration == 0:
                estimatedduration = test_sfc.get_estimated_duration(ironingclothes,propertydetails,subscription_schedule_details,servicename)
                if estimatedduration == 0:
                    content = {'error message': 'could not estimate duration'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                usedduration = estimatedduration
            base_rate, fee_detail = test_sfc.get_base_rate(area,usedduration,service_fee_list)
            if base_rate == 0:
                content = {'error message': 'could not get base rate' + str(estimatedduration)}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            if servicename == "O_Basic":
                fee_details_response = test_sfc.get_O_Basic_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,urgentbooking,fee_detail)
            elif servicename == "S_Basic":
                fee_details_response = test_sfc.get_S_Basic_fee_details_response(subscription_schedule_details,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,urgentbooking,fee_detail)
            elif servicename == "O_DeepHome":
                #fee_details_response  = {"owntool":str(owntool),"ironingclothes":str(ironingclothes),"fee_detail":str(fee_detail)}
                fee_details_response = test_sfc.get_O_DeepHome_fee_details_response(bookdate,starttime,service_fee_list,base_rate,duration,estimatedduration,usedduration,owntool,ironingclothes,urgentbooking,fee_detail)
            else :
                fee_details_response = {}

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
            propertydetails = serializer.validated_data.get("propertydetails")

            servicecodelist = servicecode.split("_")
            city = servicecodelist[2]
            area = servicecodelist[3]
            servicename = servicecodelist[0] + "_" + servicecodelist[1]
            error_messagge = sfc.check_valid_input(city,area,servicename,duration,propertydetails)
            if len(error_messagge) > 0:
                content = {'error message': error_messagge}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
            city_fee_list = sfc._DEFAUT_FEE_LIST[city]
            service_fee_list = city_fee_list[servicename]
            usedduration = duration

            if duration == 0:
                estimatedduration = sfc.get_estimated_duration(ironingclothes, propertydetails)
                if estimatedduration == 0:
                    content = {'error message': 'could not estimate duration'}
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)
                usedduration = estimatedduration
            fee_details = sfc.get_base_rate(area,usedduration,service_fee_list)
            base_rate = fee_details["base_rate"]
            fee_detail = fee_details["fee_detail"]
            if base_rate == 0:
                content = {'error message': 'could not get base rate' + str(estimatedduration)}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            extra_fee = sfc.extra_fee_special_day(bookdate,starttime,service_fee_list)
            final_rate = base_rate * (1 + extra_fee["extra_fee_percent"])
            total_fee = final_rate * usedduration
            extra_service_fee_details = extra_fee["extra_service_fee_details"]

            fee_details_response = {}
            if owntool == True:
                total_fee += service_fee_list["OwnTools"]
                extra_service_fee_details["is_OwnTools"] = True
                fee_details_response = {"Total Fee": int(total_fee),"OwnTools Fee":service_fee_list["OwnTools"]}
            else:
                fee_details_response = {"Total Fee": int(total_fee)}

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
            fee_list = serializer.validated_data.get("fee_list")
            #feedatalist = list(models.Service_Fee_List.objects.values())
            feedatalist = models.Service_Fee_List.objects.values()
            if not sflc.validate_Json(fee_list) or not sflc.validate_Json_key(fee_list):
                content = {'error message': 'invalid fee_list json'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            fee_list_duplication, error_msg = sflc.check_fee_list_duplication(fee_list,feedatalist)
            if fee_list_duplication:
                #content = {'error message': 'Fee data exist. Please use PATCH() method to update "to" key.'}
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)


            serializer.save()
            #return Response(serializer.save(),status=status.HTTP_201_CREATED)
        else:
            return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)

    def update(self, request, pk=None):
        """Handle updating an object"""
        content = {'error message': 'http_method PUT is NOT allowed'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


    def partial_update(self, request, pk):
        """Handle updating part of an object"""
        #fee_item = get_object_or_404(Car, id=kwargs.get('pk'))
        fee_items = models.Service_Fee_List.objects.values()
        #fee_item = fee_items.get('id':)
        content = {'error message': str(pk) + " "  + str(self)}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
