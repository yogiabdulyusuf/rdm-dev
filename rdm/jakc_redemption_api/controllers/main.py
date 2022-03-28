import re
import ast
import functools
import logging
import json
from datetime import datetime, date
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.jakc_redemption_api.common import invalid_response, valid_response

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

        #request.session.uid = access_token_data.user_id.id
        #request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class RdmCustomerController(http.Controller):
    
    @validate_token
    @http.route("/api/rdm/v1.0/customer", type="http", auth="none", methods=["POST"], csrf=False)
    def customerdetail(self, **post):
        
        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        _fields_includes_in_body = all([customer_id])

        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)
        
  
        customer = http.request.env['rdm.customer'].sudo().browse(int(customer_id))
        if customer:
            data = {
                "err": False,
                "message": "",
                "data": [ 
                    {
                        'name': customer.name,
                        'point': customer.point,
                        'coupon': customer.coupon,
                        'total_amount': customer.total_amount,
                    }
                ]
            }
            return valid_response(data)
        else:
            data = {
                "err": True,
                "message": "Customer not found",
                "data": [ 
                ]
            }
            return valid_response(data)

    @validate_token
    @http.route("/api/rdm/v1.0/tenant", type="http", auth="none", methods=["POST"], csrf=False)
    def tenantdetail(self, **post):

        # customer_id = post['customer_id'] or False if 'customer_id' in post else False
        # _fields_includes_in_body = all([customer_id])
        #
        # if not _fields_includes_in_body:
        #     data = {
        #         "err": True,
        #         "message": "Missing fields",
        #         "data": []
        #     }
        #     return valid_response(data)

        # customer = http.request.env['rdm.customer'].sudo().browse(int(customer_id))
        rdm_tenant_ids = http.request.env['rdm.tenant'].sudo().search([], limit=20)

        tenants = []

        for line in rdm_tenant_ids:
            vals = {}
            vals.update({'name': line.name})

            tenants.append(vals)

        if rdm_tenant_ids:
            data = {
                "err": False,
                "message": "",
                "data": tenants,
            }
            return valid_response(data)
        else:
            data = {
                "err": True,
                "message": "Customer not found",

            }
            return valid_response(data)


