from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class rdm_customer_type(models.Model):
    _name = "rdm.customer.type"
    _description = "Customer Type"
            
    name = fields.Char('Name', size=100, required=True)     


class rdm_customer_ethnic(models.Model):
    _name = "rdm.customer.ethnic"
    _description = "Customer Ethic"
            
    name = fields.Char('Name', size=100, required=True)          
      

class rdm_customer_religion(models.Model):
    _name = "rdm.customer.religion"
    _description = "Customer Religion"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_customer_gender(models.Model):
    _name = "rdm.customer.gender"
    _description = "Customer Gender"
            
    name = fields.Char('Name', size=100, required=True)  


class rdm_customer_marital(models.Model):
    _name = "rdm.customer.marital"
    _description = "Customer Marital"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_customer_zone(models.Model):
    _name = "rdm.customer.zone"
    _description = "Customer Residential Zone"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_customer_education(models.Model):
    _name = "rdm.customer.education"
    _description = "Customer Education"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_customer_interest(models.Model):
    _name = "rdm.customer.interest"
    _description = "Customer Interest"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_customer_occupation(models.Model):
    _name = "rdm.customer.occupation"
    _description = "Customer Occupation"
    
    name = fields.Char('Name', size=100, required=True)

class rdm_card_type(models.Model):
    _name = "rdm.card.type"
    _description = "Card Type"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_tenant_category(models.Model):
    _name = "rdm.tenant.category"
    _description = "Tenant Category"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_tenant_grade(models.Model):
    _name = "rdm.tenant.grade"
    _description = "Tenant Grade"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_bank(models.Model):
    _name = "rdm.bank"
    _description = "Bank"
            
    name = fields.Char('Name', size=100, required=True)      
    bank_card_ids = fields.One2many('rdm.bank.card','bank_id','Bank Card')


class rdm_bank_card(models.Model):
    _name = "rdm.bank.card"
    _description = "Bank Card"
            
    bank_id = fields.Many2one('rdm.bank','Bank ID', default=False)
    name = fields.Char('Name', size=100, required=True)        
    card_type = fields.Many2one('rdm.bank.card.type','Card Type', required=True)
 

class rdm_bank_card_type(models.Model):
    _name = "rdm.bank.card.type"
    _description = "Redemption Bank Card Type"
    
    name = fields.Char('Name', size=100, required=True)

class rdm_tenant_title(models.Model):
    _name = "rdm.tenant.title"
    _description = "Tenant Title"
            
    name = fields.Char('Name', size=100, required=True)
   

class rdm_province(models.Model):
    _name = "rdm.province"
    _description = "Province"
            
    name = fields.Char('Name', size=100, required=True)

class rdm_city(models.Model):
    _name = "rdm.city"
    _description = "City"
            
    name = fields.Char('Name', size=100, required=True)


class rdm_age_segment(models.Model):
    _name = 'rdm.age.segment'
    _description = 'Redemption Age Segment'
    _order = "start_age"

    @api.depends('start_age','end_age')
    @api.one
    def concate_name(self):
        _logger.info(str(self.start_age) + " to  " + str(self.end_age) + " Years")
        self.name = str(self.start_age) + " to  " + str(self.end_age) + " Years"

    name = fields.Char('Name', size=200, compute="concate_name", store=True, readonly=True)
    start_age = fields.Integer('Start Age', required=True)
    end_age = fields.Integer('End Age', required=True)
    

class rdm_building_floor(models.Model):
    _name = "rdm.building.floor"
    _description = "Redemption Building Floor"

    name = fields.Char('Name', size=100, required=True)
    sequence = fields.Integer("Sequence", required=True)
    image = fields.Binary(string='Image')



