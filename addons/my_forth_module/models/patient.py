# -*- coding: utf-8 -*-
#? either you import all of odoo's base module like 1 line bellow
# from odoo import modules, api, fields
# and use their method with a dot (modules.Model)
#? or do the it the modern way specifically import them
from odoo.models import Model
from odoo.api import depends
from odoo.fields import Char, Integer, Selection, Boolean, Date, Many2one

from datetime import date
class HospitalPatient(Model):
  #? main name for this Module (you can check them in the setting of debug options)
  _name = 'hospital.patient'
  #? inherit modules's method from here as a list (remember to depend them on __manifest__.py also)
  _inherit = ['mail.thread', 'mail.activity.mixin']
  _description = 'Hospital Patient'

  #? this block of varibles are the fields of the Module which odoo will convert for us, we just need to declare it
  #* string parameter is the UI's name of the field
  #* tracking parameter will let the chatter to track this field changes
  name = Char(string='Name', tracking=True)
  #* default parameter will set a default value for this field when creating a new one
  ref = Char(string='Reference', default='UNKNOWN', tracking=True)
  date_of_birth = Date(string='Date Of Birth')
  #* give the compute parameter a function and it will run when new data is created, also make the field readonly
  #* you can change the default readonly to True to change this field if you want to
  age = Integer(string='Age', compute='_compute_age') 
  #* with selection you need to prevoide the first argument as a list with tuples of the label and value of your selections
  gender = Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
  active = Boolean(string='active', default=True)
  # appointment_id = Many2one(comodel_name='hospital.appointment', string="Appointments")

  #? this depend is a decorator to run the function bellow when a 
  #? field inside of it changed (remember to add @ at the start [@api.depends('')] or [@depends('')])
  @depends('date_of_birth')
  #? this self argument of this function is the Module itself more or less for us to access
  def _compute_age(self):
    # compute an age with inputed date of birth from this module

    #? we have to iterate through the self since it is a collections of field's data of each of the object/user
    #? if we don't it will return us a singleton error in which i still have no idea what it is
    for rec in self:
      #* just the date method from datatime package to get the current date
      today = date.today()
      if rec.date_of_birth:
        rec.age = today.year - rec.date_of_birth.year
      else:
        #* if we don't have a default value there will be errors
        rec.age = 0