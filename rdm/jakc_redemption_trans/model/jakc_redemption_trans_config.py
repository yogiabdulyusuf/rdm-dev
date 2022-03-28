from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class rdm_trans_config_settings(models.Model):
    _inherit = "res.company"

    trans_delete_allowed = fields.Boolean('Allow Delete Transaction')
    trans_delete_approver = fields.Many2one('hr.employee','Delete Transaction Approver')
    trans_email_tmpl = fields.Many2one('email.template','Transaction Email')
    state = fields.Boolean('Status')
