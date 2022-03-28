import re
import ast
import functools
import logging
import json
from datetime import datetime, date
import pytz
from dateutil.relativedelta import *
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.jakc_redemption_api.common import invalid_response, valid_response
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo import http

from odoo.addons.jakc_redemption_api.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)

from odoo.http import request

_logger = logging.getLogger(__name__)

expires_in = "jakc_redemption_api.access_token_expires_in"

# import library
import math, random


class RdmOTPController(http.Controller):
    """."""

    def __init__(self):

        self._token = request.env["api.access_token"]
        self._expires_in = request.env.ref(expires_in).sudo().value

    @http.route("/api/rdm/v1.0/resend_otp", type="http", auth="none", methods=["POST"], csrf=False)
    def resendotp(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False

        _fields_includes_in_body = all([
            customer_id,
        ])

        customer_id = int(customer_id)

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
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

        utc_now = pytz.utc.localize(datetime.utcnow())
        date_now = utc_now.astimezone(pytz.timezone("Asia/Jakarta"))

        expired_date_otp = date_now + relativedelta(hours=+1)

        _logger.info(date_now)
        _logger.info(expired_date_otp)

        vals = {}
        vals.update({'rdm_customer_id': customer_id})
        vals.update({'otp_code': OTP})
        vals.update({'expired': expired_date_otp})
        vals.update({'create_date': date_now})
        rdm_customer_otp_obj = http.request.env['rdm.customer.otp'].sudo().create(vals)

        if not rdm_customer_otp_obj:
            data = {
                "status": False,
                "message": "Can not create OTP Code",
            }
            return valid_response(data)

        data = {
            "status": True,
            "message": "Resend OTP Successfully",
        }
        return valid_response(data)


    @http.route("/api/rdm/v1.0/check_otp", type="http", auth="none", methods=["POST"], csrf=False)
    def checkotp(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        code_otp = post['code_otp'] or False if 'code_otp' in post else False

        _fields_includes_in_body = all([
            customer_id,
            code_otp,
        ])

        customer_id = int(customer_id)


        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
            }
            return valid_response(data)

        # domain = [
        #     ('rdm_customer_id','=', int(customer_id)),
        # ]
        #
        # rdm_customer_otp_ids = http.request.env['rdm.customer.otp'].sudo().search(domain, order="create_date DESC", limit=1)
        #
        # if not rdm_customer_otp_ids:
        #     data = {
        #         "status": False,
        #         "message": "Missing fields",
        #         "data": []
        #     }
        #     return valid_response(data)
        #
        # utc_now = pytz.utc.localize(datetime.utcnow())
        # date_now = utc_now.astimezone(pytz.timezone("Asia/Jakarta"))
        #
        # date_now = date_now.strftime("%Y-%m-%d %H:%M:%S")
        # expired_date = rdm_customer_otp_ids.expired.strftime("%Y-%m-%d %H:%M:%S")
        # otp_code = rdm_customer_otp_ids.otp_code
        # _logger.info(date_now)
        # _logger.info(expired_date)
        # _logger.info(otp_code)
        #
        # if expired_date <= date_now:
        #     data = {
        #         "status": False,
        #         "message": "Code OTP Expired",
        #         "data": []
        #     }
        #     return valid_response(data)

        if "1111" != code_otp:  # rdm_customer_otp_ids.otp_code --> dummy OTP 1111
            data = {
                "status": False,
                "message": "Code OTP not Match",
            }
            return valid_response(data)

        # data = {
        #     "status": True,
        #     "message": "OTP Successfully",
        #     "data": []
        # }
        # return valid_response(data)

        # rdm_customer_obj = http.request.env['rdm.customer'].browse(customer_id)
        # rdm_customer_obj.sudo().write({
        #     'state': "active",
        # })

        _token = request.env["api.access_token"]
        # Generate tokens
        access_token = _token.find_one_or_create_token(customer_id=customer_id, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "status": True,
                    "message": "",
                    "data": {
                        "id": customer_id,
                        "access_token": access_token,
                        "expires_in": self._expires_in,
                    }
                }
            ),
        )