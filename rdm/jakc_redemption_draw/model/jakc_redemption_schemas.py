from odoo import api, fields, models
import logging
from psycopg2.extras import _logging

_logger = logging.getLogger(__name__)

class rdm_schemas(models.Model):
    _name = "rdm.schemas"
    _inherit = "rdm.schemas"

    @api.one
    def trans_generate_draw_detail(self):
        _logging.info("Start Generate Draw Detail")
        # trans = self.get_trans(cr, uid, ids, context=None)
        for trans in self:
            _logging.info("Transaction Found")
            draw_ids = trans.draw_ids
            for draw_id in draw_ids:
                for i in range(0, draw_id.quantity):
                    vals = {}
                    vals.update({'draw_id': draw_id.id})
                    vals.update({'schemas_id': self.id})
                    vals.update({'sequence': i + 1})
                    result_id = self.env['rdm.draw.detail'].create(vals)
        else:
            _logging.info("Transaction not found")
        _logging.info("End Generate Draw Detail")


    @api.one
    def trans_clear_draw_detail(self):
        _logging.info("Start Clear Draw Detail")
        args = [('schemas_id','=', self.id)]
        detail_ids = self.env['rdm.draw.detail'].search(args)
        detail_ids.unlink()
        _logging.info("End Clear Draw Detail")
    

    draw_ids        = fields.One2many(comodel_name="rdm.draw", inverse_name="schemas_id", string="Draws", required=False, )
    draw_detail_ids = fields.One2many(comodel_name="rdm.draw.detail", inverse_name="schemas_id", string="Draw Detail", required=False, )
