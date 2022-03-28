from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError, Warning
import logging
from decimal import Context

_logger = logging.getLogger(__name__)

AVAILABLE_STATES = [
    ("draft","Draft"),
    ("waiting","Waiting"),
    ("review","Review"),
    ("open","Open"),    
    ("pause","Pause"),                    
    ("done","Close"),    
]

AVAILABLE_BLAST_STATES = [
    ("draft","Draft"),
    ("ready","Ready"),
    ("process","Process"),                        
    ("done","Close"),    
    ("failed","Failed"),
]

AVAILABLE_EMAIL_STATES = [
    ("draft","Draft"),
    ("ready","Ready"),
    ("sent","Sent"),                        
    ("failed","Failed"),
]

AVAILABLE_TYPE_STATES = [
    ("email","Email"),
    ("sms","SMS"),
]

AVAILABLE_CALCULATION = [
    ("ditotal","Ditotal"),
    ("terbesar","Terbesar"),                         
]

AVAILABLE_SEARCH_TYPE_STATES = [
    ("all","All"),
    ("customer","Customer"),
    ("gender","Gender"),
    ("ethnic","Ethnic"),
    ("religion","Religion"),
    ("marital","Marital"),
    ("interest","Interest"),
    ("occupation","Occupation"),
    ("zone","Zone"),    
]


class rdm_schemas_segment(models.Model):
    _name = "rdm.schemas.segment"
    _description = "Redemption Trans Segment"
    
    schemas_id =  fields.Many2one("rdm.schemas","Schemas", readonly=True, default=False)
    age_segment =  fields.Many2one("rdm.age.segment","Age Segment")

class rdm_schemas_gender(models.Model):
    _name = "rdm.schemas.gender"
    _description = "Redemption Schemas gender"
    
    schemas_id =  fields.Many2one("rdm.schemas","Schemas", readonly=True, default=False)
    gender_id =  fields.Many2one("rdm.customer.gender","Gender")

class rdm_schemas_ayc_participant(models.Model):
    _name = "rdm.schemas.ayc.participant"
    _description = "Redemption Trans AYC Participant"
    
    schemas_id =  fields.Many2one("rdm.schemas","Schemas", readonly=True, default=False)
    participant_id =  fields.Selection([("1","AYC non participant tenant"),("2","AYC participant tenant")],"Participant Type",required=True)

class rdm_schemas_religion(models.Model):
    _name = "rdm.schemas.religion"
    _description = "Redemption Schemas Religion"
    
    schemas_id =  fields.Many2one("rdm.schemas","Schemas", readonly=True, default=False)
    religion_id =  fields.Many2one("rdm.customer.religion","Religion")

class rdm_schemas_ethnic(models.Model):
    _name = "rdm.schemas.ethnic"
    _description = "Redemption Schemas Ethnic"
    
    schemas_id =  fields.Many2one("rdm.schemas","Schemas", readonly=True, default=False)
    ethnic_id =  fields.Many2one("rdm.customer.ethnic","Ethnic")

class rdm_schemas_tenant(models.Model):
    _name = "rdm.schemas.tenant"
    _description = "Redemption schemas Tenant"
    
    schemas_id =  fields.Many2one("rdm.schemas","schemas", readonly=True, default=False)
    tenant_id =  fields.Many2one("rdm.tenant","Tenant")

class rdm_schemas_marital(models.Model):
    _name = "rdm.schemas.marital"
    _description = "Redemption schemas Marital"
    
    schemas_id =  fields.Many2one("rdm.schemas","schemas", readonly=True, default=False)
    marital_id =  fields.Many2one("rdm.customer.marital","Marital")

class rdm_schemas_interest(models.Model):
    _name = "rdm.schemas.interest"
    _description = "Redemption schemas Interest"
    
    schemas_id =  fields.Many2one("rdm.schemas","schemas", readonly=True, default=False)
    interest_id =  fields.Many2one("rdm.customer.interest","Interest")   

class rdm_schemas_card_type(models.Model):
    _name = "rdm.schemas.card.type"
    _description = "Redemption schemas Card Type"
    
    schemas_id =  fields.Many2one("rdm.schemas","schemas", readonly=True, default=False)
    card_type_id =  fields.Many2one("rdm.card.type","Card Type") 

class rdm_schemas_tenant_category(models.Model):
    _name = "rdm.schemas.tenant.category"
    _description = "Redemption schemas Tenant Category"
    
    schemas_id =  fields.Many2one("rdm.schemas","schemas", readonly=True, default=False)
    tenant_category_id =  fields.Many2one("rdm.tenant.category","Tenant Category")  

