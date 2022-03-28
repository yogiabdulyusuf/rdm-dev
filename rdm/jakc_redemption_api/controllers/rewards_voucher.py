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


class RdmRewardsVoucherController(http.Controller):



    @validate_token
    @http.route("/api/rdm/v1.0/rewards/voucher/list", type="http", auth="none", methods=["POST"], csrf=False)
    def rewardsvoucherlist(self, **post):

        limit = post['limit'] or False if 'limit' in post else False
        _fields_includes_in_body = all([limit])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)

        if not limit:
            limit = 5
        else:
            limit = int(limit)

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.reward'

        rewards_trans = []

        domain = [
            ('type', '=', 'voucher'),
        ]
        rdm_reward_trans_ids = http.request.env['rdm.reward'].sudo().search(domain, limit=limit, order="create_date DESC")

        for line in rdm_reward_trans_ids:
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
            vals = {}
            vals.update({'id': line.id})
            vals.update({'name': line.name or ''})
            # vals.update({'point': line.point or ''})
            vals.update({'description': line.info or ''})
            # vals.update({'state': line.state or ''})
            vals.update({'image1': str(url) or ''})

            rewards_trans.append(vals)

        if rdm_reward_trans_ids:
            data = {
                "status": True,
                "message": "",
                "data":  rewards_trans,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Rewards not found",

            }
            return valid_response(data)


    # @validate_token
    # @http.route("/api/rdm/v1.0/rewards/voucher/detail", type="http", auth="none", methods=["POST"], csrf=False)
    # def rewardsvoucherdetail(self, **post):
    #
    #     reward_id = post['reward_id'] or False if 'reward_id' in post else False
    #     _fields_includes_in_body = all([reward_id])
    #
    #     if not _fields_includes_in_body:
    #         data = {
    #             "status": False,
    #             "message": "Missing fields",
    #
    #         }
    #         return valid_response(data)
    #
    #     res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
    #     for row in res_company_obj:
    #         serverUrl = row.server_url
    #     _logger.info(str(serverUrl))
    #     model = '/rdm.reward'
    #
    #     # rewards_trans = []
    #
    #     domain = [
    #         ('id', '=', reward_id),
    #         ('type', '=', 'voucher'),
    #     ]
    #     rdm_reward_trans_ids = http.request.env['rdm.reward'].sudo().search(domain, order="create_date DESC")
    #
    #     vals = {}
    #     for line in rdm_reward_trans_ids:
    #         url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
    #
    #         vals.update({'id': line.id})
    #         vals.update({'name': line.name or ''})
    #         # vals.update({'point': line.point or ''})
    #         vals.update({'description': line.info or ''})
    #         # vals.update({'state': line.state or ''})
    #         vals.update({'image1': str(url) or ''})
    #
    #         # rewards_trans.append(vals)
    #
    #     if rdm_reward_trans_ids:
    #         data = {
    #             "status": True,
    #             "message": "",
    #             "data":  vals,
    #         }
    #         return valid_response(data)
    #     else:
    #         data = {
    #             "status": False,
    #             "message": "Rewards not found",
    #
    #         }
    #         return valid_response(data)




