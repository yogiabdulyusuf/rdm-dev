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


class RdmNotification(http.Controller):

    @validate_token
    @http.route("/api/rdm/v1.0/notif/list", type="http", auth="none", methods=["POST"], csrf=False)
    def customernotiflist(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        _fields_includes_in_body = all([customer_id])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)

        domain = [
            ('rdm_customer_id','=', int(customer_id))
        ]

        rdm_customer_notif_ids = http.request.env['rdm.customer.notif'].sudo().search(domain, order='create_date DESC')

        notif = []

        for row in rdm_customer_notif_ids:
            vals = {}
            vals.update({'id': row.id})
            vals.update({'type': row.type or ''})
            vals.update({'subject': row.subject or ''})
            vals.update({'date': row.date or ''})
            vals.update({'detail': row.detail or ''})
            vals.update({'status': row.state or ''})
            notif.append(vals)

        if rdm_customer_notif_ids:
            data = {
                "status": True,
                "message": "",
                "data": notif,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Events not found",
                "data": [
                ]
            }
            return valid_response(data)


    @validate_token
    @http.route("/api/rdm/v1.0/notif/read", type="http", auth="none", methods=["POST"], csrf=False)
    def customernotifread(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        notif_id = post['notif_id'] or False if 'notif_id' in post else False
        _fields_includes_in_body = all([customer_id,notif_id])

        domain = [
            ('rdm_customer_id', '=', int(customer_id)),
            ('notif_id', '=', int(notif_id)),
        ]

        rdm_customer_notif_ids = http.request.env['rdm.customer.notif'].sudo().search(domain, )

        rec = rdm_customer_notif_ids.write({
            'state': 'read',
        })

        if not rec:
            data = {
                "status": False,
                "message": "Can read notification",
                "data": []
            }
            return valid_response(data)
        else:
            data = {
                "status": True,
                "message": "Read Notif successfully",
                "data": []
            }
            return valid_response(data)




    @validate_token
    @http.route("/api/rdm/v1.0/notif/detail", type="http", auth="none", methods=["POST"], csrf=False)
    def customernotifdetail(self, **post):

        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        notif_id = post['notif_id'] or False if 'notif_id' in post else False
        _fields_includes_in_body = all([customer_id, notif_id])

        domain = [
            ('rdm_customer_id', '=', int(customer_id)),
            ('notif_id', '=', int(notif_id)),
        ]

        rdm_customer_notif_ids = http.request.env['rdm.customer.notif'].sudo().search(domain, )

        # notif = []
        vals = {}
        for row in rdm_customer_notif_ids:
            vals.update({'id': row.id})
            vals.update({'type': row.type or ''})
            vals.update({'subject': row.subject or ''})
            vals.update({'date': row.date or ''})
            vals.update({'detail': row.detail or ''})
            # notif.append(vals)

        if rdm_customer_notif_ids:
            data = {
                "status": True,
                "message": "",
                "data": vals,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Events not found",
                "data": [
                ]
            }
            return valid_response(data)