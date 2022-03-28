from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class rdm_config_settings(models.Model):
    _inherit = 'res.company'

    rdm_server = fields.Char('RDM Server', size=50)
    enable_email = fields.Boolean('Enable Email')
    pop3_download = fields.Boolean('POP3 Download')
    pop3_server = fields.Char('POP3 Server', size=50)
    pop3_user = fields.Char('POP3 User', size=50)
    pop3_password = fields.Char('POP3 Password', size=50)
    email_from = fields.Char('Email From', size=50)
    report_server = fields.Char('Report Server', size=50)
    report_server_port = fields.Char('Report Server Port', size=50)
    report_user = fields.Char('Report User', size=50)
    report_password = fields.Char('Report Password', size=50)
    trans_delete_allowed = fields.Boolean('Allow Delete Transaction')
    trans_delete_approver = fields.Many2one('hr.employee','Delete Transaction Approver')
    ayc_image_horizontal = fields.Binary(string='AYC Image Horizontal')
    ayc_image_vertical = fields.Binary(string='AYC Image Vertical')