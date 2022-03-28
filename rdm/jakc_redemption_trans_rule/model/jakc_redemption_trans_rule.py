from odoo import api, fields, models

SCHEMAS_SelectionS = [
    ("ethnic","Ethnic"),
    ("religion","Religion"),
    ("gender","Gender"),
    ("marital","Marital"),
    ("zone","Zone"),
    ("education","Education"),
    ("interest","Interest"),
    ("occupation","Occupation"),
    ("birthday","Birthday"),
    ("day","Day"),
    ("dayname","Day Name"),
    ("cardtype","Card Type"),
    ("tenant","Tenant"),
    ("tenanttype","Tenant Type"),
    ("bank","Bank"),
    ("bankcard","Bank Card"),
    ("age","Customer Age"),
    ("spending","Spending Amount"),
    ("participant","Participant Type"),
    ("cash","Cash"),    
]

OPERATOR_SelectionS = [
    ("eq","Equal"),
    ("ne","Not Equal"),
    ("lt","Less Than"),
    ("gt","Greater Than"),
    ("bw","Between"),
]

DAY_NAME_SelectionS = [
    ("01","Sunday"),
    ("02","Monday"),
    ("03","Tuesday"),
    ("04","Wednesday"),
    ("05","Thursday"),
    ("06","Friday"),
    ("07","Saturday")
]

OPERATION_SelectionS = [                    
    ("or","OR"),
    ("and","AND"),
]

AVAILABLE_PARTICIPANT = [
    ("1","AYC non participant tenant"),
    ("2","AYC participant tenant")
]

class rdm_rules(models.Model):
    _name = "rdm.rules"
    _description = "Redemption Rules"

    name = fields.Char(string="Name", size=200, required=True)
    apply_for = fields.Selection(string="Apply For", selection=[("1", "Coupon"), ("2", "Point"), ("3", "Reward"), ], required=True, )
    reward_id = fields.Many2one(comodel_name="rdm.reward", string="Reward")
    operation = fields.Selection(string="Operation", selection=[("add", "Add"), ("multiple", "Multiple"), ], required=True, )
    calculation = fields.Selection(string="Method", selection=[("terbesar", "Terbesar"), ("ditotal", "Di Total"), ], required=False, )
    quantity = fields.Float(string="Quantity", required=True, default=1)
    rules_detail_ids = fields.One2many(comodel_name="rdm.rules.detail", inverse_name="rules_id", string="Detail")
    

class rdm_rules_detail(models.Model):
    _name = "rdm.rules.detail"
    _rec_name = "rules_id"
    _description = "Redemption Rules Detail"

    rules_id = fields.Many2one(comodel_name="rdm.rules", string="Rules")
    rule_schema = fields.Selection(selection=SCHEMAS_SelectionS, string="Schema", required=True)
    operation = fields.Selection(selection=OPERATION_SelectionS, string="Operation", required=True, default="and")
    day = fields.Date(string="Day")
    day_name = fields.Selection(selection=DAY_NAME_SelectionS, string="Day Name")
    ethnic_ids = fields.One2many(comodel_name="rdm.rules.ethnic", inverse_name="rules_detail_id", string="Ethnic")
    religion_ids = fields.One2many(comodel_name="rdm.rules.religion", inverse_name="rules_detail_id", string="Religion")
    marital_ids = fields.One2many(comodel_name="rdm.rules.marital", inverse_name="rules_detail_id", string="Marital")
    zone_ids = fields.One2many(comodel_name="rdm.rules.zone", inverse_name="rules_detail_id", string="Zone")
    education_ids = fields.One2many(comodel_name="rdm.rules.education", inverse_name="rules_detail_id", string="Education")
    interest_ids = fields.One2many(comodel_name="rdm.rules.interest", inverse_name="rules_detail_id", string="Interest")
    occupation_ids = fields.One2many(comodel_name="rdm.rules.occupation", inverse_name="rules_detail_id", string="Occupation")
    card_type_ids = fields.One2many(comodel_name="rdm.rules.card.type", inverse_name="rules_detail_id", string="Card Type")
    tenant_ids = fields.One2many(comodel_name="rdm.rules.tenant", inverse_name="rules_detail_id", string="Tenant")
    tenant_category_ids = fields.One2many(comodel_name="rdm.rules.tenant.category", inverse_name="rules_detail_id", string="Tenant Category")
    participant_ids = fields.One2many(comodel_name="rdm.rules.participant", inverse_name="rules_detail_id", string="Participant")
    bank_ids = fields.One2many(comodel_name="rdm.rules.bank", inverse_name="rules_detail_id", string="Bank")
    bank_card_ids = fields.One2many(comodel_name="rdm.rules.bank.card", inverse_name="rules_detail_id", string="Bank Card")
    age_ids = fields.One2many(comodel_name="rdm.rules.customer.age", inverse_name="rules_detail_id", string="Age")
    spending_amount_ids = fields.One2many(comodel_name="rdm.rules.spending.amount", inverse_name="rules_detail_id", string="Spending Amount")
    gender_ids = fields.One2many(comodel_name="rdm.rules.gender", inverse_name="rules_detail_id", string="Gender")
    cash_ids = fields.One2many(comodel_name="rdm.rules.cash", inverse_name="rules_detail_id", string="Cash")


