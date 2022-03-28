from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class rdm_reward_config_settings(models.Model):
    _inherit = "res.company"

    reward_limit = fields.Boolean("Reward Limit Per Day")
    reward_limit_product = fields.Boolean("Reward Limit Per Day Per Product")
    reward_limit_count = fields.Integer("Reward Limit Count")
    reward_booking_expired_day = fields.Integer("Reward Booking Expired Day")
    reward_trans_email_tmpl = fields.Many2one("email.template","Reward Transaction Email")
    reward_booking_email_tmpl = fields.Many2one("email.template","Reward Booking Email")