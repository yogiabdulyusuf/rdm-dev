from odoo import api, fields, models, _ 
from odoo.exceptions import UserError, Warning
from datetime import datetime
import logging


class RedemptionMobileEvent(models.Model):
    _name = 'rdm.mobile.event'
    
    
    name = fields.Char('Title', size=200)
    description = fields.Text("Description")
    image_file = fields.Binary('Image File')
    image_filename = fields.Char('Image Filename')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    events_owner = fields.Selection(string='Events Owner', selection=[('internal', 'Internal'), ('tenant', 'Tenant'),])
    
    