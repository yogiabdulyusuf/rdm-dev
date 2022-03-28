from odoo import api, fields, models

class rdm_customer(models.Model):
    _name = "rdm.customer"
    _inherit = "rdm.customer"

    @api.depends('trans_ids')
    def _compute_total_transaction(self):
        total_amount = 0.0
        for row in self:
            for trans in row.trans_ids:
                 total_amount += trans.total_amount
            row.total_amount = total_amount
    
    trans_ids = fields.One2many(comodel_name="rdm.trans", inverse_name="customer_id", string="Transaction", required=False, readonly=True)
    total_amount = fields.Float('Total Transaction', compute="_compute_total_transaction", readonly=True, store=False)