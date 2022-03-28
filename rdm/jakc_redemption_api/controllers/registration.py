import re
import ast
import functools
import logging
import json
from datetime import datetime, date
import pytz
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.jakc_redemption_api.common import invalid_response, valid_response
from dateutil.relativedelta import *
from odoo import http

from odoo.addons.jakc_redemption_api.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)

from odoo.http import request

_logger = logging.getLogger(__name__)

# import library
import math, random


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(customer_id=access_token_data.customer_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        # request.session.uid = access_token_data.user_id.id
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class RdmRegistrationController(http.Controller):

    # function to generate OTP
    def generateOTP(self):

        # Declare a digits variable
        # which stores all digits
        digits = "0123456789"
        OTP = ""

        # length of password can be chaged
        # by changing value in range
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]

        return OTP

    @http.route("/api/rdm/v1.0/registration", type="http", auth="none", methods=["POST"], csrf=False)
    def registrationdetail(self, **post):

        phone_number = post['phone_number'] or False if 'phone_number' in post else False
        full_name = post['full_name'] or False if 'full_name' in post else False
        email = post['email'] or False if 'email' in post else False
        password = post['password'] or False if 'password' in post else False
        conf_password = post['conf_password'] or False if 'conf_password' in post else False
        _fields_includes_in_body = all([
            phone_number,
            full_name,
            email,
            password,
            conf_password,
        ])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",

            }
            return valid_response(data)

        email = email.lower()
        full_name = full_name.upper()

        if password != conf_password:
            data = {
                "status": False,
                "message": "Password not match with confirm password",

            }
            return valid_response(data)

        domain = [
            '|', ('mobile_phone1', '=', phone_number), ('email', '=', email), ('state', '=', 'active')
        ]

        rdm_customer_obj = http.request.env['rdm.customer'].sudo().search(domain, limit=1)

        if rdm_customer_obj:
            data = {
                "status": False,
                "message": "Field already exist",

            }
            return valid_response(data)

        # Phone Number
        if phone_number:
            if phone_number[0:2] == "62":
                pass
            elif phone_number[0] == "0":
                phone_number = "62" + phone_number[1:len(phone_number) - 1]
            else:
                data = {
                    "status": False,
                    "message": "Mobile Phone format should be start with 62 or 0",
                }
                return valid_response(data)


        # Declare a digits variable
        # which stores all digits
        digits = "0123456789"
        OTP = ""

        # length of password can be chaged
        # by changing value in range
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]

        rdm_customer_obj = http.request.env['rdm.customer']
        vals = {}
        vals.update({'name': full_name})
        vals.update({'mobile_phone1': phone_number})
        vals.update({'email': email})
        vals.update({'password': password})
        # Save Data
        result = rdm_customer_obj.sudo().create(vals)
        _logger.info(result)

        if not result:
            data = {
                "status": False,
                "message": "Create Failed",

            }
            return valid_response(data)
        result.sudo().write({
            'password': password,
            'state' : "draft",
        })

        utc_now = pytz.utc.localize(datetime.utcnow())
        date_now = utc_now.astimezone(pytz.timezone("Asia/Jakarta"))

        date_now = date_now + relativedelta(hours=+1)
        expired_date_otp = date_now.strftime("%Y-%m-%d %H:%M:%S")

        rdm_customer_otp_obj = http.request.env['rdm.customer.otp']
        val = {}
        val.update({'rdm_customer_id': result.id})
        val.update({'otp_code': OTP})
        val.update({'expired': expired_date_otp})
        result_otp = rdm_customer_otp_obj.sudo().create(val)

        if not result_otp:
            data = {
                "status": False,
                "message": "Create OTP Failed",

            }
            return valid_response(data)

        message_otp = "MTA OTP " + OTP

        data_otp = """
                   <mt_data>
                       <msg_type>txt</msg_type>
                       <username>proM_demo</username>
                       <password>WU66yN3rPV</password>
                       <priority>1</priority>
                       <msisdn_sender>ProMDemo</msisdn_sender>
                       <msisdn>{}</msisdn>
                       <message>{}</message>
                       <dr_url>http://rmd-dev.server007.weha-id.com/api/v1.0/rdm/otp_dr</dr_url>
                   </mt_data>
               """.format(phone_number, message_otp)  # +62 format phone number

        # Prepare Voucher Order Line List
        # customers = result.get_json()

        _logger.info(data_otp)

        data = {
            "status": True,
            "message": "Create OTP successfully",
            "data":
                {
                    'customer_id': result.id,
                    'name': result.name,
                }
        }
        return valid_response(data)