from odoo import api, fields, models
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [
    ('draft','New'),
    ('active','Active'),
    ('done','Close'),
    ('expired','Expired'),
    ('req_delete','Request For Delete'),
    ('delete','Deleted')    
]

AVAILABLE_TRANS_TYPE = [
    ('reward','Reward'),
    ('adjust','Adjustment'),
]

class rdm_customer_point(models.Model):
    _name = 'rdm.customer.point'
    _description = 'Redemption Customer Point'

    @api.one
    def trans_close(self, point_id):
        datas = self.env['rdm.customer.point'].search([('id','=',point_id),])
        vals = {}
        vals.update({'state': 'done'})
        datas.write(vals)

    @api.one
    def trans_expired(self):
        self.state = "expired"
    
    @api.one
    def process_expired(self):
        _logger.info('Start Customer Point Process Expired')
        now = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')
        sql_req = "UPDATE rdm_customer_point SET state='expired' WHERE expired_date < '" + now + "' AND state='active'" 
        self.env.cr.execute(sql_req)
        _logger.info('End Customer Point Process Expired')
        return True
    
    @api.one
    def get_active_customer_point(self):
        args = [('state','=','active')]
        return self.env['rdm.customer.point'].browse(args)

    def get_customer_total_point(self):
        now = datetime.now().strftime('%Y-%m-%d')
        sql_req = """SELECT sum(a.point - a.usage) as total FROM rdm_customer_point a   
                  WHERE a.customer_id='{}' AND expired_date >= '{}'  
                  AND a.state='active'""".format(self.id, now)
                          
        self.env.cr.execute(sql_req)
        sql_res = self.env.cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0        
        _logger.info(total_points)
        return total_points

    def get_customer_total_point_usage(self, customer_id):            
        sql_req = """SELECT sum(a.usage) as total FROM rdm_customer_point a  
                  WHERE (a.customer_id='{}')                   
                  AND a.state='active'""".format(customer_id)
                          
        self.env.cr.execute(sql_req)
        sql_res = self.env.cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0        
                    
        return total_points 

    def get_usages(self):
        # trans_id = self.id
        # res = {}
        total_points = self.env['rdm.customer.point.detail'].get_point_usage(self.id)
        _logger.info('Total Points : ' + str(total_points))
        return total_points
    
    def deduct_point(self, trans_id, customer_id, point):
        status = False
        total_point = 0
        sisa_point = point
        today = datetime.today()
        args = [('customer_id', '=', customer_id), ('expired_date', '>=', today), ('state', '=', 'active')]
        point_ids = self.search(args, order='expired_date asc')
        # point_ids = self.browse(ids)
        for point_id in point_ids:
            avai_point = point_id.point - point_id.usage
            if avai_point < sisa_point:
                total_point = total_point + avai_point
                sisa_point = sisa_point - avai_point
                trans_data = {}
                trans_data.update({'customer_point_id': point_id.id})
                trans_data.update({'trans_id': trans_id})
                trans_data.update({'trans_type': 'reward'})
                trans_data.update({'point': avai_point})
                self.env['rdm.customer.point.detail'].deduct_point(trans_data)
                point_id.write({'usage': point_id.usage + avai_point})
                self.trans_close(point_id.id)
            else:
                total_point = total_point + sisa_point
                trans_data = {}
                trans_data.update({'customer_point_id': point_id.id})
                trans_data.update({'trans_id': trans_id})
                trans_data.update({'trans_type': 'reward'})
                trans_data.update({'point': sisa_point})
                self.env['rdm.customer.point.detail'].deduct_point(trans_data)
                point_id.write({'usage': point_id.usage + sisa_point})
                break


    customer_id = fields.Many2one(comodel_name="rdm.customer", string="Customer", required=True, )
    trans_type = fields.Selection(selection=[('promo','Promotion'),('point','Point'),('adjust','Adjust'),('reference','Reference'),('member','New Member')], string='Transaction Type')        
    point = fields.Integer(string='Point #', default=0)       
    usage = fields.Integer(string='Usage #', default=0)      
    expired_date = fields.Date('Expired Date')        
    state = fields.Selection(selection=AVAILABLE_STATES,string='Status',size=16,readonly=True, default='active')      
    

class rdm_customer_point_detail(models.Model):
    _name = "rdm.customer.point.detail"
    _description = "Redemption Customer Point Detail"

    def get_point_usage(self, trans_id):
        sql_req = """SELECT sum(a.point) as total FROM rdm_customer_point_detail a
                  WHERE (a.customer_point_id='{}')""".format(trans_id)
    
        self.env.cr.execute(sql_req)
        sql_res = self.env.cr.dictfetchone()
        if sql_res:
            total_points = sql_res['total']
        else:
            total_points = 0
    
        if total_points is None:
            total_points = 0
    
        return total_points
    
    @api.one
    def deduct_point(self, values):
        trans_data = {}
        trans_data.update({'customer_point_id': values.get('customer_point_id')})
        trans_data.update({'reward_trans_id': values.get('trans_id')})
        trans_data.update({'trans_type': values.get('trans_type')})
        trans_data.update({'point': values.get('point')})
        self.env['rdm.customer.point.detail'].create(trans_data)


    customer_point_id = fields.Many2one(comodel_name="rdm.customer.point", string="Customer Point", required=False, )
    trans_type = fields.Selection(selection=AVAILABLE_TRANS_TYPE, string='Transaction Type', size=16)
    point = fields.Integer(string='Point')

