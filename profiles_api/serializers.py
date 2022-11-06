from rest_framework import serializers

from profiles_api import models


class HelloSerializer(serializers.Serializer):
    """Serializes a name field for testing our APIView"""
    name = serializers.CharField(max_length=10)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a user profile object"""

    class Meta:
        model = models.UserProfile
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create and return a new user"""
        user = models.UserProfile.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )

        return user

    def update(self, instance, validated_data):
        """Handle updating user account"""
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        return super().update(instance, validated_data)


class ProfileFeedItemSerializer(serializers.ModelSerializer):
    """Serializes profile feed items"""

    class Meta:
        model = models.ProfileFeedItem
        fields = ('id', 'user_profile', 'status_text', 'created_on')
        extra_kwargs = {'user_profile': {'read_only': True}}


class Test_One_Off_Fee_Serializer(serializers.ModelSerializer):
	class Meta:
		model = models.Test_One_Off_Fee
		fields = ('id', 'bookdate', 'starttime', 'duration', 'owntool', 'ironingclothes', 'servicecode', 'propertydetails', 'subscription_schedule_details')


class One_Off_Fee_Serializer(serializers.ModelSerializer):
	class Meta:
		model = models.One_Off_Fee
		fields = ('id', 'bookdate', 'starttime', 'duration', 'owntool', 'ironingclothes', 'servicecode', 'propertydetails')


class Service_Fee_List_Serializer(serializers.ModelSerializer):
    """Serializes Service_Fee_List"""

    class Meta:
        model = models.Service_Fee_List
        fields = ('id', 'fee_list', 'created_on')
        extra_kwargs = {'feename': {'read_only': True}}
