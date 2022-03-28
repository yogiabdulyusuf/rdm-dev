from odoo import api, fields, models
from datetime import datetime
import logging


_logger = logging.getLogger(__name__)


class rdm_customer(models.Model):    
    _inherit = "rdm.customer"
        
    def get_coupons(self):
        total = 0
        for row in self:
            for datas in row.customer_coupon_ids:
                _logger.info("DATE : " + str(datas.expired_date))
                exp_date = fields.Datetime.from_string(datas.expired_date)
                if datas.state == 'active' and exp_date >= datetime.now():
                    total = total + datas.coupon
            row.coupon = total
            _logger.info('Total Coupon : ' + str(total))

    # coupon = fields.Function(get_coupons, type="integer", string='Coupons')
    coupon = fields.Integer(string="Coupons", compute="get_coupons", required=False, store=False)
    customer_coupon_ids = fields.One2many('rdm.customer.coupon','customer_id','Coupons',readonly=True)