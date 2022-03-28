from odoo import api, fields, models
import time
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ('draft','New'),
    ('active','Active'),
    ('expired','Expired'),
    ('claimed','Claimed'),    
    ('req_delete','Request For Delete'),
    ('delete','Deleted')
]


AVAILABLE_TRANS_TYPE = [
    ('promo','Promotion'),
    ('point','Point'),
    ('reward','Reward'),
    ('reference','Reference'),
    ('member','New Member'),
]


class rdm_customer_coupon(models.Model):
    _name = 'rdm.customer.coupon'
    _description = 'Redemption Customer Coupon'
                
    # def get_trans(self):
    #     trans_id = self.id
    #     return self.browse(trans_id)
    
    # @api.one
    # def process_expired(self, cr, uid, context=None):
    #     _logger.info('Start Customer Coupon Process Expired')
    #     _logger.info('End Customer Coupon Process Expired')
    #     return True
    
    @api.one
    def delete_coupon(self):
        _logger.info('Start Delete Coupon')
        # trans = self.get_trans()
        for trans in self:
            customer_coupon_detail_ids = trans.customer_coupon_detail_ids
            for customer_coupon_detail_id in customer_coupon_detail_ids:
                self.env['rdm.customer.coupon.detail'].trans_delete(customer_coupon_detail_id.id)
            _logger.info('End Delete Coupon')
    
    @api.one
    def undelete_coupon(self):
        _logger.info('Start UnDelete Coupon')
        # trans = self.get_trans()
        for trans in self:
            customer_coupon_detail_ids = trans.customer_coupon_detail_ids
            for customer_coupon_detail_id in customer_coupon_detail_ids:
                self.env['rdm.customer.coupon.detail'].trans_close(customer_coupon_detail_id.id)
            _logger.info('End UnDelete Coupon')
    
    @api.one
    def generate_coupon(self):
        _logger.info('Start Generate Coupon')
        trans = self
        coupon = trans.coupon
        for i in range (0,coupon):
            values = {}
            values.update({'customer_coupon_id' : trans.id})
            values.update({'expired_date' : trans.expired_date})
            self.env['rdm.customer.coupon.detail'].create(values)
        time.sleep(0.1)
        _logger.info('End Generate Coupon')
            

    customer_id =  fields.Many2one('rdm.customer','Customer', required=False)
    trans_type =  fields.Selection(AVAILABLE_TRANS_TYPE, 'Transaction Type', size=16)       
    coupon =  fields.Integer('Coupon #', required=False, default=0)
    expired_date =  fields.Date('Expired Date', required=False)
    customer_coupon_detail_ids =  fields.One2many('rdm.customer.coupon.detail','customer_coupon_id','Coupon Codes')
    state =  fields.Selection(AVAILABLE_STATES,'Status',size=16,readonly=True, default='active')
       
    @api.model
    def create(self, vals):
        id = super(rdm_customer_coupon, self).create(vals)
        id.generate_coupon()
        return id

    

class rdm_customer_coupon_detail(models.Model):
    _name = 'rdm.customer.coupon.detail'
    _description = 'Redemption Customer Coupon Detail'

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.coupon_code))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            recs = self.search([('coupon_code', operator, name)] + args, limit=limit)
        else:
            recs = self.search([] + args, limit=limit)
        return recs.name_get()
    
    # def get_trans(self):
    #     trans_id = self.id
    #     return self.browse(trans_id)
    
    @api.one
    def trans_delete(self):
        _logger.info('Start Trans Delete')
        vals = {}
        vals.update({'state' : 'delete'})
        self.write(vals)
        _logger.info('End Trans Delete')
    
    @api.one
    def trans_close(self):
        _logger.info('Start Trans Close')
        vals = {}
        vals.update({'state' : 'done'})
        self.write(vals)
        _logger.info('End Trans Close')
    
    @api.one
    def trans_expired(self):
        _logger.info('Start Trans Expired')
        vals = {}
        vals.update({'state' : 'expired'})
        self.write(vals)
        _logger.info('End Trans Expired')
    
    @api.one
    def trans_claimed(self):
        _logger.info('Start Customer Coupon Detail Process Claimed')
        vals = {}
        vals.update({'state' : 'claimed'})
        super(rdm_customer_coupon_detail,self).write(vals)
        _logger.info('End Customer Coupon Detail Process Claimed')
        return True
    
    @api.one
    def trans_re_open(self):
        _logger.info('Start Customer Coupon Detail Process Re-open')
        vals = {}
        vals.update({'state' : 'active'})
        super(rdm_customer_coupon_detail,self).write(vals)
        _logger.info('End Customer Coupon Detail Process Re-open')
        return True
    
    @api.one
    def expired_coupon(self, customer_coupon_id):
        _logger.info('Start Expired Coupon')
        args = {('customer_coupon_id','=',customer_coupon_id)}
        ids = self.search(args)
        vals = {}
        vals.update({'state' : 'expired'})
        ids.write(vals)
        _logger.info('End Expired Coupon')
        

    customer_coupon_id = fields.Many2one(comodel_name="rdm.customer.coupon", string="Customer Coupon", required=False, readonly=True)
    coupon_code =  fields.Char(string='Coupon Code', size=15, required=False, readonly=True)
    expired_date =  fields.Date(string='Expired Date', required=False, readonly=True)
    state =  fields.Selection(AVAILABLE_STATES,'Status',size=16,readonly=True, default='active')

    @api.model
    def create(self, vals):
        vals['coupon_code'] = self.env['ir.sequence'].next_by_code('rdm.customer.coupon.sequence')
        _logger.info("Generate Coupon" + vals['coupon_code'])

        id =  super(rdm_customer_coupon_detail, self).create(vals)
        return id
    
    @api.multi
    def write(self, vals):
        # trans = self.get_trans(cr, uid, ids)
        # for trans in  self:
        if 'state' in vals.keys():
            if vals.get('state') == 'claimed':
                return self.process_claimed()

        return super(rdm_customer_coupon_detail, self).write(vals)
