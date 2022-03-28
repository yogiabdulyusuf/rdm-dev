from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class MassMailingList(models.Model):
    """Model of a contact list. """
    _inherit = 'mail.mass_mailing.list'
    
    