from odoo import api, fields, models

class rdm_customer_point(models.Model):
    _name = "rdm.customer.point"
    _inherit = "rdm.customer.point"

    reward_trans_id = fields.Many2one(comodel_name="rdm.reward.trans", string="Reward Transaction ID", required=False, )
