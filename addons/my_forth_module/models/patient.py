# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Char, Integer, Selection, Boolean
class HospitalPatient(Model):
  _name = "hospital.patient"
  _inherit = ["mail.thread", "mail.activity.mixin"]
  _description = "Hospital Patient"

  name = Char(string="Name", tracking=True)
  ref = Char(string="Reference", tracking=True)
  age = Integer(string="Age") 
  gender = Selection([("male", "Male"), ("female", "Female")], string="Gender")
  active = Boolean(string="active", default=True)