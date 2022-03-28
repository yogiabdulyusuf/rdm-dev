from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, Warning
import logging
import re
import logging
import string
import random
import uuid
import os
import hashlib

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [
    ("draft","New"),    
    ("active","Active"),    
    ("blacklist","Black List"),    
    ("disable", "Disable"),
]

CONTACT_TYPES = [
    ("customer","Customer"),
    ("tenant","Tenant"),
    ("both","Customer or Tenant"),    
]


class rdm_customer(models.Model):
    _name = "rdm.customer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    _description = "Redemption Customer"

    @api.one
    def set_black_list(self):
        _logger.info("Blacklist ID : " + str(self.id))
        self.state = "blacklist"

    @api.one
    def set_remove_black_list(self):
        _logger.info("Reset Blacklist ID : " + str(self.id))
        self.state = "active"

    @api.one
    def set_disable(self):
        _logger.info("Activate ID : " + str(self.id))
        self.state = "disable"

    @api.one
    def set_enable(self):
        _logger.info("Reset activate ID : " + str(self.id))
        self.state = "active"


    @api.multi
    def change_password(self):  # CHANGE
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Password',
            'res_model': 'rdm.customer.change.password',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('view_wizard_change_password', False),
            'target': 'new',
        }


    @api.one
    def _request_forget_password(self):
        _logger.info("Start Request Forget Password Process")
        vals = {}
        vals.update({"request_change_password": True})
        vals.update({"request_change_password_passcode": str(uuid.uuid1()).replace("-","")})
        result = super(rdm_customer, self).write(vals)
        if result:
            self._send_request_reset_password_notification()
        _logger.info("End Request Forget Password Process")

    @api.one
    def _forget_password(self):
        _logger.info("Start Forget Password Process")

        enable_email_config_ids = self.env.user.company_id.enable_email
        receive_email_config_ids = self.env.user.company_id.receive_email

        if not enable_email_config_ids:
            raise ValidationError(("Warning"), ("Customer cannot Receive Email"))

        if not receive_email_config_ids:
            raise ValidationError("Customer cannot Receive Email")

        new_password = self._password_generator()
        vals = {}
        vals.update({"password": new_password})
        vals.update({"request_change_password": False})
        result = self.env['rdm.customer'].write(vals)
        if result:
            self._send_reset_password_notification()
            _logger.info("Send Change Password Email Notification")
        _logger.info("End Forget Password Process")

    @api.one
    def _add_re_registration_point(self):
        _logger.info("Start Add Re-registration Point")

        re_registration_point_config_ids = self.env.user.company_id.re_registration_point
        re_registration_expired_duration_config_ids = self.env.user.company_id.re_registration_expired_duration

        vals = {}
        vals.update({"customer_id": self.id})
        vals.update({"trans_type": "member"})
        vals.update({"point": re_registration_point_config_ids})
        expired_date = datetime.today() + timedelta(re_registration_expired_duration_config_ids)
        vals.update({"expired_date": expired_date.strftime("%Y-%m-%d")})
        self.env['rdm.customer.point'].create(vals)
        _logger.info("End Add Re-registration Point")

    @api.one
    def re_registration_customer(self):
        _logger.info("Start Re-registration Process")

        enable_re_registration_config_ids = self.env.user.company_id.enable_re_registration
        enable_email_config_ids = self.env.user.company_id.enable_email

        #Re-registration Validation
        if not enable_re_registration_config_ids:
            raise ValidationError("Customer Re-registration not enable")
        if self.re_registration:
            raise ValidationError("Customer already re-registration")
        if not self.email_required:
            raise ValidationError("Customer Email Required")
        if not self.receive_email:
            raise ValidationError("Customer cannot Receive Email")

        #Generate Password
        new_password = self._password_generator()
        self.password = new_password

        #Close Re-registration
        self._close_re_registration()
        self._add_re_registration_point()

        if enable_email_config_ids:
            #Send Re-registration Email Notification
            self._send_re_registration_email_notification()

        _logger.info("End Re-registration Process")

    @api.one
    def _close_re_registration(self):
        _logger.info("Start Close Re-registration")
        self.re_registration = True
        _logger.info("End Close Re-registration")

    @api.one
    def reset_password(self):    # CHANGE
        enable_email_config_ids = self.env.user.company_id.enable_email

        if not enable_email_config_ids:
            raise ValidationError("Customer cannot Receive Email")
        if not self.receive_email:
            raise ValidationError("Customer cannot Receive Email")

        gen_pass = self._password_generator()
        self.password = gen_pass   # CHANGE
        self._send_reset_password_notification()
        _logger.info("Send Change Password Email Notification")

    def _password_generator(self):
        # Generate Password
        size = 10
        chars= string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for _ in range(size))

    @api.one
    def _send_reset_password_notification(self):
        _logger.info("Start Send Reset Password Notification")

        args = [('name', '=', 'RDM Reset Password')]  # CHANGE
        template_ids = self.env['mail.template'].search(args)
        vals = {}
        vals.update({'email_to': self.email})
        template_ids.write(vals)
        template_ids[0].sudo().send_mail(self.id, force_send=True)

        _logger.info("Start End Reset Password Notification")

    def _add_new_member_point(self):
        _logger.info("Start Add New Member Point")
        # rdm_customer_config = self.env("rdm.customer.config")
        # CHANGE
        new_member_point_config_ids = self.env.user.company_id.new_member_point
        new_member_expired_duration_config_ids = self.env.user.company_id.new_member_expired_duration

        vals = {}
        vals.update({"customer_id": self.id})
        vals.update({"trans_type": "member"})
        vals.update({"point": new_member_point_config_ids})
        expired_date = datetime.today() + timedelta(new_member_expired_duration_config_ids)
        vals.update({"expired_date": expired_date.strftime("%Y-%m-%d")})
        self.env['rdm.customer.point'].create(vals)
        _logger.info("End Add New Member Point")

    @api.one
    def _add_referal_point(self):
        _logger.info("Start Add Referal Point")
        referal_point_config_ids = self.env.user.company_id.referal_point
        expired_duration_config_ids = self.env.user.company_id.expired_duration

        vals = {}
        vals.update({"customer_id": self.ref_id.id})
        vals.update({"trans_type": "reference"})
        vals.update({"point": referal_point_config_ids})
        expired_date = datetime.today() + timedelta(expired_duration_config_ids)
        vals.update({"expired_date": expired_date.strftime("%Y-%m-%d")})
        self.env['rdm.customer.point'].create(vals)
        _logger.info("End Add Referal Point")

    @api.one
    def _new_member_process(self):
        _logger.info("Start New Member Process : " + str(self.id))

        # rdm_config = self.env("rdm.config")
        # customer_config = self.env("rdm.customer.config")
        enable_new_member_config_ids = self.env.user.company_id.enable_new_member
        enable_email_config_ids = self.env.user.company_id.enable_email

        if enable_new_member_config_ids:

            if self.email_required and self.receive_email:
                self._add_new_member_point()

            #Send Email
            if self.email_required and self.receive_email and enable_email_config_ids:
                _logger.info("Send Email New Member")
                args = [('name', '=', 'New Customer Notification')]  # CHANGE
                template_ids = self.env['mail.template'].search(args)
                vals = {}
                vals.update({'email_to': self.email})
                template_ids.write(vals)
                template_ids[0].sudo().send_mail(self.id, force_send=True)
        _logger.info("End New Member Process")

    @api.one
    def _referal_process(self):
        _logger.info("Start Referal Process : " + str(self.id))

        # rdm_config = self.env("rdm.config")
        # customer_config = self.env("rdm.customer.config")
        enable_referal_config_ids = self.env.user.company_id.enable_referal
        enable_email_config_ids = self.env.user.company_id.enable_email

        if enable_referal_config_ids:
            if self.ref_id:
                if self.ref_id.email_required and self.ref_id.receive_email:
                    self._add_referal_point()

                #Send Email
                if self.ref_id.email_required and self.ref_id.receive_email and enable_email_config_ids:
                    _logger.info("Send Email Referal")

                    args = [('name', '=', 'Referral Notification')]  # CHANGE
                    template_ids = self.env['mail.template'].search(args)
                    vals = {}
                    vals.update({'email_to': self.email})
                    template_ids.write(vals)
                    template_ids[0].sudo().send_mail(self.id, force_send=True)
            else:
                _logger.info("No Referal Point")
        return True

    def _check_duplicate(self, vals):
        _logger.info("Start Check Duplicate")
        # customer_config = self.env["rdm.customer.config"]
        # Check Email Address
        duplicate_email_config_ids = self.env.user.company_id.duplicate_email
        duplicate_social_config_ids = self.env.user.company_id.duplicate_social_id

        if duplicate_email_config_ids:
            if self.email_required:
                if "customer_id" in vals.keys():
                    #Update Transaction
                    customer_ids = self.env['rdm.customer'].search([("email","=",self.email),("id","!=",self.id)])
                else:
                    #Create Transaction
                    customer_ids = self.env['rdm.customer'].search([('email','=',self.email)])

                if customer_ids:
                    # customer = customer_ids[0]
                    _logger.info("End Check Duplicate")
                    return True #,"Email Duplicate with " + customer.name

        #Check Social ID
        if duplicate_social_config_ids:
            customer_ids = self.env['rdm.customer'].search([('social_id', '=', self.social_id), ("id","!=",self.id)])
            if customer_ids:
                # customer = customer_ids[0]
                _logger.info("End Check Duplicate")
                return True #,"Social ID Duplicate with " + customer.name

        #check AYC Number
        if self.ayc_number:
            customer_ids = self.env['rdm.customer'].search([("ayc_number","=",self.ayc_number), ("id","!=",self.id)])
            if customer_ids:
                # customer = customer_ids[0]
                _logger.info("End Check Duplicate")
                return True #,"Duplicate AYC Number with " + customer.name

        _logger.info("End Check Duplicate")
        return False
    #
    # @api.one
    # def onchange_email_required(self):
    #     if not self.email_required:
    #         return {"value":{"email_required":""}}
    #
    # @api.one
    # def onchange_mobil_phone1_number(self):
    #     if not self.mobile_phone1:
    #         return {"value":{}}
    #     return {"value":{"mobile_phone1": self.mobile_phone1}}
    #
    # @api.one
    # def onchange_mobile_phone2_number(self):
    #     if not self.mobile_phone2:
    #         return {"value":{}}
    #     return {"value":{"mobile_phone2": self.mobile_phone2}}
    #
    # @api.one
    # def _send_email_notification(self):
    #     _logger.info("Start Send Email Notification")
    #     mail_mail = self.env("mail.mail")
    #     mail_ids = []
    #     mail_ids.append(mail_mail.create( {
    #         "email_from": self.email_from,
    #         "email_to": self.email_to,
    #         "subject": self.subject,
    #         "body_html": self.body_html,
    #         }))
    #     mail_mail.send( mail_ids)
    #     _logger.info("End Send Email Notification")
    #
    @api.one
    def send_create_email_notification(self):
        receive_email_config_ids = self.env.user.company_id.receive_email
        enable_email_config_ids = self.env.user.company_id.enable_email
        enable_new_member_config_ids = self.env.user.company_id.enable_new_member
        enable_referal_config_ids = self.env.user.company_id.enable_referal

        if enable_email_config_ids and receive_email_config_ids:
            # rdm_customer_config = self.env['rdm.customer.config")
            if enable_new_member_config_ids:
                self.send_mail_to_new_customer()
            if enable_referal_config_ids:
                self.send_mail_to_referal_customer()

    @api.one
    def _send_re_registration_email_notification(self):
        _logger.info("Start Send Re-registraton Email Notification")
        # rdm_customer_config = self.env("rdm.customer.config")
        # email_obj = self.env("email.template")

        args = [('name', '=', 'New Customer Notification')]  # CHANGE
        template_ids = self.env['mail.template'].search(args)
        vals = {}
        vals.update({'email_to': self.email})
        template_ids.write(vals)
        template_ids[0].sudo().send_mail(self.id, force_send=True)
        _logger.info("End Send Re-registraton Email Notification")

    @api.one
    def _send_request_reset_password_notification(self):
        _logger.info("Start Send Request Reset Password Notification")

        # rdm_customer_config = self.env("rdm.customer.config")
        # email_obj = self.env("email.template")

        args = [('name', '=', 'Request Change Password')]  # CHANGE
        template_ids = self.env['mail.template'].search(args)
        vals = {}
        vals.update({'email_to': self.email})
        template_ids.write(vals)
        template_ids[0].sudo().send_mail(self.id, force_send=True)

        _logger.info("End Send Request Reset Password Notification")

                        
    type = fields.Many2one(comodel_name="rdm.customer.type", string="Type")
    image = fields.Binary(string='Image')
    barcode = fields.Char(string='Barcode')
    code_otp = fields.Char(string="OTP", size=4, required=False, )
    contact_type = fields.Selection(selection=CONTACT_TYPES, string="Contact Type", size=16, default="customer")
    old_ayc_number = fields.Char(string="Old AYC #", size=50, track_visibility='onchange')
    ayc_number = fields.Char(string="AYC #", size=50, required=False, track_visibility='onchange')
    name = fields.Char(string="Name", size=200, required=True, track_visibility='onchange')
    title = fields.Many2one(comodel_name="rdm.tenant.title", string="Title")
    birth_place = fields.Char(comodel_name="Birth Place", size=100, track_visibility='onchange')
    birth_date = fields.Date(comodel_name="Birth Date", required=False, track_visibility='onchange')
    gender = fields.Many2one(comodel_name="rdm.customer.gender", string="Gender", required=False, track_visibility='onchange')
    ethnic = fields.Many2one(comodel_name="rdm.customer.ethnic", string="Ethnic", track_visibility='onchange')
    religion = fields.Many2one(comodel_name="rdm.customer.religion", string="Religion", track_visibility='onchange')
    marital = fields.Many2one(comodel_name="rdm.customer.marital", string="Marital", track_visibility='onchange')
    social_id = fields.Char(string="ID or Passport", size=50, required=False, track_visibility='onchange')
    address = fields.Text(string="Address", track_visibility='onchange')
    province = fields.Many2one(comodel_name="rdm.province", string="Province", track_visibility='onchange')
    city = fields.Many2one("rdm.city","City", track_visibility='onchange')
    zipcode = fields.Char(string="Zipcode", size=10, track_visibility='onchange')
    phone1 = fields.Char(string="Phone 1", size=20, widget="phone", track_visibility='onchange')
    phone2 = fields.Char(string="Phone 2", size=20, track_visibility='onchange')
    mobile_phone1 = fields.Char(string="Mobile Phone 1", size=20, required=True, track_visibility='onchange')
    mobile_phone2 = fields.Char(string="Mobile Phone 2", size=20, track_visibility='onchange')
    email = fields.Char(string="Email", required=False, widget="email", track_visibility='onchange')
    email_required = fields.Boolean(string="Email Required", default=True, track_visibility='onchange')
    password = fields.Char(string="Password",size=20, track_visibility='onchange')
    customer_token =  fields.Char(string="Token", size=255, track_visibility='onchange')
    request_change_password = fields.Boolean(string="Request Change Password", default=False, track_visibility='onchange')
    request_change_password_passcode = fields.Char(string="Passcode", size=50, track_visibility='onchange')
    request_change_password_expired = fields.Datetime(string="Passcode Expired Time", track_visibility='onchange')
    request_change_password_times = fields.Integer(string="Request Change Passwosrd Times", default=0, track_visibility='onchange')
    zone = fields.Many2one(comodel_name="rdm.customer.zone",string="Residential Zone", track_visibility='onchange')
    occupation = fields.Many2one(comodel_name="rdm.customer.occupation",string="Occupation", track_visibility='onchange')
    education = fields.Many2one(comodel_name="rdm.customer.education", string="Education", track_visibility='onchange')
    card_type = fields.Many2one(comodel_name="rdm.card.type", string="Card Type", track_visibility='onchange')
    interest = fields.Many2one(comodel_name="rdm.customer.interest", string="Interest", track_visibility='onchange')
    ref_id = fields.Many2one(comodel_name="rdm.customer", string="Refferal", track_visibility='onchange')
    receive_email = fields.Boolean(string="Receive Email",track_visibility='onchange')
    join_date = fields.Date(string="Join Date", default=fields.Date.today(), track_visibility='onchange')
    re_registation = fields.Boolean(string="Re-registration", default=False, track_visibility='onchange')
    re_registration = fields.Boolean(string="Re-registration", readonly=True, track_visibility='onchange')
    state = fields.Selection(selection=AVAILABLE_STATES, string="Status", size=16, readonly=True, default="draft", track_visibility='onchange')
    deleted = fields.Boolean(string="Deleted",readonly=True, default=False)
    active = fields.Boolean(default=True)
    create_uid = fields.Many2one(comodel_name="res.users",string="Created By", readonly=True)
    create_date = fields.Datetime(string="Date Created", readonly=True)
    write_uid = fields.Many2one(comodel_name="res.users", string="Modified By", readonly=True)
    write_date = fields.Datetime(string="Date Modified", readonly=True)
    otp_code_ids = fields.One2many(comodel_name="rdm.customer.otp", inverse_name="rdm_customer_id", string="OTP Code", required=False, )
    notif_ids = fields.One2many(comodel_name="rdm.customer.notif", inverse_name="rdm_customer_id", string="Notification", required=False, )

    _sql_constraints = [('email_unique', 'CHECK(1=1)', 'Email already exists.'),
                        ('social_id_unique', 'CHECK(1=1)', 'KTP already exists.'),
                        ('mobile_phone1', 'CHECK(1=1)', 'Mobile phone already exists.'),]

    # ('email_unique', 'unique(email)', 'Email already exists.'),
    # ('social_id_unique', 'unique(social_id)', 'KTP already exists.'),
    # ('mobile_phone1', 'unique(mobile_phone1)', 'Mobile phone already exists.'),

    @api.model
    def create(self, vals):
        vals['state'] = "active"

        if "email_required" in vals.keys() and "receive_email" in vals.keys():
            if vals['email_required'] and vals['receive_email']:
                vals.update({"re_registration": True})

        #Upper Case Name
        if "name" in vals.keys():
            name = vals['name']
            vals.update({"name":name.upper()})

        # if vals['contact_type'] == "tenant":
        #     if "tenant_id" in vals.keys():
        #         vals.update({"contact_type": "tenant"})

        #Lower Case Email
        if "email" in vals.keys():
            email = vals['email']
            if email:
                vals.update({"email":email.lower()})


        #Mobile Phone 1
        if "mobile_phone1" in vals.keys():
            mobile_phone1 = vals['mobile_phone1']
            if mobile_phone1:
                if mobile_phone1[0:2] == "62":
                    vals.update({"mobile_phone1": mobile_phone1})
                elif mobile_phone1[0] == "0":
                    mobile_phone1 = "62" + mobile_phone1[1:len(mobile_phone1)-1]
                    vals.update({"mobile_phone1": mobile_phone1})
                else:
                    raise ValidationError("Mobile Phone 1 format should be start with 62 or 0")

        #Mobile Phone 1
        if "mobile_phone2" in vals.keys():
            mobile_phone2 = vals['mobile_phone2']
            if mobile_phone2:
                if mobile_phone2[0:2] == "62":
                    vals.update({"mobile_phone2":mobile_phone2})
                elif mobile_phone2[0] == "0":
                    mobile_phone2 = "62" + mobile_phone2[1:len(mobile_phone2)-1]
                    vals.update({"mobile_phone2": mobile_phone2})
                else:
                    raise ValidationError("Mobile Phone 2 format should be start with 62 or 0")

        # Generate Password
        gen_pass = self._password_generator()
        vals.update({"password": gen_pass})
        
        # Generate Customer Token
        rbytes = os.urandom(40)
        vals.update({"customer_token": str(hashlib.sha1(rbytes).hexdigest())})
        
        # Checks Duplicate Customer
        # is_duplicate = self._check_duplicate(vals)

        # Create Customer
        id =  super(rdm_customer, self).create(vals)

        # Enable Customer
        id.set_enable()
        # Process New Member and Generate Point if Enable
        id._new_member_process()
        # Process Referal and Generate Point For Reference Customer If Enable
        id._referal_process()

        #Send Email Notification for Congrat and Customer Web Access Password
        #self.send_create_email_notification( [id])

        return id

    @api.multi
    def write(self, vals):

        if "state" in vals.keys():
            state = vals.get('state')
            #Request Change Password
            if state == "request_change_password":
                self._request_forget_password()
                return True
            if state == "reset_password":
                self._forget_password()
                return True

        #Upper Case Name
        if "name" in vals.keys():
            name = vals.get('name')
            vals.update({"name": name.upper()})
        # if self.name:
        #     vals['name'] = self.name.upper()

        #Lower Case Email
        if "email" in vals.keys():
            email = vals.get('email')
            if email:
                vals.update({"email_required": True})
                vals.update({"email":email.lower()})

        # Mobile Phone 1
        if "mobile_phone1" in vals.keys():
            mobile_phone1 = vals.get('mobile_phone1')
            if mobile_phone1:
                if mobile_phone1[0:2] == "62":
                    vals.update({"mobile_phone1": mobile_phone1})
                elif mobile_phone1[0] == "0":
                    mobile_phone1 = "62" + mobile_phone1[1:len(mobile_phone1) - 1]
                    vals.update({"mobile_phone1": mobile_phone1})
                else:
                    raise ValidationError("Mobile Phone 1 format should be start with 62 or 0")

        # Mobile Phone 1
        if "mobile_phone2" in vals.keys():
            mobile_phone2 = vals.get('mobile_phone2')
            if mobile_phone2:
                if mobile_phone2[0:2] == "62":
                    vals.update({"mobile_phone2": mobile_phone2})
                elif mobile_phone2[0] == "0":
                    mobile_phone2 = "62" + mobile_phone2[1:len(mobile_phone2) - 1]
                    vals.update({"mobile_phone2": mobile_phone2})
                else:
                    raise ValidationError("Mobile Phone 2 format should be start with 62 or 0")

        # vals.update({"customer_id": self.id})
        is_duplicate = self._check_duplicate(vals)

        _logger.info("Check Log Duplicate")
        _logger.info(is_duplicate)

        if is_duplicate == True:
            raise ValidationError("Error Write")
        else:
            res = super(rdm_customer, self).write(vals)
            return res

