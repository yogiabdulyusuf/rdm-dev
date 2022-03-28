from odoo import api, fields, models

class rdm_customer(models.Model):
    _name = "rdm.customer"
    _inherit = "rdm.customer"

    reward_trans_ids = fields.One2many(comodel_name="rdm.reward.trans", inverse_name="customer_id", string="Rewards", required=True, )
