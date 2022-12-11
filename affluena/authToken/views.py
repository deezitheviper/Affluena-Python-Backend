from __future__ import absolute_import, unicode_literals
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_auth.models import TokenModel
from rest_framework.response import Response
from django.views.decorators.debug import sensitive_post_parameters
from .serializers import MFAAuthTokenSerializer
from django.conf import settings
from django.utils.decorators import method_decorator
from  rest_auth.app_settings import (LoginSerializer,TokenSerializer, JWTSerializer, create_token)
from django.contrib.auth import (
    login as django_login
)
from rest_framework import status
sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password',
    )
)
from django.contrib.auth import (
    login as django_login)
from django.contrib.auth import authenticate

class ObtainMFAAuthToken(ObtainAuthToken):
    serializer_class = MFAAuthTokenSerializer
    token_model = TokenModel


    def post(self, request, *args, **kwargs):
       
        
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if "mfa_required" in data and data["mfa_required"]:
              user = serializer.validated_data['user']
              token, created = Token.objects.get_or_create(user=user)
              return Response({
                "mfa_required": True,
                "mfa_type": serializer.validated_data["mfa_type"],
                "token": token.key
            })
        else:
            user = serializer.validated_data['user']
            email = user.email
            phone = user.phone
            token, created = Token.objects.get_or_create(user=user)
            django_login(request, user)
            return Response({"token": token.key, 'email':email, 'phone':phone})