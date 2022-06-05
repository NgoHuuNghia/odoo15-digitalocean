# -*- coding: utf-8 -*-
#? either you import all of odoo's base module like 1 line bellow
# from odoo import modules, api, fields
# and use their method with a dot (modules.Model)
#? or do the it the modern way specifically import them
from odoo import _
from odoo.exceptions import ValidationError
from odoo.models import Model
from odoo.api import depends, model, constrains, ondelete
from odoo.fields import Char, Integer, One2many, Selection, Boolean, Date, Image, Many2many
from dateutil import relativedelta
class HospitalPatient(Model):
  #? main name for this Module (you can check them in the setting of debug options)
  _name = 'hospital.patient'
  #? inherit modules's method from here as a list (remember to depend them on __manifest__.py also)
  _inherit = ['mail.thread', 'mail.activity.mixin']
  _description = 'Hospital Patient'

  #$ yes all inherited odoo's base methods are placed before field declarations
  #? here is how to inherit the odoo's method to create a new module, allowing us to manipulate the created record 
  @model
  def create(self, vals_list):
    vals_list['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
    return super(HospitalPatient, self).create(vals_list)

  #? for the write/update method a decorator is unnecessary
  def write(self, vals):
    if not self.ref and not vals.get('ref'):
      vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
    return super(HospitalPatient, self).write(vals)

  #? with this inherited odoo's method we can get and manipulate the rec_name
  def name_get(self):
    return [(record.id, "[%s] %s" % (record.ref, record.name)) for record in self]

  #? this block of varibles are the fields of the Module which odoo will convert for us, we just need to declare it
  #* string parameter is the UI's name of the field
  #* tracking parameter will let the chatter to track this field changes
  name = Char(string='Name', tracking=True)
  #* default parameter will set a default value for this field when creating a new one
  ref = Char(string='Reference', default='UNKNOWN', tracking=True)
  date_of_birth = Date(string='Date Of Birth')
  #* give the compute parameter a function and it will run when new data is created, also make the field readonly
  #* you can change the default readonly to True to change this field if you want to
  #*108* with the inverse parameter we can make this compute field editable, but for it to also reflect it's changes inversely to the
  #*108* depended field, in this case [date_of_birth]. Simply add the inverse functions as value and declare the functionality in this model
  #*109* provide a [search] parameter with a search function to enable search function of a non-stored field like computed one
  age = Integer(string='Age', compute='_compute_age', inverse='_inverse_compute_age', search='_search_age') 
  #* with selection you need to provide the first argument as a list with tuples of the label and value of your selections
  gender = Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
  active = Boolean(string='active', default=True)
  #* with the Image method we can add images file to the view using the image widget
  image = Image(string="Image")
  #* Many2many method to create free relations between models, basically creating a intermediary table
  #* it is recommended to provide all the arguments such as [relation] for the table name and the 2 columns label
  tag_ids = Many2many(comodel_name='hospital.patient.tag', relation="hospital_patient_tag_ids_rel", column1="patient_id", column2="tag_id", string='Tags')
  #*95* since compute fields won't be store on the database, use the store parameter to make it so
  appointment_count = Integer(string="Appointment Count", compute=("_compute_appointment_count"), store=True)
  #*95* with the One2many field we can specify 
  appointment_ids = One2many(comodel_name='hospital.appointment', inverse_name='patient_id', string="Appointments")
  #*98* these 3 fields bellow is used for learning how to hide fields in views base on conditions
  parent = Char(string='Parent')
  marital_status = Selection(selection=[
    ('married', 'Married'),
    ('single', 'Single'),
  ], string='Marital Status', tracking=True)
  partner_name = Char(string='Partner\'s Name')
  #*122* to enable the birthday alert create this Boolean field and let compute decide when today is equal to their birthday
  is_birthday = Boolean(string='Birthday?', compute="_compute_is_birthday")
  phone = Char(string="Phone")
  email = Char(string="Email")
  website = Char(string="Website")

  #?92? Other than using the sql constraints, we can use the odoo's constrains decorator and python to apply the same logic
  @constrains('date_of_birth')
  def _check_date_of_birth(self):
    for record in self:
      if record.date_of_birth and record.date_of_birth > Date.today():
        raise ValidationError("Date of birth cannot be in the future")

  #?104? ondelete decorator, to stop and raise a warning if a patient is delete while one2many model is still active
  #? pretty much the decorator way to to use the [ondelete='restrict'] in the depended instead of the related model
  #? [at_uninstall] parameter will determine if this function be executed when uninstalling this module
  @ondelete(at_uninstall=False)
  def _check_appointments(self):
    for record in self:
      if record.appointment_ids:
        raise ValidationError("Cannot delete a patient with active appointments")

  #? this depend is a decorator to run the function bellow when a 
  #? field inside of it changed (remember to add @ at the start [@api.depends('')] or [@depends('')])
  @depends('date_of_birth')
  #? this self argument of this function is the Module itself more or less for us to access
  def _compute_age(self):
    #? we have to iterate through the self since it is a collections of field's data of each of the object/user
    #? if we don't it will return us a singleton error in which i still have no idea what it is
    for rec in self:
      #* just the date method from datatime package to get the current date
      today = Date.today()
      if rec.date_of_birth:
        rec.age = today.year - rec.date_of_birth.year
      else:
        #* if we don't have a default value there will be errors
        rec.age = 0

  #?108? the inverse function is define here, also remember to add the depends decorator
  @depends('age')
  def _inverse_compute_age(self):
    # today = Date.today()
    for record in self:
      #? use relativedelta from dateutil package to calculate for us the date base on the age's integer (you can also add months and days too btw)
      record.date_of_birth = Date.today() - relativedelta.relativedelta(years=record.age)

  #?109? the search function will need 3 arguments (value is the value entered by the user in search view)
  #? the self here doesn't contain any record fyi, since age is not stored this is a realistic way of searching it
  def _search_age(self, operator, value):
    date_of_birth = Date.today() - relativedelta.relativedelta(years=value)
    start_of_year = date_of_birth.replace(day=1,month=1)
    end_of_year = date_of_birth.replace(day=31,month=12)
    return [('date_of_birth', '>=', start_of_year),('date_of_birth', '<=', end_of_year)]

  #?95? as we know a compute field won't be store in the database, here how we can store it
  #? it is also import to have the decorator depends to make sure the _compute is run everytime there a new appointment
  @depends('appointment_ids')
  def _compute_appointment_count(self):
    #? the [search_count] is an ORM method that allow count a given domain using a condition
    # for record in self:
      # record.appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', record.id)])
    #? another way of getting [appointment_count] is using [read_group] method instead with 3 parameters
    #? (domain, fields, group by) all in a list, with this method we can more fine tune that data and domain behavior we need
    appointment_group = self.env['hospital.appointment'].read_group(
      #? with [domain] parameter we can specify which group with which condition that will be read
      domain=[],
      fields=['patient_id'],
      groupby=['patient_id']
    )
    
    #? [appointment_group] will return a list of dictionary containing the counts of all the appointments that is in many2one relation with [patient_id]
    for appointment in appointment_group:
      #$ example of one of the dictionary from read_group
      #$ {'patient_id_count': 4, 'patient_id': (1, <odoo.tools.func.lazy object at 0x000002904A573D80>), '__domain': [('patient_id', '=', 1)]}
      patient_id = appointment.get('patient_id')[0]
      patient_record = self.browse(patient_id)
      patient_record.appointment_count = appointment['patient_id_count']
      #? to ensure that newly created patient will have at least 0 appointment_count the record set need extract them from removing ones with values
      self -= patient_record
    #? give the newly created patient a value to avoid server error
    self.appointment_count = 0

  #?122? here is the compute function for the is_birthday
  @depends('date_of_birth')
  def _compute_is_birthday(self):
    for record in self:
      #? check if [date_of_birth] exist yet, important for newly created patient to avoid server error 
      if record.date_of_birth:  
        if Date.today().day == record.date_of_birth.day and Date.today().month == record.date_of_birth.month:
          record.is_birthday = True
        else: record.is_birthday = False
      else: record.is_birthday = False

  #?105? the action in group by list need to be added in it's core module
  def action_test(self):
    print('BUTTON CLICKED', self)
    return

  #?129? the return contain the actions properties in a dictionary
  #? with [context] and [domain] properties determine the returned records
  def action_view_appointments(self):
    return {
        'name': _('Appointments'),
        'res_model': 'hospital.appointment',
        'view_mode': 'list,form',
        'context': {'default_patient_id':self.id},
        'domain': [('patient_id','=',self.id)],
        'target': 'current',
        'type': 'ir.actions.act_window',
    }