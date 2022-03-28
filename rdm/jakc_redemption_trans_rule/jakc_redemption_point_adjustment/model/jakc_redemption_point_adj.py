from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),    
    ('open','Open'),    
    ('done', 'Closed'),
    ('reqdel', 'Request Delete'),
    ('delete', 'Deleted'),
]

AVAILABLE_ADJUST_TYPE = [
    ('+','Add'),    
    ('-','Deduct'),    
]


class rdm_point_adj(models.Model):
    _name="rdm.point.adj"
    _description =  "Redemption Point Adjustment"

    def trans_close(self):
        self.state = 'done'
        self._adjust_point_()
    
    # def print_reciept(self):
    #
    #
    # def re_print(self):

    @api.one
    def trans_reset(self):
        self.state = 'open'

    @api.one
    def trans_req_delete(self):
        self.state = 'req_delete'

    @api.one
    def trans_delete(self):
        self.state = 'delete'

    
    # def _get_trans(self):
    #     return self.trans_id
    
    def _adjust_point_(self):
        _logger.info('Start Point Adjustment')
        # trans_id = self.id
        # trans = self._get_trans()
        for trans in self:
            point_data = {}
            point_data.update({'customer_id': trans.customer_id.id})
            point_data.update({'adj_id':trans.id})
            point_data.update({'trans_type':'adjust'})
            if trans.adjust_type == '+':
                point_data.update({'point':trans.point})
                point_data.update({'expired_date': trans.expired_date})
                self.env['rdm.customer.point'].create(point_data)
            if trans.adjust_type == '-':
                customer = self.env['rdm.customer'].browse(trans.customer_id.id)
                if customer.point >= trans.point:
                    self.env['rdm.customer.point'].deduct_point(trans.id, trans.customer_id.id, trans.point)
                else:
                    raise ValidationError('Point not enough for adjustment!')
            _logger.info('End Point Adjustment')


    trans_date = fields.Date('Date',readonly=True, default=fields.Date.today())
    customer_id = fields.Many2one('rdm.customer','Customer', required=True)
    adjust_type = fields.Selection(AVAILABLE_ADJUST_TYPE,'Type',size=16, required=True, default="+")
    point = fields.Integer('Point',required=True, default=0)
    expired_date = fields.Date('Expired Date')
    printed = fields.Boolean('Printed',readonly=True, default=False)
    info = fields.Text(string="Information", required=False, )
    state = fields.Selection(AVAILABLE_STATES,'Status',size=16,readonly=True, default="draft")


    @api.model    
    def create(self, values):
        values.update({'state':'open'})
        if values.get('adjust_type') == '+':
            if values.get('expired_date'):
                id =  super(rdm_point_adj, self).create(values)
                return id
            else:
                raise ValidationError('Please define Expired Date!')
        else:
            id =  super(rdm_point_adj, self).create(values)
            return id

