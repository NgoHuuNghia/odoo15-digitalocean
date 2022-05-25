# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Char, Integer, Selection

print("hello")

class HospitalPatient(Model):
  _name = "hospital.patient"
  _description = "Hospital Patient"

  name = Char(string="Name")
  ref = Char(string="Reference")
  age = Integer(string="Age") 
  gender = Selection([("males", "Male"), ("female", "Female")], string="Gender")