# -*- coding: utf-8 -*-
from odoo.models import Model
from odoo.api import onchange
from odoo.fields import Many2one, One2many, Datetime, Date, Selection, Char, Html, Integer, Float, Boolean
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
  ref = Char(string='Reference', help="Referece of the patient's record")
  prescription = Html(string="Prescription")
  doctor_id = Many2one('res.users', string="Doctor")
  # ? here we are creating a one2many relations using a new model bellow, go down there for more infomation
  # ? 1st argument is the model's name and 2nd is the field that link these 2 model in this case [appointment_id]
  pharmacy_line_ids = One2many('hospital.appointment.pharmacy.lines', 'appointment_id', string="Pharmacy Lines")
  # ? this is just a test boolean to learn how to hide column
  hide_sales_price = Boolean(string="Hide sales Price")
  priority = Selection(
    [
      ('0', 'Normal'),
      ('1', 'Low'),
      ('2', 'High'),
      ('3', 'Very High')
    ], string="Priority"
  )
  state = Selection(
    [
      ('draft', 'Draft'),
      ('in_consultation', 'In Consultation'),
      ('done', 'Done'),
      ('cancel', 'Cancel')
    ], string="Status", default="draft", tracking=True, required=True
  )

  @onchange('patient_id')
  def onchange_patient_id(self):
    self.ref = self.patient_id.ref

  def object_test(self):
    return {
      'effect': {
          'fadeout': 'slow',
          'message': f'Clicked successfully on {self.patient_id}',
          'type': 'rainbow_man',
      }
    }

  def action_done(self):
    for rec in self:
      rec.state = "done" 
  def action_in_consultation(self):
    for rec in self:
      rec.state = "in_consultation" 
  def action_cancel(self):
    for rec in self:
      rec.state = "cancel" 
  def action_draft(self):
    for rec in self:
      rec.state = "draft"

# ? first step to create a one2many relation is to create a new model either in a new file or same up to you
# ? then create a field to link betweeen them with a [many2one] method see -> appointment_id
# ? also here we are depending the [product] model from the [product] module for testing purposes, remember to depend them on manifest.py
class HospitalAppointmentPharmacyLines(Model):
  _name = "hospital.appointment.pharmacy.lines"
  _description = "Appointment Pharmacy Lines"

  product_id = Many2one('product.product', require=True)
  price_unit = Float(related="product_id.list_price")
  qty = Integer(string="Quantity", default=1)
  appointment_id = Many2one('hospital.appointment', string="Appointment")