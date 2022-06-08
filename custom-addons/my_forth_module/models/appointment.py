# -*- coding: utf-8 -*-
from odoo import _
from odoo.exceptions import ValidationError, CacheMiss
from odoo.models import Model
from odoo.api import depends, onchange, model, ondelete
from odoo.fields import Many2one, One2many, Datetime, Date, Selection, Char, Html, Integer, Float, Boolean, Monetary
class HospitalAppointment(Model):
  #? main name for this Module (you can check them in the setting of debug options)
  _name = "hospital.appointment"
  #?41? inherit modules's method from here as a list (remember to depend them on __manifest__.py)
  _inherit = ["mail.thread", "mail.activity.mixin"]
  _description = "Hospital Appointment"
  #? by default _rec-name will have field with 'name' as it value but you can change it into any field to show it on form's breadcrumbs
  _rec_name = 'name'
  #?119 with the [_order] property we can specify the order of our fields in the tree view?
  _order = 'id desc'
  #? just add more separated by comma for more complacted ordering
  # _order = 'id desc, name, age asc'

  @model
  def create(self, vals_list):
    vals_list['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
    return super(HospitalAppointment, self).create(vals_list)

  def write(self, vals):
    for record in self:
      if (not record.name or record.name == False) and not vals.get('name'):
        print('self.name--',self.name)
        print('self.name--',vals.get('name'))
        record.name = self.env['ir.sequence'].next_by_code('hospital.appointment')
    return super(HospitalAppointment, self).write(vals)

  #?89?94? the unlike method let us access the delete functions on the odoo's UI letting us manipulate the process
  #? in this case disallowing the user from delete the record while it in any but draft state
  def unlink(self):
    for record in self:
      if record.state != "draft":
        raise ValidationError("You can only delete appointments in draft state")
    return super(HospitalAppointment, self).unlink()

  name = Char(string="Appointment ID")
  #?97? with the [ondelete='restrict'] parameter we can prevent the deletion of the depended many2one model's record
  #? until all of depending model's records in the many's side is deleted first
  #? on the other hand [ondelete='cascade'] will detect if the depended many2one model's record is deleted than it will
  #? also delete all the model's records here that depending on it
  # patient_id = Many2one(comodel_name='hospital.patient', string="Patient", ondelete='restrict')
  patient_id = Many2one(comodel_name='hospital.patient', string="Patient", ondelete='cascade')
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
  operation_id = Many2one(comodel_name="hospital.operation",string="Operation ID")
  #?126? adding a progress widget in the view, we will need a computed Integer field
  progress = Integer(string="Progress", compute="_compute_progress")
  duration = Float(string="Duration")
  #?131? adding a currency_id and company_id of our current company the all the currencies to add currency to Monetary field
  company_id = Many2one('res.company', "Company", default=lambda self: self.env.company)
  currency_id = Many2one('res.currency', related='company_id.currency_id')
  total = Monetary(string='Total Bill', compute='_compute_total', default=0.0, store=True)
  priority = Selection(
    [
      ('0', 'Normal'),
      ('1', 'Low'),
      ('2', 'High'),
      ('3', 'Very High')
    ], string="Priority", default="0"
  )
  state = Selection(
    [
      ('draft', 'Draft'),
      ('in_consultation', 'In Consultation'),
      ('done', 'Done'),
      ('cancel', 'Cancel')
    ], string="Status", default="draft", tracking=True, required=True
  )

  #? an onchange decorator will run the def bellow whenever this field [patient_id] is changed
  @onchange('patient_id')
  def onchange_patient_id(self):
    for record in self:
      record.ref = record.patient_id.ref

  def object_test(self):
    return {
      'effect': {
          'fadeout': 'slow',
          'message': f'Clicked successfully on {self.patient_id}',
          'type': 'rainbow_man',
      }
    }
  
  #?126? here where we define the logic behind the progress compute
  @depends('state')
  def _compute_progress(self):
    for record in self:
      if record.state == 'cancel':
        record.progress = 0
      elif record.state == 'draft':
        record.progress = 25
      elif record.state == 'in_consultation':
        record.progress = 50
      elif record.state == 'done':
        record.progress = 100
      else:
        record.progress = 0
        raise CacheMiss("a record in hospital.appointment model has an invalid state's value")

  @depends('pharmacy_line_ids')
  def _compute_total(self):
    for record in self:
      print('record.pharmacy_line_ids.price_subtotal---------', record.pharmacy_line_ids)
      for bill_record in record.pharmacy_line_ids:
        record.total += bill_record.price_subtotal

  def action_done(self):
    for rec in self:
      if rec.state == 'in_consultation':
        rec.state = "done" 
  def action_in_consultation(self):
    for rec in self:
      #?102? extra condition when we want to use this function in the tree view
      if rec.state == 'draft':
        rec.state = "in_consultation"
  # ? if you need to get an window action and run it using a function then here the syntax
  def action_cancel(self):
    action = self.env.ref("my_forth_module.action_cancel_appointment").read()[0]
    # for rec in self:
    #   rec.state = "cancel"
    return action
  def action_draft(self):
    for rec in self:
      rec.state = "draft"

  #$ Action to return from appointment to a patient form view
  def action_view_patient(self):
    return {
        'name': _('Patient'),
        'res_model': 'hospital.patient',
        'view_mode': 'form',
        'res_id': self.patient_id.id,
        # 'context': {'default_id':self.patient_id},
        # 'domain': [('id','=',self.patient_id)],
        'target': 'current',
        'type': 'ir.actions.act_window',
    }

# ? first step to create a one2many relation is to create a new model either in a new file or same up to you
# ? then create a field to link betweeen them with a [many2one] method see -> appointment_id
# ? also here we are depending the [product] model from the [product] module for testing purposes, remember to depend them on manifest.py
class HospitalAppointmentPharmacyLines(Model):
  _name = "hospital.appointment.pharmacy.lines"
  _description = "Appointment Pharmacy Lines"

  product_id = Many2one('product.product', required=True)
  price_unit = Float(related="product_id.list_price")
  qty = Integer(string="Quantity", default=1)
  appointment_id = Many2one('hospital.appointment', string="Appointment")
  #?131? link a related currency_id field from the parent to add type of currencies
  #! fyi [currency_id] is a technical name so changing it you need to specify it with [currency_field] in subtotal
  # currency_id = Many2one('res.currency', "Currency", related='appointment_id.currency_id')
  company_currency_id = Many2one('res.currency', "Currency", related='appointment_id.currency_id')
  #?131? field to calculate the subtotal of a product with a [currency_id], later total for a bill
  price_subtotal = Monetary(currency_field="company_currency_id",string="Sub Total", compute="_compute_price_subtotal")

  @depends('price_unit','qty')
  def _compute_price_subtotal(self):
    for record in self:
      record.price_subtotal = record.price_unit * record.qty