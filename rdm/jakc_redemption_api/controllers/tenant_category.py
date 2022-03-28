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


class RdmTenantCategoryController(http.Controller):

    @http.route("/api/rdm/v1.0/tenant/category", type="http", auth="none", methods=["POST"], csrf=False)
    def tenantcategory(self, **post):

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.tenant'

        data = []

        tenants_category_ids = http.request.env['rdm.tenant.category'].sudo().search([])

        for line in tenants_category_ids:
            val = {}
            val.update({
                'id': line.id,
                'name': line.name,
            })

            domain = [('category', '=', line.id)]
            rdm_tenant_ids = http.request.env['rdm.tenant'].sudo().search(domain, limit=5)

            # create array
            tenants = []

            for row in rdm_tenant_ids:
                vals = {}
                url = 'http://' + serverUrl + '/web/content' + model + '/' + str(row.id) + '/image'
                vals.update({'id': row.id})
                vals.update({'name': row.name or ''})
                vals.update({'location': row.location or ''})
                vals.update({'floor': row.floor_id.name or ''})
                vals.update({'phone': row.number or ''})
                vals.update({'description': row.about or ''})
                vals.update({'image': url or ''})
                #add array tenants
                tenants.append(vals)
    
            val.update({
                'tenants': tenants,
            })

            data.append(val)

        datas = {
            "status": True,
            "message": "",
            "data": data,
        }
        return valid_response(datas)

    @http.route("/api/rdm/v1.0/tenant/category/detail", type="http", auth="none", methods=["POST"], csrf=False)
    def tenantcategorydetail(self, **post):

        category_id = post['category_id'] or False if 'category_id' in post else False
        _fields_includes_in_body = all([category_id])

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
        model = '/rdm.tenant'

        data = {}

        tenants_category_id = http.request.env['rdm.tenant.category'].sudo().browse(int(category_id))
        data.update({
            'id': tenants_category_id.id,
            'name': tenants_category_id.name,
        })

        domain = [('category', '=', int(category_id))]
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
