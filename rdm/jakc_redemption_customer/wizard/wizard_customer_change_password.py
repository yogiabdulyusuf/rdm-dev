from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning

class rdm_customer_change_password(models.Model):
    _name = 'rdm.customer.change.password'
    _description = 'Redemption Customer Change Password'

    @api.multi
    def change_password(self):
        # AMBIL ACTIVE ID YANG ADA DI FORM
        active_id = self.env['rdm.customer'].browse(self.env.context.get('active_id'))

        if self.password_new == self.password_confirm:
            active_id.password = self.password_new
        else:
            raise ValidationError("Wrong password, Please try again!")


    password_new = fields.Char(string="New Password", required=True, )
    password_confirm = fields.Char(string="Confirm Password", required=True, )
