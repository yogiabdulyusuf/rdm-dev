from odoo import api, fields, models, _ 
from odoo.exceptions import UserError, Warning
from datetime import datetime
import logging


class RedemptionMobileBanner(models.Model):
    _name = 'rdm.mobile.banner'
    
    
    name = fields.Char('Title', size=200)
    description = fields.Text(string='Description')
    image_file = fields.Binary('Image File')
    image_filename = fields.Char('Image Filename')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    link = fields.Char(string='Link')
    
    
