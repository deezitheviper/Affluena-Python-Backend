from deux.abstract_models import AbstractMultiFactorAuth 
from django.db import models
from .constants import EMAIL, CHALLENGE_TYPES, DISABLED, SMS
from binascii import unhexlify
from deux.services import generate_key
from .models import User
from django.core.validators import RegexValidator

class CustomDeux(AbstractMultiFactorAuth):
    
    CHALLENGE_CHOICES = (
        (SMS, "SMS"),
        (EMAIL, "EMAIL"), 
        (DISABLED, "Off"),
    )
    phone_regex = RegexValidator( regex   =r'^\+?1?\d{9,14}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone_num = models.CharField(validators=[phone_regex], max_length=17, unique=True,blank=True, null=True)
    email = models.EmailField()
    user = models.OneToOneField(
            User, on_delete=models.CASCADE,
        related_name="multi_factor_auth_users", primary_key=True
    )
    @property
    def email_bin_key(self):
        """Returns binary data of the SMS secret key.""" 
        return unhexlify(self.sms_secret_key)

    @property
    def enabled(self):
        """Returns if MFA is enabled."""
        return self.challenge_type in CHALLENGE_TYPES

    def get_bin_key(self, challenge_type):
        """
        Returns the key associated with the inputted challenge type.
        :param challenge_type: The challenge type the key is requested for.
                               The type must be in the supported
                               `CHALLENGE_TYPES`.
        :raises AssertionError: If ``challenge_type`` is not a supported
                                challenge type.
        """
        assert challenge_type in CHALLENGE_TYPES, (
            "'{challenge}' is not a valid challenge type.".format(
                challenge=challenge_type)
        )
        return {
            SMS: self.sms_bin_key,
            EMAIL: self.email_bin_key
        }.get(challenge_type, None)

    def enable(self, challenge_type):
        """
        Enables MFA for this user with the inputted challenge type.
        The enabling process includes setting this objects challenge type and
        generating a new backup key.
        :param challenge_type: Enable MFA for this type of challenge. The type
                               must be in the supported `CHALLENGE_TYPES`.
        :raises AssertionError: If ``challenge_type`` is not a supported
                                challenge type.
        """
        assert challenge_type in CHALLENGE_TYPES, (
            "'{challenge}' is not a valid challenge type.".format(
                challenge=challenge_type)
        )
        self.challenge_type = challenge_type
        self.backup_key = generate_key()
        self.save()