from allauth.account import app_settings as allauth_settings
from allauth.account.models import EmailAddress
from allauth.utils import (email_address_exists,
                            get_username_max_length)
from allauth.account.utils import setup_user_email
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.encoding import force_text
from rest_framework.views import exception_handler
from django.db import IntegrityError
import re
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers,exceptions
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer
from .models import *
from allauth.account.adapter import get_adapter
from rest_framework.authtoken.models import Token
from .models import User as MaxUser
from datetime import datetime
from allauth.account.views import SignupView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from .models import Profile
from django.contrib.auth.validators import ASCIIUsernameValidator
from .constants import CHALLENGE_TYPES,EMAIL
from deux import strings
from deux.serializers import _BaseChallengeRequestSerializer,_BaseChallengeVerifySerializer
from deux.constants import SMS
from deux.exceptions import FailedChallengeError
import six
from deux.services import MultiFactorChallenge,generate_mfa_code, verify_mfa_code
from deux.app_settings import mfa_settings
from django.core.mail import send_mail
from rest_framework.response import Response
from deux.authtoken.serializers import MFAAuthTokenSerializer
import requests
from decouple import config



def send_phone(code, phone):
    url = "https://api.80kobosms.com/v2/app/sendsms"
    access_token = config('sms_access_token')
    message = "Your Authentication Code: {}".format(code)
    
    PARAMS = {'message':message,'sender_name':"Affluena",'recipients':phone}
    r = requests.post(url,
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)}, params=PARAMS)
    

def send_mfa_code_email_message(mfa_instance, mfa_code):
        c = mfa_instance
        email = c.user.email
        phone = c.user.phone
        code = mfa_code 
        #send_phone(code, phone)
        message = "Two Factor Authentication code: {0} ".format(code)
        send_mail('Two Factor Authentication code', message, settings.DEFAULT_FROM_EMAIL, [email])
        


class MultiFactorChallenge(object):
    def __init__(self, instance, challenge_type):
        assert challenge_type in CHALLENGE_TYPES, (
            "Inputted challenge type is not supported."
        )
        self.instance = instance
        self.challenge_type = challenge_type

    def generate_challenge(self):
        dispatch = {
            SMS: self._sms_challenge,
            EMAIL: self._email_challenge
        } 
        for challenge in CHALLENGE_TYPES:
            assert challenge in dispatch, (
                "'{challenge}' does not have a challenge dispatch "
                "method.".format(challenge=challenge)
            )
        return dispatch[self.challenge_type]()
    
    def _sms_challenge(self):
        """Executes the SMS challenge."""
        code = generate_mfa_code(bin_key=self.instance.sms_bin_key)
        mfa_settings.SEND_MFA_TEXT_FUNC(
            mfa_instance=self.instance, mfa_code=code)


    
    
    def _email_challenge(self):
        
        code = generate_mfa_code(bin_key=self.instance.email_bin_key,drift=1)
        send_mfa_code_email_message(mfa_instance=self.instance, mfa_code=code)


