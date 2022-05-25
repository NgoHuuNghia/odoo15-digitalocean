# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Char, Integer, Selection

class HospitalPatient(Model):
  _name = "hospital.patient"
  _description = "Hospital Patient"

  name = Char(string="Name")
  age = Integer(string="Age") 
  gender = Selection([("males", "Male"), ("female", "Female")], string="Gender")