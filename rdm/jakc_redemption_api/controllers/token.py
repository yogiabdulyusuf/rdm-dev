# Part of odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

import werkzeug.wrappers
from datetime import datetime, date
import pytz
from dateutil.relativedelta import *
# import library
import math, random
from odoo import http
from odoo.addons.jakc_redemption_api.common import invalid_response, valid_response
from odoo.http import request
from odoo.exceptions import AccessError, AccessDenied

_logger = logging.getLogger(__name__)

expires_in = "jakc_redemption_api.access_token_expires_in"


class AccessToken(http.Controller):
    """."""

    def __init__(self):

        self._token = request.env["api.access_token"]
        self._expires_in = request.env.ref(expires_in).sudo().value

    @http.route("/api/rdm/v1.0/auth/token", methods=["GET"], type="http", auth="none", csrf=False)
    def token(self, **post):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.
        Returns:

            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests

           headers = {'content-type': 'text/plain', 'charset':'utf-8'}

           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           eq = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))
        """
        _token = request.env["api.access_token"]
        params = ["login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        username, password = (
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return werkzeug.wrappers.Response(
                    status=200,
                    content_type="application/json; charset=utf-8",
                    headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
                    response=json.dumps(
                        {
                            "status": False,
                            "message": "either of the following are missing [username,password]",
                            # "access_token": access_token,
                            # "expires_in": self._expires_in,

                        }
                    ),
                )

        domain = [
            ('mobile_phone1', '=', str(username)),
            ('password', '=', password),
            ('state','=','active')
        ]

        # Login in odoo database:
        customer_id = request.env['rdm.customer'].sudo().search(domain,limit=1)

        # odoo login failed:
        if not customer_id.id:
            return werkzeug.wrappers.Response(
                status=200,
                content_type="application/json; charset=utf-8",
                headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
                response=json.dumps(
                    {
                        "status": False,
                        "message": "authentication failed",
                        # "access_token": access_token,
                        # "expires_in": self._expires_in,

                    }
                ),
            )


        # Declare a digits variable
        # which stores all digits
        digits = "0123456789"
        OTP = ""

        # length of password can be chaged
        # by changing value in range
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]

        # Timezone in Asia/Jakarta
        utc_now = pytz.utc.localize(datetime.utcnow())
        date_now = utc_now.astimezone(pytz.timezone("Asia/Jakarta"))

        date_now = date_now + relativedelta(hours=+1)
        expired_date_otp = date_now.strftime("%Y-%m-%d %H:%M:%S")

        # Create OTP
        rdm_customer_otp_obj = http.request.env['rdm.customer.otp']
        val = {}
        val.update({'rdm_customer_id': customer_id.id})
        val.update({'otp_code': OTP})
        val.update({'expired': expired_date_otp})
        result_otp = rdm_customer_otp_obj.sudo().create(val)

        if result_otp:
            otp = "Create OTP successfully"
            status = True
        else:
            otp = "Can not create OTP"
            status = False

        # # Generate tokens
        # access_token = _token.find_one_or_create_token(customer_id=customer_id.id,  create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "status": status,
                    "message": otp,
                    # "access_token": access_token,
                    # "expires_in": self._expires_in,
                    "data": {
                        'customer_id': customer_id.id,
                        'name': customer_id.name,
                    }
                }
            ),
        )

    @http.route("/api/rdm/v1.0/auth/token", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete(self, **post):
        """."""
        _token = request.env["api.access_token"]
        access_token = request.httprequest.headers.get("access_token")
        access_token = _token.search([("token", "=", access_token)])
        if not access_token:
            # info = "No access token was provided in request!"
            # error = "Access token is missing in the request header"
            # _logger.error(info)
            data = {
                "status": False,
                "message": "Access token is missing in the request header",

            }
            return invalid_response(data)
        for token in access_token:
            token.unlink()
        # Successful response:
        data = {
            "status": True,
            "message": "access token successfully deleted",
        }
        return valid_response(data)
