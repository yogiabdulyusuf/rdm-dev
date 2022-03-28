from odoo import api, fields, models


class rdm_reward_trans(models.Model):
    _name = "rdm.reward.trans"
    _inherit = "rdm.reward.trans"

    trans_id = fields.Many2one(comodel_name="rdm.trans", string="Transaction", required=False, readonly=True)
