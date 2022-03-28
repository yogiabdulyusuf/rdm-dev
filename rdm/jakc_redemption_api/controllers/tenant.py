import re
import ast
import functools
import logging
import json
from datetime import datetime, date
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.jakc_redemption_api.common import invalid_response, valid_response
import random

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


class RdmTenantController(http.Controller):

    @http.route("/api/rdm/v1.0/tenant/category/home", type="http", auth="none", methods=["POST"], csrf=False)
    def tenantcategoryhome(self, **post):

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.tenant'

        tenants_category = []

        tenants_category_obj = http.request.env['rdm.tenant.category'].sudo().search([])

        for line in tenants_category_obj:
            tenants_category.append(line.id)

        if not tenants_category_obj:
            data = {
                "status": False,
                "message": "Tenant category not found",

            }
            return valid_response(data)

        data = {}

        randoom_id = random.choice(tenants_category)
        tenants_category_id = http.request.env['rdm.tenant.category'].sudo().browse(randoom_id)
        data.update({
            'id': tenants_category_id.id,
            'name': tenants_category_id.name,
        })

        domain = [('category', '=', randoom_id)]
        rdm_tenant_ids = http.request.env['rdm.tenant'].sudo().search(domain, limit=5)

        tenants = []

        for line in rdm_tenant_ids:
            vals = {}
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image'
            vals.update({'id': line.id})
            vals.update({'name': line.name or ''})
            vals.update({'location': line.location or ''})
            vals.update({'floor': line.floor_id.name or ''})
            vals.update({'phone': line.number or ''})
            vals.update({'description': line.about or ''})
            vals.update({'image': url or ''})
            tenants.append(vals)
   
        data.update({
            'tenants': tenants,
        })

        datas = {
            "status": True,
            "message": "",
            "data": data,
        }
        return valid_response(datas)
       
    @http.route("/api/rdm/v1.0/tenant/detail", type="http", auth="none", methods=["POST"], csrf=False)
    def tenantdetail(self, **post):

        tenant_id = post['tenant_id'] or False if 'tenant_id' in post else False
        _fields_includes_in_body = all([tenant_id])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Tenant ID not found",

            }
            return valid_response(data)

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.tenant'
        model2 = '/rdm.building.floor'

        domain = [('id', '=', int(tenant_id))]
        rdm_tenant_ids = http.request.env['rdm.tenant'].sudo().search(domain,)

        # tenants = []
        vals = {}
        for line in rdm_tenant_ids:
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image'
            url2 = 'http://' + serverUrl + '/web/content' + model2 + '/' + str(line.floor_id.id) + '/image'
            vals.update({'id': line.id})
            vals.update({'name': line.name or ''})
            vals.update({'location': line.location or ''})
            vals.update({'floor': line.floor_id.name or ''})
            vals.update({'maps_image': url2 or ''})
            vals.update({'phone': line.number or ''})
            vals.update({'description': line.about or ''})
            vals.update({'image': url or ''})
            # tenants.append(vals)

        if rdm_tenant_ids:
            data = {
                "status": True,
                "message": "",
                "data": vals,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Tenant not found",
            }
        return valid_response(data)


