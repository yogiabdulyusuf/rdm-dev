from odoo import api, fields, models

class ResCompanyAPISettings(models.Model):
    _inherit = 'res.company'

    server_url = fields.Char(string="Server URL API", )