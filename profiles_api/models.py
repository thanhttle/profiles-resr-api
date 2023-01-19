import jsonfield
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.conf import settings


class UserProfileManager(BaseUserManager):
	"""Manager for user profiles"""

	def create_user(self, email, name, password=None):
		"""Create a new user profile"""
		if not email:
			raise ValueError('User must have an email address')

		email = self.normalize_email(email)
		user = self.model(email=email, name=name)

		user.set_password(password)
		user.save(using=self._db)

		return user

	def create_superuser(self, email, name, password):
		"""Create and save a new superuser with given details"""
		user = self.create_user(email, name, password)

		user.is_superuser = True
		user.is_staff = True
		user.save(using=self._db)

		return user

class UserProfile(AbstractBaseUser, PermissionsMixin):
	"""Database model for users in the system"""
	email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(max_length=255)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)

	objects = UserProfileManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['name']

	def get_full_name(self):
		"""Retrieve full name of user"""
		return self.name

	def get_short_name(self):
		"""Retrieve shot name of user"""
		return self.name

	def __str__(self):
		"""Return string representation of our user"""
		return self.email


class ProfileFeedItem(models.Model):
	"""Profile status update"""
	user_profile = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE
	)
	status_text = models.CharField(max_length=255)
	created_on = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		"""Return the model as a string"""
		return self.status_text


class Test_One_Off_Fee(models.Model):
	"""Service Fee calculation for Testing purposes"""
	bookdate = models.DateField(blank=True)
	starttime = models.TimeField(blank=True)
	duration = models.IntegerField(default=0)
	owntool = models.BooleanField(default=False)
	ironingclothes = models.BooleanField(default=False)
	urgentbooking = models.BooleanField(default=False)
	servicecode = models.CharField(max_length=64)
	locationdetails = jsonfield.JSONField(blank=True)
	propertydetails = jsonfield.JSONField(blank=True)
	subscription_schedule_details = jsonfield.JSONField(blank=True)
	extra_hours_request = jsonfield.JSONField(blank=True)
	premiumservices = models.BooleanField(default=False)
	foreignlanguage = models.BooleanField(default=False)
	handwashclothes = models.BooleanField(default=False)

	def __str__(self):
		"""Return the model as a string"""
		return self.servicecode


class One_Off_Fee(models.Model):
	"""Service Fee calculation"""
	bookdate = models.DateField(blank=True)
	starttime = models.TimeField(blank=True)
	duration = models.IntegerField(default=0)
	owntool = models.BooleanField(default=False)
	ironingclothes = models.BooleanField(default=False)
	urgentbooking = models.BooleanField(default=False)
	servicecode = models.CharField(max_length=64)
	locationdetails = jsonfield.JSONField(blank=True)
	propertydetails = jsonfield.JSONField(blank=True)
	subscription_schedule_details = jsonfield.JSONField(blank=True)
	extra_hours_request = jsonfield.JSONField(blank=True)
	premiumservices = models.BooleanField(default=False)
	foreignlanguage = models.BooleanField(default=False)

	def __str__(self):
		"""Return the model as a string"""
		return self.servicecode


class Service_Fee_List(models.Model):
	"""Service Fee List Record"""
	from_date = models.DateField(null=True, blank=True)
	to_date = models.DateField(null=True, blank=True)
	fee_list = jsonfield.JSONField()
	active = models.BooleanField(default=False)
	created_on = models.DateTimeField(auto_now_add=True)

	#def __str__(self):
		#"""Return the model as a string"""
		#return str(self.id)