class rdm_schemas_rules(models.Model):
    _name = "rdm.schemas.rules"
    _description = "Redemption schemas Rules"
    
    @api.one
    def trans_set_global(self):
        schema = "spending"
        for trans in self:
            if not trans.is_global:
                rules_id = trans.rules_id
                rules_detail_ids = rules_id.rules_detail_ids
                status = False
                for rules_detail_id in rules_detail_ids:
                    rule_schema = rules_detail_id.rule_schema
                    if rule_schema  == schema:
                        status = True
                if status:
                    self.is_global = True
                else:
                    raise ValidationError("Please Provide Spending Rule Schema!")
            else:
                raise ValidationError("Already Set Global!")

    @api.one
    def trans_unset_global(self):
        for trans in self:
            if trans.is_global:
                self.is_global = False
            else:
                raise ValidationError("Rules is not Global")
        
    
    schemas_id =  fields.Many2one("rdm.schemas","schemas", readonly=True, default=False)
    rules_id =  fields.Many2one("rdm.rules","Rules")
    is_global =  fields.Boolean("Is Global", readonly=True, default=False)
    schemas =  fields.Selection([("ditotal","Ditotal"),("terbesar","Terbesar")],"Schemas")


class rdm_schemas_blast(models.Model):
    _name = "rdm.schemas.blast"
    _description = "Redemption Schemas Blast"

    @api.one
    def trans_ready(self):        
        self.state = "ready"
        return True

    @api.one
    def trans_process(self):        
        self.state = "process"
        return True

    @api.one
    def trans_done(self):        
        self.state = "done"
        return True

    @api.one
    def trans_failed(self):        
        self.state = "failed"
        return True

    @api.one
    def blast_customer(self):
        return {
               "type" :  "ir.actions.act_window",
               "name" : "Blast Customer",
               "view_mode" :  "form",
               "view_type" :  "form",                              
               "res_model" : "rdm.schemas.blast.customer",
               "nodestroy" :  True,
               "target" : "new",
               "context" :  {"blast_id" : self.id},
        } 
            
    
    schemas_id =  fields.Many2one("rdm.schemas", "Schemas", readonly=True)
    description =  fields.Text("Description")
    customer_schemas_blast_ids =  fields.Many2many(
                                     "rdm.customer",
                                     "customer_schemas_blast_rel",
                                     "rdm_customer_id",
                                     "rdm_schemas_blast_id",
                                     string = "Customers")
    schedule =  fields.Datetime(string="Schedule",required=True)
    type =  fields.Selection(AVAILABLE_TYPE_STATES,"Type", size=16, required=True)
    blast_detail_ids =  fields.One2many("rdm.schemas.blast.detail","blast_id", readonly=True)
    state =  fields.Selection(AVAILABLE_BLAST_STATES, "Status", size=16, readonly=True, default="draft")

    
    
class rdm_schemas_blast_detail(models.Model):
    _name = "rdm.schemas.blast.detail"
    _description = "Redemption Schemas Blast Detail"

    @api.one
    def trans_ready(self):        
        self.state = "ready"
        return True

    @api.one
    def trans_sent(self):        
        self.state = "sent"
        return True

    @api.one
    def trans_failed(self):        
        self.state = "failed"
        return True
    
    
    blast_id =  fields.Many2one("rdm.schemas.blast", "Schemas Blast", readonly=True,  ondelete="cascade")          
    customer_id =  fields.Many2one("rdm.customer", "Customer", required=True)
    state =  fields.Selection(AVAILABLE_EMAIL_STATES, "Status", size=16, readonly=True, default="draft")
    

