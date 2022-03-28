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


class RdmRewardsBookingController(http.Controller):

    @validate_token
    @http.route("/api/rdm/v1.0/rewards/booking", type="http", auth="none", methods=["POST"], csrf=False)
    def rewardsbooking(self, **post):

        reward_id = post['reward_id'] or False if 'reward_id' in post else False
        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        _fields_includes_in_body = all([reward_id,customer_id])

        if not _fields_includes_in_body:
            data = {
                "status": False,
                "message": "Missing fields",

            }
            return valid_response(data)

        customer_id = int(customer_id)
        reward_id = int(reward_id)

        # reward_stock = self.check_reward_stock(self.reward_id.id)
        reward_stock = http.request.env['rdm.reward.trans'].sudo().check_reward_stock(reward_id)
        _logger.info("Reward Stock API : " + str(reward_stock))
        if reward_stock == False:
            data = {
                "status": False,
                "message": "Reward has no stock",

            }
            return valid_response(data)

        # check_reward_limit_count  = self.check_reward_limit_count(self.customer_id.id, self.reward_id.id)
        check_reward_limit_count = http.request.env['rdm.reward.trans'].sudo().check_reward_limit_count(customer_id, reward_id)
        if check_reward_limit_count == False:
            data = {
                "status": False,
                "message": "Reward Limit Count Applied",

            }
            return valid_response(data)

        # allow_redeem_reward = self.allow_redeem_reward(self.customer_id.id, self.reward_id.id)
        allow_redeem_reward = http.request.env['rdm.reward.trans'].sudo().allow_redeem_reward(customer_id, reward_id)
        if allow_redeem_reward == False:
            data = {
                "status": False,
                "message": "Redeem Limit Applied",

            }
            return valid_response(data)

        customer_ids = http.request.env['rdm.customer'].sudo().browse(customer_id)
        reward = http.request.env['rdm.reward'].sudo().browse(reward_id)

        vals = {}

        # if reward.type == 'promo':
        #     vals.update({'state': 'done'})
        # elif reward.type == 'reward':
        if customer_ids.point < reward.point:
            data = {
                "status": False,
                "message": "Point not enough",

            }
            return valid_response(data)
        else:
            vals.update({'point': reward.point})
            vals.update({'state': 'open'})

        vals.update({'customer_id': customer_ids.id})
        vals.update({'reward_id': reward.id})
        vals.update({'is_booking': True})
        rdm_reward_trans_ids = http.request.env['rdm.reward.trans'].sudo().create(vals)

        # if rdm_reward_trans_ids.is_booking == True:
        #     point = rdm_reward_trans_ids.point
        #     self.env['rdm.customer.point'].deduct_point(trans_id_id, customer_id, point)
        #     self._send_booking_notitication_to_customer()

        if not rdm_reward_trans_ids:
            data = {
                "status": False,
                "message": "Can not booking reward",

            }
            return valid_response(data)

        if rdm_reward_trans_ids:
            data = {
                "status": True,
                "message": "Create booking successfully",
            }
            return valid_response(data)



    @validate_token
    @http.route("/api/rdm/v1.0/rewards/booking/list", type="http", auth="none", methods=["POST"], csrf=False)
    def rewardsbookinglist(self, **post):


        customer_id = post['customer_id'] or False if 'customer_id' in post else False
        limit = post['limit'] or False if 'limit' in post else False
        _fields_includes_in_body = all([limit, customer_id])

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
            ('customer_id', '=', int(customer_id)),
            ('is_booking', '=', True),
        ]
        rdm_reward_trans_ids = http.request.env['rdm.reward.trans'].sudo().search(domain, limit=limit, order="create_date DESC")

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
            vals.update({'name': line.reward_id.name or ''})
            # vals.update({'trans_date': line.trans_date or ''})
            # vals.update({'type': line.type or ''})
            vals.update({'point': line.point or ''})
            # vals.update({'is_booking': line.is_booking or ''})
            # vals.update({'customer_id': {
            #     'id' : line.customer_id.id or '',
            #     'name' : line.customer_id.name or '',
            # }})
            # vals.update({'reward_id': {
            #     'id' : line.reward_id.id or '',
            #     'name' : line.reward_id.name or '',
            #     'image': url or '',
            # }})
            # vals.update({'booking_expired': line.booking_expired or ''})
            vals.update({'description': line.reward_id.info or ''})
            vals.update({'image': url or ''})
            # vals.update({'state': line.state or ''})

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
    # @http.route("/api/rdm/v1.0/rewards/booking/detail", type="http", auth="none", methods=["POST"], csrf=False)
    # def rewardsbookingdetail(self, **post):
    #
    #     trans_reward_id = post['trans_reward_id'] or False if 'trans_reward_id' in post else False
    #     customer_id = post['customer_id'] or False if 'customer_id' in post else False
    #     _fields_includes_in_body = all([trans_reward_id, customer_id])
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
    #         ('id', '=', int(trans_reward_id)),
    #         ('customer_id', '=', int(customer_id)),
    #         ('is_booking', '=', True),
    #     ]
    #     rdm_reward_trans_ids = http.request.env['rdm.reward.trans'].sudo().search(domain, order="create_date DESC")
    #
    #     vals = {}
    #     for line in rdm_reward_trans_ids:
    #         url = 'http://' + serverUrl + '/web/content' + model + '/' + str(line.id) + '/image1'
    #         vals.update({'id': line.id})
    #         vals.update({'name': line.reward_id.name or ''})
    #         # vals.update({'trans_date': line.trans_date or ''})
    #         vals.update({'type': line.type or ''})
    #         vals.update({'point_deduct': line.point or ''})
    #         # vals.update({'is_booking': line.is_booking or ''})
    #         # vals.update({'customer_id': {
    #         #     'id' : line.customer_id.id or '',
    #         #     'name' : line.customer_id.name or '',
    #         # }})
    #         # vals.update({'reward_id': {
    #         #     'id' : line.reward_id.id or '',
    #         #     'name' : line.reward_id.name or '',
    #         #     'image' : url,
    #         # }})
    #         vals.update({'booking_expired': line.booking_expired or ''})
    #         vals.update({'description': line.reward_id.info or ''})
    #         vals.update({'image': url or ''})
    #         # vals.update({'state': line.state or ''})
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

