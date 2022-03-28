from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES=[
    ('draft','New'),
    ('open','Open'),
    ('done','Close'),
]

class rdm_schemas(models.Model):
    _name = "rdm.schemas"
    _inherit = "rdm.schemas"

    draw_ids = fields.One2many(comodel_name="rdm.draw", inverse_name="schemas_id", string="Draws", required=False, )


class rdm_draw(models.Model):
    _name = "rdm.draw"
    _description = "Redemption Draw"

    name = fields.Char('Name', size=100, required=True)
    schemas_id = fields.Many2one(comodel_name="rdm.schemas", string="Schemas", required=False, )
    quantity = fields.Integer('Quantity', required=True, default=1)
    sequence = fields.Integer('Sequence')
    


class rdm_draw_detail(models.Model):
    _name = "rdm.draw.detail"
    _description = "Redemption Draw Detail"
    
    # def get_trans(self, ):
    #     return self.browse(cr, uid, ids[0], context=context)

    @api.one
    def trans_confirm(self):        
        _logger.info('Start Trans Confirm')
        # trans = self.get_trans(cr, uid, ids, context=context)
        for trans in self:
            schemas_id = trans.schemas_id.id
            customer_id = trans.customer_id.id
            is_get = self._check_customer_by_schemas(schemas_id, customer_id)
            if is_get:
                raise ValidationError('Customer already get the prize!')
            customer = self.env['rdm.customer'].browse(customer_id)
            if customer:
                if customer.state != 'active':
                    raise ValidationError ('Customer disable or blacklist')      
                    
            values = {}
            values.update({'state': 'done'})        
            super(rdm_draw_detail,self).write(values)
            coupon_id = trans.coupon_id.id
            _logger.info('Start Detail Trans Claimed')
            self.env['rdm.customer.coupon.detail'].trans_claimed(coupon_id)
            _logger.info('End Trans Confirm')

    @api.one
    def trans_re_open_01(self):
        vals = {}
        vals.update({'state': 'open'})
        super(rdm_draw_detail,self).write(vals)

    @api.one
    def trans_re_open_02(self):
        # trans = self.get_trans(cr, uid, ids, context=context)
        for trans in self:
            vals = {}
            vals.update({'state': 'open'})
            super(rdm_draw_detail,self).write(vals)
            # coupon_id = trans.coupon_id.id
            self.env['rdm.customer.coupon.detail'].trans_re_open()
            # self.env['rdm.customer.coupon.detail'].trans_re_open(coupon_id)

    @api.one
    def trans_show_display(self):
        # trans = self.get_trans(cr, uid, ids, context=context)
        for trans in self:
            if trans.state == 'done':
                vals = {}
                vals.update({'iface_show': True})
                return super(rdm_draw_detail, self).write(vals)
            else:
                raise ValidationError ('Please confirm this transaction first!')

    @api.one
    def trans_close_display(self):
        values = {}
        values.update({'iface_show': False})
        return super(rdm_draw_detail,self).write(values)


    @api.onchange('coupon_id')
    def onchange_coupon_id(self):
        if self.coupon_id:
            # coupon_detail = self.env['rdm.customer.coupon.detail'].browse(self.coupon_id.id)
            # if coupon_detail:
            customer_id = self.coupon_id.customer_coupon_id.customer_id.id
            self.customer_id = customer_id

    @api.one
    def _update_customer_id(self):
        # trans = self.get_trans(cr, uid, ids, context=context)  
        for trans in self:
            customer_id = trans.coupon_id.customer_coupon_id.customer_id.id
            vals = {}
            vals.update({'customer_id': customer_id})
            return super(rdm_draw_detail, self).write(vals)

    def _check_customer_by_schemas(self, schemas_id, customer_id):
        args = [('schemas_id','=',schemas_id),('customer_id','=',customer_id),('state','=','done')]
        ids  = self.search(args)        
        if ids:
            return True
        else:
            return False    
        

    draw_id = fields.Many2one(comodel_name="rdm.draw", string="Draw #", required=False, readonly=True)
    schemas_id = fields.Many2one(comodel_name="rdm.schemas", string="Draw Detail #", required=False, readonly=True)
    coupon_id = fields.Many2one(comodel_name="rdm.customer.coupon.detail", string="Coupon #", required=False, )
    customer_id = fields.Many2one(comodel_name="rdm.customer", string="Customer", required=False, readonly=True)
    sequence = fields.Integer(string='Sequence', readonly=True)
    iface_show = fields.Boolean(string='Display', readonly=True, default=False)
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True, default='draft')

    @api.multi
    def write(self, vals):
        # trans = self.get_trans(cr, uid, ids, context=context)
        for trans in self:
            if trans.state == 'done':
                raise ValidationError('Transaction already closed!')

            result = super(rdm_draw_detail, self).write(vals)

            if 'coupon_id' not in vals.keys():
                raise ValidationError("coupon id is empty")

            if 'coupon_id' in vals.keys():
                self._update_customer_id()
        
        return result
