from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from .models import User

class CustomerBackend(ModelBackend):
	def authenticate(self, request, **kwargs):
		email = None
		username = None
		user = None
		try:
			email = kwargs['email']
		except KeyError:
			username = kwargs['username']	
		password = kwargs['password']
		try:
			if email:
				user = User.objects.get(email=email)
			elif username :
				user = User.objects.get(username=username)
			if user.check_password(password) is True:
				return user
		except User.DoesNotExist:
			return None
    
	