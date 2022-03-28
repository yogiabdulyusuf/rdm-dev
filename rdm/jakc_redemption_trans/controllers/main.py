from odoo import http
from odoo.http import request
import werkzeug 
import logging

_logger = logging.getLogger(__name__)


class RedemptionController(http.Controller):

    @http.route('/redemption/topnav/', auth='public')
    def redemption_topnav(self):
        return http.request.render('jakc_redemption_trans.jakc_redemption_trans_top_nav',{})