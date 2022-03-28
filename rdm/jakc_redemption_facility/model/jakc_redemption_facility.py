from odoo import api, fields, models
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ("draft","New"),    
    ("active","Active"),
    ("disable", "Disable"),
    ("terminate", "Terminate"),
]

AVAILABLE_PARTICIPANT = [
    ("1","AYC non participant tenant"),
    ("2","AYC participant tenant")
]


class rdm_building_floor(models.Model):
    _name = "rdm.building.floor"
    _description = "Redemption Building Floor"

    name = fields.Char('Name', size=100, required=True)
    sequence = fields.Integer("Sequence", required=True)
    lot_ids = fields.One2many('rdm.building.lot','floor_id', string="Lots")

class rdm_building_lot(models.Model):
    _name = "rdm.building.lot"
    _description = "Redemption Building Lot"
    
    name = fields.Char('Name', size=100, required=True)
    floor_id = fields.Many2one('rdm.building.floor', 'Floor', required=True)
    

