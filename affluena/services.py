from __future__ import absolute_import, unicode_literals

import six
from uuid import uuid4

from django.utils.crypto import constant_time_compare
from django_otp.oath import totp

from deux.app_settings import mfa_settings
from deux.constants import CHALLENGE_TYPES, SMS


def generate_mfa_code(bin_key, drift=0):
   
    return six.text_type(totp(
        bin_key,
        step=500,
        digits=6,
        drift=drift
    )).zfill(6)


def generate_key():
    
    return uuid4().hex


def verify_mfa_code(bin_key, mfa_code):
    if not mfa_code:
        return False
    try:
        mfa_code = int(mfa_code)
    except ValueError:
        return False
    else:
        totp_check = lambda drift: int(
            generate_mfa_code(bin_key=bin_key, drift=drift))
        return any(
            constant_time_compare(totp_check(drift), mfa_code)
            for drift in [-1, 0, 1]
        )

