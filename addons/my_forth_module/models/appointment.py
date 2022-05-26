# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.fields import Many2one

class HospitalAppointment(Model):
  _name = "hospital.appointment"
  _inherit = ["mail.thread", "mail.activity.mixin"]
  _description = "Hospital Appointment"

  patient_id = Many2one(comodel_name='hospital.patient', string="Patient")