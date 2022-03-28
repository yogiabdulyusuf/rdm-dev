from odoo import api, fields, models

import logging


_logger = logging.getLogger(__name__)


class rdm_customer_otp(models.Model):
    _name = 'rdm.customer.otp'
    _description = 'OTP Customer'

    rdm_customer_id = fields.Many2one(comodel_name="rdm.customer", string="Customer ID", required=False, )
    otp_code = fields.Char(string="OTP", size=4)
    expired = fields.Datetime(string="Expired", required=False, )


