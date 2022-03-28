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


class RdmEventsController(http.Controller):

    @http.route("/api/rdm/v1.0/events/home", type="http", auth="none", methods=["POST"], csrf=False)
    def eventshome(self, **post):

        date_now = datetime.now()

        domain = [
            ('date_start','>=',date_now)
        ]

        rdm_event_ids = http.request.env['rdm.mobile.event'].sudo().search(domain,order='date_start DESC', limit=5)

        events = []

        for line in rdm_event_ids:
            vals = {}
            vals.update({'id': line.id})
            if line.events_owner == 'internal':
                event_owner = "By MTA"
            elif line.events_owner == 'tenant':
                event_owner = "Shop"
            vals.update({'category_name': event_owner or ''})
            vals.update({'name': line.name or ''})
            vals.update({'description': line.description or ''})
            vals.update({'date_start': line.date_start or ''})
            vals.update({'date_end': line.date_end or ''})
            vals.update({'image_file': line.image_file or ''})

            events.append(vals)

        if rdm_event_ids:
            data = {
                "status": True,
                "message": "",
                "data": events,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Events not found",

            }
            return valid_response(data)


    @http.route("/api/rdm/v1.0/events/detail", type="http", auth="none", methods=["POST"], csrf=False)
    def eventsdetail(self, **post):

        event_id = post['event_id'] or False if 'event_id' in post else False
        _fields_includes_in_body = all([event_id])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",

            }
            return valid_response(data)

        domain = [
            ('id','=',int(event_id))
        ]

        rdm_event_ids = http.request.env['rdm.mobile.event'].sudo().search(domain, limit=1)

        # events = []
        vals = {}

        for line in rdm_event_ids:

            vals.update({'id': line.id})
            if line.events_owner == 'internal':
                event_owner = "By MTA"
            elif line.events_owner == 'tenant':
                event_owner = "Shop"
            vals.update({'category_name': event_owner or ''})
            vals.update({'name': line.name or ''})
            vals.update({'description': line.description or ''})
            vals.update({'date_start': line.date_start or ''})
            vals.update({'date_end': line.date_end or ''})
            vals.update({'image_file': line.image_file or ''})

            # events.append(vals)

        if rdm_event_ids:
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

            }
            return valid_response(data)