class rdm_rules_ethnic(models.Model):
    _name = "rdm.rules.ethnic"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Ethnic"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail", string="Rules ID", required=False, readonly=True)
    ethnic_id = fields.Many2one(comodel_name="rdm.customer.ethnic", string="Ethnic", required=False, )

class rdm_rules_religion(models.Model):
    _name = "rdm.rules.religion"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Religion"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    religion_id = fields.Many2one(comodel_name="rdm.customer.religion",string="Religion")

class rdm_rules_marital(models.Model):
    _name = "rdm.rules.marital"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Marital"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    marital_id = fields.Many2one(comodel_name="rdm.customer.marital",string="Marital")

class rdm_rules_zone(models.Model):
    _name = "rdm.rules.zone"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Zone"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    zone_id = fields.Many2one(comodel_name="rdm.customer.zone",string="Zone")

class rdm_rules_education(models.Model):
    _name = "rdm.rules.education"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Education"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    education_id = fields.Many2one(comodel_name="rdm.customer.education",string="Education")

class rdm_rules_interest(models.Model):
    _name = "rdm.rules.interest"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Interest"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    interest_id = fields.Many2one(comodel_name="rdm.customer.interest",string="Interest")

class rdm_rules_occupation(models.Model):
    _name = "rdm.rules.occupation"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Occupation"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    occupation_id = fields.Many2one(comodel_name="rdm.customer.occupation",string="Occupation")

class rdm_rules_gender(models.Model):
    _name = "rdm.rules.gender"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Gender"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    gender_id = fields.Many2one(comodel_name="rdm.customer.gender",string="Gender")

class rdm_rules_participant(models.Model):
    _name = "rdm.rules.participant"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Tenant Participant Type"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    participant_id = fields.Selection(selection=AVAILABLE_PARTICIPANT,string="Participant Type",required=True)

class rdm_rules_card_type(models.Model):
    _name = "rdm.rules.card.type"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Card Type"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    card_type_id = fields.Many2one(comodel_name="rdm.card.type",string="Card Type")

class rdm_rules_tenant(models.Model):
    _name = "rdm.rules.tenant"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Tenant"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    tenant_id = fields.Many2one(comodel_name="rdm.tenant",string="Tenant")

class rdm_rules_customer_age(models.Model):
    _name = "rdm.rules.customer.age"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rules Customer Age"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    operator = fields.Selection(selection=OPERATOR_SelectionS,string="Operator",size=16,required=True)
    value1 = fields.Integer("Value 01")
    value2 = fields.Integer("Value 02")

class rdm_rules_spending_amount(models.Model):
    _name = "rdm.rules.spending.amount"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rules Spending Amount"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    operator = fields.Selection(selection=OPERATOR_SelectionS,string="Operator",size=16,required=True)
    value1 = fields.Float(string="Value 01")
    value2 = fields.Float(string="Value 02")

class rdm_rules_tenant_category(models.Model):
    _name = "rdm.rules.tenant.category"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Tenant Category"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    tenant_category_id = fields.Many2one(comodel_name="rdm.tenant.category",string="Tenant Category")

class rdm_rules_bank(models.Model):
    _name = "rdm.rules.bank"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Bank"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    bank_id = fields.Many2one(comodel_name="rdm.bank",string="Bank")

class rdm_rules_bank_card(models.Model):
    _name = "rdm.rules.bank.card"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Bank Card"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    bank_card_id = fields.Many2one(comodel_name="rdm.bank.card",string="Bank Card")

class rdm_rules_cash(models.Model):
    _name = "rdm.rules.cash"
    _rec_name = "rules_detail_id"
    _description = "Redemption Rule Cash"

    rules_detail_id = fields.Many2one(comodel_name="rdm.rules.detail",string="Rules ID", readonly=True)
    bank_id = fields.Many2one(comodel_name="rdm.bank",string="Exclude Bank")

