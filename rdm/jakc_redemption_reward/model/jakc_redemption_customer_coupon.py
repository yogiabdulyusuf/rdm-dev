from odoo import api, fields, models

class rdm_customer_coupon(models.Model):
    _name = "rdm.customer.coupon"
    _inherit = "rdm.customer.coupon"

    reward_trans_id = fields.Many2one(comodel_name="rdm.reward.trans", string="Reward Transaction ID", required=False, )
