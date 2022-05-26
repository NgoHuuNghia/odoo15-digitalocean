# -*- coding: utf-8 -*-
from email.policy import default
from xmlrpc.client import Boolean
from odoo.models import Model
from odoo.fields import Char, Integer, Selection, Boolean

print("hello")

class HospitalPatient(Model):
  _name = "hospital.patient"
  _inherit = "mail.thread"
  _description = "Hospital Patient"

  name = Char(string="Name")
  ref = Char(string="Reference")
  age = Integer(string="Age") 
  gender = Selection([("male", "Male"), ("female", "Female")], string="Gender")
  active = Boolean(string="active", default=True)