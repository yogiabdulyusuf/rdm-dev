from odoo import api, fields, models

import logging


_logger = logging.getLogger(__name__)


class rdm_customer_notif(models.Model):
    _name = 'rdm.customer.notif'
    _rec_name = 'subject'
    _description = 'Notif Customer'

    rdm_customer_id = fields.Many2one(comodel_name="rdm.customer", string="Customer ID", required=False, )
    type = fields.Selection(string="Type", selection=[('info', 'Info'), ('trans', 'Transaction'), ], required=False, )
    subject = fields.Char(string="Subject", required=False, )
    detail = fields.Text(string="Detail", required=False, )
    date = fields.Datetime(string="Date", required=False, )
    state = fields.Selection(string="", selection=[('read', 'Read'), ('unread', 'Unread'), ], required=False, )