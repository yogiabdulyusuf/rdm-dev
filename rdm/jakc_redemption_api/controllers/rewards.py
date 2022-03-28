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


class RdmRewardsController(http.Controller):

    @validate_token
    @http.route("/api/rdm/v1.0/rewards", type="http", auth="none", methods=["POST"], csrf=False)
    def rewards(self, **post):

        limit = post['limit'] or False if 'limit' in post else False
        offset = post['page'] or False if 'page' in post else False
        _fields_includes_in_body = all([limit,offset])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)

        if not limit:
            limit = 5
            offset = 0
        else:
            limit = int(limit)
            offset = int(offset)

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.reward'

        rewards_trans = []

        rdm_reward_trans_ids = http.request.env['rdm.reward'].sudo().search([], offset=offset, limit=limit, order='id DESC')

        for line in rdm_reward_trans_ids:
            vals = {}
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
            vals.update({'id': line.id})
            vals.update({'name': line.name or ''})
            vals.update({'point': line.point or ''})
            vals.update({'description': line.info or ''})
            vals.update({'image1': str(url) or ''})

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

    @validate_token
    @http.route("/api/rdm/v1.0/rewards/home", type="http", auth="none", methods=["POST"], csrf=False)
    def rewardshome(self, **post):

        res_company_obj = http.request.env['res.company'].sudo().search([], limit=1)
        for row in res_company_obj:
            serverUrl = row.server_url
        _logger.info(str(serverUrl))
        model = '/rdm.reward'

        rdm_reward_ids = http.request.env['rdm.reward'].sudo().search([],order='create_date DESC', limit=5)

        rewards = []

        for line in rdm_reward_ids:
            vals = {}
            url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
            vals.update({'id': line.id})
            vals.update({'name': line.name or ''})
            vals.update({'point': line.point or ''})
            vals.update({'description': line.info or ''})
            vals.update({'image1': str(url) or ''})

            rewards.append(vals)

        if rdm_reward_ids:
            data = {
                "status": True,
                "message": "",
                "data": rewards,
            }
            return valid_response(data)
        else:
            data = {
                "status": False,
                "message": "Rewards not found",

            }
            return valid_response(data)


    # @validate_token
    # @http.route("/api/rdm/v1.0/rewards/detail", type="http", auth="none", methods=["POST"], csrf=False)
    # def rewardsdetail(self, **post):
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
    #         ('id', '=', int(reward_id)),
    #     ]
    #     rdm_reward_trans_ids = http.request.env['rdm.reward'].sudo().search(domain, limit=1)
    #
    #     vals = {}
    #     for line in rdm_reward_trans_ids:
    #
    #         url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
    #         vals.update({'id': line.id})
    #         vals.update({'name': line.name or ''})
    #         vals.update({'point': line.point or ''})
    #         vals.update({'description': line.info or ''})
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


    