class rdm_schemas_blast_customer(models.Model):
    _name = "rdm.schemas.blast.customer"
    _description = "Redemption Schema Blast Customer"
    
    def _check_customer(self, blast_id, customer_id):
        args = [("blast_id","=", blast_id),("customer_id","=", customer_id)]
        detail_ids = self.env["rdm.schemas.blast.detail"].search(args)
        if len(detail_ids) > 0:
            return True
        else:
            return False
    
    def add_customer(self):
        _logger.info("Start Add Customer")
    
        blast_id = self.blast_id
        if self.search_type == "all":
            customer_ids = self.env["rdm.customer"].search([("state","=","active"),])
            for i in range(len(customer_ids)):
                if not self._check_customer(blast_id, customer_ids):
                    data = {}
                    data.update({"blast_id" : blast_id})
                    data.update({"customer_id" :  customer_ids.id})
                    self.env["rdm.schemas.blast.detail"].create(data)
    
        if self.search_type == "customer":
            customer_id = self.customer_id.id
            if not self._check_customer(blast_id, customer_ids):
                data = {}
                data.update({"blast_id" : blast_id})
                data.update({"customer_id" : customer_id})
                self.env["rdm.schemas.blast.detail"].create(data)
    
        if self.search_type == "gender":
            gender_id = self.gender_id.id
            customer_ids = self.env["rdm.customer"].search([("gender","=", gender_id),("state","=","active")])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        if self.search_type == "ethnic":
            ethnic_id = self.enthic_id.id
            customer_ids = self.env("rdm.customer").search([("ethnic","=", ethnic_id),("state","=","active")])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        if self.search_type == "religion":
            religion_id = self.religion_id.id
            customer_ids = self.env["rdm.customer"].search([("religion","=", religion_id)])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        if self.search_type == "marital":
            marital_id = self.marital_id.id
            customer_ids = self.env["rdm.customer"].search([("marital","=", marital_id)])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        if self.search_type == "education":
            education_id = self.education_id.id
            customer_ids = self.env["rdm.customer"].search([("education","=", education_id)])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        if self.search_type == "interest":
            interest_id = self.interest_id.id
            customer_ids = self.env["rdm.customer"].search([("interest_id","=", interest_id)])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        if self.search_type == "occupation":
            occupation_id = self.occupation_id.id
            customer_ids = self.env["rdm.customer"].search([("occupation","=", occupation_id)])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
    
        if self.search_type == "zone":
            zone_id = self.zone_id.id
            customer_ids = self.env["rdm.customer"].search([("zone","=",zone_id)])
            if len(customer_ids) > 0:
                for i in range(len(customer_ids)):
                    if not self._check_customer(blast_id, customer_ids):
                        data = {}
                        data.update({"blast_id" : blast_id})
                        data.update({"customer_id" :  customer_ids.id})
                        self.env["rdm.schemas.blast.detail"].create(data)
            else:
                raise ValidationError("No Customer Found!")
    
        _logger.info("End Add Customer")
    
        return False
        
    
    search_type =  fields.Selection(AVAILABLE_SEARCH_TYPE_STATES,"Search Type", size=16, required=True)
    customer_id =  fields.Many2one("rdm.customer","Customer")
    gender_id =  fields.Many2one("rdm.customer.gender","Customer Gender")
    ethnic_id =  fields.Many2one("rdm.customer.ethnic","Customer Ethnic")
    religion_id =  fields.Many2one("rdm.customer.religion","Customer Religion")
    marital_id =  fields.Many2one("rdm.customer.marital","Customer Marital")
    education_id =  fields.Many2one("rdm.customer.education","Customer Education")
    interest_id =  fields.Many2one("rdm.customer.education","Customer Interest")
    occupation_id =  fields.Many2one("rdm.customer.occupation","Customer Occupation")
    zone_id =  fields.Many2one("rdm.customer.zone","Customer Zone")
    
