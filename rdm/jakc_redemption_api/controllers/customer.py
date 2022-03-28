import re
import ast
import functools
import logging
import json
from datetime import datetime, date
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.jakc_redemption_api.common import invalid_response, valid_response
import base64
from odoo import http

from odoo.addons.jakc_redemption_api.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)

from odoo.http import request

_logger = logging.getLogger(__name__)


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


class RdmCustomerController(http.Controller):

    @validate_token
    @http.route("/api/rdm/v1.0/customer/detail", type="http", auth="none", methods=["POST"], csrf=False)
    def customerdetail(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        _fields_includes_in_body = all([customer_id])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
            }
            return valid_response(data)

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
            ayc_image_id = row.id
        _logger.info(str(serverUrl))
        model = '/rdm.customer'
        model2 = '/res.company'

        customer = http.request.env['rdm.customer'].sudo().browse(int(customer_id))

        url = 'http://' + serverUrl + '/web/content' + model + '/' + str(customer.id) + '/image'
        url2 = 'http://' + serverUrl + '/web/content' + model2 + '/' + str(ayc_image_id) + '/ayc_image_horizontal'
        url3 = 'http://' + serverUrl + '/web/content' + model2 + '/' + str(ayc_image_id) + '/ayc_image_vertical'
        if customer:
            data = {
                "status": True,
                "message": "",
                "data":
                    {
                        'id': customer.id,
                        'name': customer.name or '',
                        'point': customer.point or 0,
                        'coupon': customer.coupon or 0,
                        'total_amount': int(customer.total_amount) or 0,
                        'image': url or '',
                        'email': customer.email or '',
                        'ayc_number': customer.ayc_number or '',
                        'ayc_image_horizontal': url2 or '',
                        'ayc_image_vertical': url3 or '',
                        'phone_number': customer.mobile_phone1 or '',
                    }

            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Customer not found",
            }
            return valid_response(data)

    @validate_token
    @http.route("/api/rdm/v1.0/customer/update", type="http", auth="none", methods=["POST"], csrf=False)
    def customerupdate(self, **post):

        image = post['image'] or False if 'image' in post else False
        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        email = post['email'] or False if 'email' in post else False
        _fields_includes_in_body = all([customer_id,email])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
            }
            return valid_response(data)

        res_customer_obj = http.request.env['rdm.customer']

        res_customer_ids = res_customer_obj.sudo().search([('id','=',customer_id)], limit=1)

        if image:
            res_customer_ids.write({
                'image': base64.encodestring(image.read()),
                'email': email,
            })
        else:
            res_customer_ids.write({
                'email': email,
            })

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.customer'

        customer = res_customer_obj.sudo().browse(int(customer_id))

        url = 'http://' + serverUrl + '/web/content' + model + '/' + str(customer.id) + '/image'

        if customer:
            data = {
                "status": True,
                "message": "",
                "data":
                    {
                        'id': customer.id,
                        'name': customer.name or '',
                        'image': url or '',
                        'email': customer.email or '',
                        'ayc_number': customer.ayc_number or '',
                        'phone_number': customer.mobile_phone1 or '',
                    }

            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Can not update",
            }
            return valid_response(data)


    @validate_token
    @http.route("/api/rdm/v1.0/customer/transaction", type="http", auth="none", methods=["POST"], csrf=False)
    def customertransaction(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False

        _fields_includes_in_body = all([customer_id])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
            }
            return valid_response(data)

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.reward'

        rewards_trans = []

        domain = [
            ('customer_id', '=', int(customer_id)),
            ('state', '=', 'done'),
        ]
        rdm_reward_trans_ids = http.request.env['rdm.reward.trans'].sudo().search(domain, order="create_date DESC")

        if not rdm_reward_trans_ids:
            data = {
                "status": False,
                "message": "Booking reward not found",
            }
            return valid_response(data)

        for line in rdm_reward_trans_ids:
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
            vals = {}
            vals.update({'id': line.id})
            vals.update({'trans_date': line.trans_date or ''})
            vals.update({'type': line.type or ''})
            vals.update({'point_deduct': line.point or ''})
            vals.update({'is_booking': line.is_booking or ''})
            vals.update({'customer_id': {
                'id': line.customer_id.id or '',
                'name': line.customer_id.name or '',
            }})
            vals.update({'reward_id': {
                'id': line.reward_id.id or '',
                'name': line.reward_id.name or '',
                'image': url or '',
            }})
            vals.update({'booking_expired': line.booking_expired or ''})
            vals.update({'state': line.state or ''})

            rewards_trans.append(vals)

        if rdm_reward_trans_ids:
            data = {
                "status": True,
                "message": "",
                "data": rewards_trans,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Rewards not found",
            }
            return valid_response(data)