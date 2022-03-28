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

        # request.session.uid = access_token_data.user_id.id
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class RdmBannerController(http.Controller):

    @http.route("/api/rdm/v1.0/banner/home", type="http", auth="none", methods=["POST"], csrf=False)
    def banners(self, **post):

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.mobile.banner'

        date_now = datetime.now()

        domain = [
            ('date_start','<=',date_now)
        ]

        rdm_banner_ids = http.request.env['rdm.mobile.banner'].sudo().search(domain,order='date_start DESC', limit=5)

        banners = []

        for line in rdm_banner_ids:
            vals = {}
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image_file'
            vals.update({'id': line.id})
            vals.update({'name': line.name or ''})
            vals.update({'description': line.description or ''})
            vals.update({'date_start': line.date_start or ''})
            vals.update({'date_end': line.date_end or ''})
            vals.update({'image': url or ''})
            vals.update({'link': line.link or ''})

            banners.append(vals)

        if rdm_banner_ids:
            data = {
                "status": True,
                "message": "",
                "data": banners,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Banner not found",
            }
            return valid_response(data)