class rdm_schemas(models.Model):
    _name = "rdm.schemas"
    _description = "Redemption schemas"

    @api.one
    def trans_review(self):
        self.state = "review"

    @api.one
    def trans_start(self):
        self.state = "open"

    @api.one
    def trans_pause(self):
        self.state = "pause"

    @api.one
    def trans_close(self):
        self.state = "done"

    @api.one
    def trans_reset(self):
        self.state = "open"

    @api.one
    def trans_waiting(self):
        self.state = "waiting"
    
    
    def active_schemas(self):
        ids = self.env["rdm.schemas"].search([("state","=","open"),("type","=","promo"),])
        return self.env["rdm.schemas"].browse(ids)
    
    def promo_to_close(self):
        today = datetime.now().strftime("%Y-%m-%d")
        args = [("state","=","open"),("end_date","<", today)]
        ids = self.search(args)
        vals = {}
        vals.update({"state" : "done"})
        ids.write(vals)
        return True
    
    def active_promo_schemas(self):
        today = datetime.now().strftime("%Y-%m-%d")
        ids = self.env["rdm.schemas"].search([("state","=","open"),("type","=","promo"),("start_date","<=",today),("end_date",">=", today)])
        return ids
    
    def active_point_schemas(self):
        today = datetime.now().strftime("%Y-%m-%d")
        ids = self.env["rdm.schemas"].search([("state","=","open"),("type","=","point"),("start_date","<=",today),("end_date",">=", today)])
        return ids
    
    @api.one
    def start_blast(self):
        _logger.info("Start Schemas Blast")
        active_schemas = self.active_schemas()
        for schemas in active_schemas:
            blast_ids = schemas.blast_ids
            for blast in blast_ids:
                if blast.state == "ready":
                    blast_schedule  = datetime.strptime(blast.schedule, "%Y-%m-%d %H:%M:%S")
                    if blast_schedule <= datetime.now():
                        _logger.info("Email Blast for " + schemas.name + " executed")

                        self.env["rdm.schemas.blast"].trans_process(blast.id)

                        email_from = "info@taman-anggrek-mall.com"
                        subject = schemas.name
                        body_html = schemas.desc_email
                        blast_customer_schemas_blast_ids = blast.customer_schemas_blast_ids
                        #blast_detail_ids = blast.blast_detail_ids
                        for customer_id in blast_customer_schemas_blast_ids:
                            if customer_id.receive_email:
                                _logger.info("Send Email to " + customer_id.name)

                                # email_to = customer_id.email
                                # message = {}
                                # message.update({"email_from" : email_from})
                                # message.update({"email_to" : email_to})
                                # message.update({"subject" : subject})
                                # message.update({"body_html" : body_html})
                                # self._send_email_notification(message)
                                
                                email_to = customer_id.email
                                args = [('name', '=', 'Schemas Blast')]  # CHANGE
                                template_ids = self.env['mail.template'].search(args)
                                vals = {}
                                vals.update({"email_from" : email_from})
                                vals.update({'email_to': email_to})
                                vals.update({"subject" : subject})
                                vals.update({"body_html" : body_html})
                                template_ids.write(vals)
                                template_ids[0].sudo().send_mail(schemas.id, force_send=True)
                            else:
                                _logger.info("Send Email to " + customer_id.name + " not allowed!")
                        self.env("rdm.schemas.blast").trans_done(blast.id)
        _logger.info("End Schemas Blast")
    
    @api.one
    def close_schemas_scheduler(self):
        _logger.info("Start Close Schemas Scheduler")
        result = self.promo_to_close()
        _logger.info("End Close Schemas Scheduler")
        return result

    @api.one    
    def _get_open_schemas(self):
        for trans in self:
            ids = None
            if trans.type == "promo":
                ids = self.env["rdm.schemas"].search([("type","=","promo"),("state","=","open"),])
            if trans.type == "point":
                ids = self.env["rdm.schemas"].search([("type","=","point"),("state","=","open"),])
            if ids:
                return True
            else:
                return False
    #
    # def _send_email_notification(self):
    #     _logger.info("Start Send Email Notification")
    #     mail_mail = self.env("mail.mail")
    #     mail_ids = []
    #     mail_ids.append(mail_mail.create( {
    #         "email_from" :  values["email_from"],
    #         "email_to" :  values["email_to"],
    #         "subject" :  values["subject"],
    #         "body_html" :  values["body_html"],
    #         }))
    #     result_id = mail_mail.send(mail_ids)
    #     _logger.info("Mail ID : " + str(result_id))
    #     _logger.info("End Send Email Notification")
    
    
    name        =  fields.Char(string="Name", size=200, required=True)
    type        =  fields.Selection([("promo","Promo"),("point","Point")], string="Type", readonly=True)
    calculation =  fields.Selection(AVAILABLE_CALCULATION,"Calculation",size=16,required=True)
    description =  fields.Text(string="Description",required=True)
    desc_email  =  fields.Text(string="Description For Email",required=True)
    desc_sms    =  fields.Char(string="Description For SMS", size=140,required=True)

    #Periode
    start_date  =  fields.Date(string="Start Date",required=True)
    end_date    =  fields.Date(string="End Date",required=True)
    last_redeem =  fields.Date(string="Last Redeem",required=True)
    draw_date   =  fields.Date(string="Draw Date",required=True, default=fields.Date.today())
        
        #Spend, coupon , point and reward
    max_spend_amount    =  fields.Float(string="Maximum Spend Amount", required=True, help="-1 for No Limit", default=-1)
    max_spend_amount_global =  fields.Boolean(string="Global")
    max_coupon          =  fields.Integer(string="Maximum Coupon")
    max_coupon_global   =  fields.Boolean(string="Maximum Coupon Global")
    max_point           =  fields.Integer(string="Maximum Point")
    max_point_global    =  fields.Boolean(string="Maximum Point Global")
    min_spend_amount    =  fields.Float(string="Minimum Spend Amount", required=False, help="-1 for No Limit")
    coupon_spend_amount =  fields.Float(string="Coupon Spend Amount",required=True)
    point_spend_amount  =  fields.Float(string="Point Spend Amount",required=True)
    reward_spend_amount =  fields.Float(string="Reward Spend Amount", required=True, default=-1)
    limit_coupon        =  fields.Integer(string="Coupon Limit",help="-1 for No Limit",required=True, default=-1)
    limit_coupon_per_periode =  fields.Integer(string="Coupon Limit Per Periode", help="-1 for No Limit",required=True, default=-1)
    min_coupon          =  fields.Integer(string="Minimum Coupon")
    limit_point         =  fields.Integer(string="Point Limit",help="-1 for No Limit",required=True, default=-1)
    limit_point_per_periode =  fields.Integer(string="Point Limit Per Periode", help="-1 for No Limit", required=True, default=-1)
    min_point           =  fields.Integer(string="Minimum Point")
    rdm_reward_ids      =  fields.Many2one(comodel_name="rdm.reward", string="Redeem Reward", required=False, )
    limit_reward        =  fields.Integer(string="Reward Limit",help="-1 for No Limit",required=True, default=-1)
    point_expired_date  =  fields.Date(string="Point Expired Date")


    segment_ids =  fields.One2many("rdm.schemas.segment","schemas_id","Segment")
    image1      =  fields.Binary(string="schemas Image")

    #Bank Promo
    bank_id     = fields.Many2one(comodel_name="rdm.bank", string="Bank Promo", required=False, )

    #Customer Filter
    gender_ids      = fields.One2many(comodel_name="rdm.schemas.gender", inverse_name="schemas_id", string="schemas Gender", required=False, )
    religion_ids    = fields.One2many(comodel_name="rdm.schemas.religion", inverse_name="schemas_id", string="schemas Religion", required=False, )
    ethnic_ids      = fields.One2many(comodel_name="rdm.schemas.ethnic", inverse_name="schemas_id", string="schemas Ethnic", required=False, )
    marital_ids     = fields.One2many(comodel_name="rdm.schemas.marital", inverse_name="schemas_id", string="schemas Marital", required=False, )
    interest_ids    = fields.One2many(comodel_name="rdm.schemas.interest", inverse_name="schemas_id", string="schemas Interest", required=False, )
    card_type_ids   = fields.One2many(comodel_name="rdm.schemas.card.type", inverse_name="schemas_id", string="schemas AYC Card Type", required=False, )

    #Tenant Filter
    tenant_ids          = fields.One2many(comodel_name="rdm.schemas.tenant", inverse_name="schemas_id", string="schemas Tenant", required=False, )
    tenant_category_ids = fields.One2many(comodel_name="rdm.schemas.tenant.category", inverse_name="schemas_id", string="Tenant Category", required=False, )
    ayc_participant_ids = fields.One2many(comodel_name="rdm.schemas.ayc.participant", inverse_name="schemas_id", string="AYC Participant", required=False, )

    #Rules List
    rules_ids   = fields.One2many(comodel_name="rdm.schemas.rules", inverse_name="schemas_id", string="Rules", required=False, )

    #Blast List
    blast_ids   = fields.One2many(comodel_name="rdm.schemas.blast", inverse_name="schemas_id", string="Blast", required=False, )

    #Receipt Header and Footer
    receipt_header =  fields.Char(string="Receipt Header", size=50)
    receipt_footer =  fields.Text(string="Receipt Footer",)
    state          =  fields.Selection(AVAILABLE_STATES, string="Status", size=16, readonly=True,  default="draft")
    
    @api.model
    def create(self, vals):
        if "point_spend_amount" in vals.keys():
            if self.point_spend_amount > 0:
                if not self.point_expired_date:
                    raise ValidationError("Point Expired Date Required!")
    
        id =  super(rdm_schemas, self).create(vals)
        id.trans_waiting()
        return id

    @api.multi
    def write(self, vals):
        if "point_spend_amount" in vals.keys():
            if self.point_spend_amount > 0:
                if not self.point_expired_date:
                    raise ValidationError("Point Expired Date Required!")
    
        result =  super(rdm_schemas, self).write(vals)
        return result
