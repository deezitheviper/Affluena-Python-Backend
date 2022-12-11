from __future__ import absolute_import, unicode_literals

from django.utils.encoding import force_text
from rest_framework import serializers
from .restSerializer import AuthTokenSerializer

from deux import strings
from deux.services import verify_mfa_code
from affluena.serializers import MultiFactorChallenge

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError



# Get the UserModel
UserModel = get_user_model()


class MFAAuthTokenSerializer(AuthTokenSerializer):
    """
    class::MFAAuthTokenSerializer()
    This extends the ``AuthTokenSerializer`` to support multifactor
    authentication.
    """

    #: Serializer field for MFA code field.
    mfa_code = serializers.CharField(required=False)

    #: Serializer field for Backup code.
    backup_code = serializers.CharField(required=False)


    def validate(self, attrs):
        attrs = super(MFAAuthTokenSerializer, self).validate(attrs)
        # User must exist if super method didn't throw error.
        user = attrs["user"]
        assert user is not None
        
        mfa = getattr(user, "multi_factor_auth_users", None)

        if mfa and mfa.enabled:
            mfa_code = attrs.get("mfa_code")
            backup_code = attrs.get("backup_code")

            if mfa_code and backup_code:
                raise serializers.ValidationError(
                    force_text(strings.BOTH_CODES_ERROR))
            elif mfa_code:
                bin_key = mfa.get_bin_key(mfa.challenge_type)
                if not verify_mfa_code(bin_key, mfa_code):
                    raise serializers.ValidationError(
                        force_text(strings.INVALID_MFA_CODE_ERROR))
            elif backup_code:
                if not mfa.check_and_use_backup_code(backup_code):
                    raise serializers.ValidationError(
                        force_text(strings.INVALID_BACKUP_CODE_ERROR))
            else:
                challenge = MultiFactorChallenge(mfa, mfa.challenge_type)
                challenge.generate_challenge()
                attrs["mfa_required"] = True
                attrs["mfa_type"] = mfa.challenge_type

        
        if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
                
        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))        
        
        return attrs


        