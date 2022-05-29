# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.api import onchange
from odoo.fields import Many2one, Datetime, Date, Selection, Char
class HospitalAppointment(Model):
  #? main name for this Module (you can check them in the setting of debug options)
  _name = "hospital.appointment"
  #? inherit modules's method from here as a list (remember to depend them on __manifest__.py)
  _inherit = ["mail.thread", "mail.activity.mixin"]
  _description = "Hospital Appointment"
  #? by default _rec-name will have field with 'name' as it value but you can change it into any field to show it on form's breadcrumbs
  _rec_name = 'patient_id'

  patient_id = Many2one(comodel_name='hospital.patient', string="Patient")
  gender = Selection(related='patient_id.gender')
  appointment_time = Datetime(string="Appointment Time", default=Datetime.now)
  booking_date = Date(string="Booking Date", default=Date.context_today)
  ref = Char(string='Reference')

  @onchange('patient_id')
  def onchange_patient_id(self):
    self.ref = self.patient_id.ref