class Contact(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    company = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    message = serializers.CharField()


class PhoneVerify(serializers.Serializer):
    phonecode = serializers.CharField()
    bin_key = serializers.CharField()

class Phone(serializers.Serializer):
    phone = serializers.CharField()

class OTPCODE(serializers.Serializer):
    code = serializers.CharField()
    user = serializers.CharField()

class NewBaseChallengeRequestSerializer(_BaseChallengeRequestSerializer):
    challenge_type = EMAIL

    def execute_challenge(self, instance):
        """
        Execute challenge for this instance based on the ``challenge_type``.
        :param instance: :class:`MultiFactorAuth` instance to use.
        :raises serializers.ValidationError: If the challenge fails to execute.
        """
        try:
            MultiFactorChallenge(
                instance, self.challenge_type).generate_challenge()
    
        except FailedChallengeError as e:
            raise serializers.ValidationError({
                "detail": six.text_type(e)
            })




class EmailChallengeRequestSerializer(NewBaseChallengeRequestSerializer):
    """
    class::EmailChallengeRequestSerializer()
    Serializer that facilitates a request to enable MFA over Email.
    """

    #: This serializer represents the ``SMS`` challenge type.
    challenge_type = EMAIL
    

    def update(self, mfa_instance, validated_data):
        """
        If the request data is valid, the serializer executes the challenge
        by calling the super method and also saves the phone number the user
        requested the SMS to.
        :param mfa_instance: :class:`MultiFactorAuth` instance to use.
        :param validated_data: Data returned by ``validate``.
        """
        
        mfa_instance.email = validated_data["email"]
        
        super(EmailChallengeRequestSerializer, self).update(
            mfa_instance, validated_data)
        mfa_instance.save()

        return mfa_instance

    class Meta(NewBaseChallengeRequestSerializer.Meta):
        fields = ("email",)
        extra_kwargs = {
            "email": {
                "required": True,
            },
        }


class EmailChallengeVerifySerializer(_BaseChallengeVerifySerializer):
    """
    class::EmailChallengeVerifySerializer()
    Extension of ``_BaseChallengeVerifySerializer`` that implements
    challenge verification for the SMS challenge.
    """
    #: This serializer represents the ``SMS`` challenge type.
    challenge_type = EMAIL
    def validate(self, internal_data):
        """
        Validates the request to verify the MFA code. It first ensures that
        MFA is not already enabled and then verifies that the MFA code is the
        correct code.
        :param internal_data: Dictionary of the request data.
        :raises serializers.ValidationError: If MFA is already enabled or if
            the inputted MFA code is not valid.
        """
        if self.instance.enabled:
            pass

        mfa_code = internal_data.get("mfa_code")
        bin_key = self.instance.get_bin_key(self.challenge_type)
        if not verify_mfa_code(bin_key, mfa_code):
            raise serializers.ValidationError({
                "mfa_code": strings.INVALID_MFA_CODE_ERROR
            })
        return {"mfa_code": mfa_code}

    
class Login(LoginSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise CustomValidation(
                    'User account is disabled.',"error",status_code=status.HTTP_200_OK)

        else:
            msg = _('Unable to log in with provided credentials.')
            raise CustomValidation(
                   'Unable to log in with provided credentials.',"error",status_code=status.HTTP_200_OK)


        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                try:
                    email_address = user.emailaddress_set.get(email=user.email)
                except ObjectDoesNotExist:
                    raise CustomValidation('E-mail does not exit',"error",status_code=status.HTTP_200_OK)
                if not email_address.verified:
                    raise CustomValidation('E-mail is not verified.',"error",status_code=status.HTTP_200_OK)

        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}


    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        if not get_user_model().objects.filter(email=value).exists():
            raise CustomValidation('Account not found',"error",status_code=status.HTTP_200_OK)
        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'        

class CustomValidation(APIException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        default_detail = 'A server error occurred.'

        def __init__(self, detail, field, status_code):
            if status_code is not None:self.status_code = status_code
            if detail is not None:
                self.detail = {field: force_text(detail)}
            else: self.detail = {'error': force_text(self.default_detail)}



class UpdateUserSerializer(serializers.ModelSerializer):

    is_verified = serializers.SerializerMethodField()
    def get_is_verified(self, user):    
        return (user.emailaddress_set.filter().exists())

    class Meta:
        model = User
        fields = ('email','phone','full_name','address','city','state','profile_pic','signature','bank_name','account_no','account_name','is_verified') 

    def update(self, instance, validated_data):
        new_email = validated_data.pop('email', None)
        user = super(UpdateUserSerializer, self).update(instance, validated_data)

       
        if new_email:
            context = self.context
            request = context.get('request', None)
            if request:
                EmailAddress.objects.add_email(request, user, new_email, confirm=True)

        return user

class SignupSerializer(RegisterSerializer):
    full_name = serializers.CharField(max_length=300,required=False)
    code = serializers.CharField(max_length=200,required=False)
    
    def get_cleaned_data(self):
        return {
            'full_name': self.validated_data.get('full_name',''),
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
            'phone': self.validated_data.get('phone', ''),
            'code': self.validated_data.get('code', ''),
        }


    def validate_username(self, value):
        existing = User.objects.filter(username__iexact=value)
        if existing.exists():
            raise CustomValidation(
                    "A user is already registered with this username.","error",status_code=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise CustomValidation(
                    "username may contain only letters, numbers.","error",status_code=status.HTTP_400_BAD_REQUEST)
        return value
        

    def validate_phone(self, phone):
        existing = User.objects.filter(phone__iexact=phone)
        if existing.exists():
            raise CustomValidation(
                    "A user is already registered with this phone.","error",status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return phone  

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise CustomValidation(
                    "A user is already registered with this e-mail address.","error",status_code=status.HTTP_400_BAD_REQUEST)
        return email

    def save(self, request):
    
        adapter = get_adapter()
        user = adapter.new_user(request) 
        self.cleaned_data = self.get_cleaned_data()  
        code = self.data.get('code')
        if code is not None:
            user.link_code = self.data.get('code') 
        user.is_super = False
        user.full_name = self.data.get('name')
        user.state = self.data.get('state')
        user.city = self.data.get('city')
        user.phone = self.data.get('phone')
  
        try:
            adapter.save_user(request, user, self)
        except IntegrityError as e: 
            pass
        return user
        



class TokenSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()
   
    
    class Meta:
        model= Token 
        fields = ('key','user','user_detail')

    def get_user_detail(self, obj):
        serializer_data = UserSerializer(obj.user).data
        usern =  serializer_data.get('username')
        user = User.objects.get(username=usern)
        if user.profile.referredBy is not None:
            reff = user.profile.referredBy
            referral = reff.username
        else:
            referral = ""
        is_staff = serializer_data.get('is_staff')
        username = serializer_data.get('username')
        email = serializer_data.get('email')
        email_verified = serializer_data.get('email_verified')
        compounding = serializer_data.get('compounding')
        withdrawn = serializer_data.get('totalWithdrawn')
        time = serializer_data.get('date_joined')
        date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B')
        balance = serializer_data.get('account_balance')
        last = serializer_data.get('last_login')
        last_login = datetime.strptime(last, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%I:%M%p on %d %B %Y')
        activeA = serializer_data.get('active_affiliates')
        activeP = serializer_data.get('active_package')
        full_name = serializer_data.get('full_name')
        country = serializer_data.get('country')
        address = serializer_data.get('address')
        city = serializer_data.get('city')
            
            
        return{

            'is_staff': is_staff,
            'email': email,
            'username': username,
            'monthjoined': date,
            'balance': balance,
            'last_login': last_login,
            'compounding':compounding,
            "referral": referral,
            "last_login": last_login,
            "activeA": activeA,
            "activeP": activeP,
            "full_name": full_name,
            "country": country,
            "address": address,
            "city": city,
            "email_verified": email_verified,
            "withdrawn": withdrawn
            
        }
