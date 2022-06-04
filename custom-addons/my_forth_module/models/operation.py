from odoo import models,api,fields

#?115? model to learn about [_log_access] to remove base fields (Create, Write)
class HospitalOperation(models.Model):
  _name = 'hospital.operation'
  _description = 'Current Operations'
  # _rec_name = 'doctor_id'
  #?115? with [_log_access] property we can remove base fields like (Create, Write,...).
  #? Though only normal model can use this property not transient ones
  _log_access = False
  
  doctor_id = fields.Many2one('res.users', string="Doctor")
  operation_name = fields.Char(string='Name')
  #?121? with [Reference] method we can add a selection field of Pseudo-relational fields of [model_name,this_field_string]
  #! one thing to remember that [Many2one] and relations like that will store value as integer id of that record [1]
  #!  while [Reference] will store a string [hospital.patient,1]
  reference_record = fields.Reference(selection=[
    ('hospital.patient','Patient'),
    ('hospital.appointment','Appointment')
  ],string='Record')

  #?116? using name_create function for niche use-case when we don't have a [name] field or [_rec_name] property
  #? applicable when creating a new record using the Many2one fields
  @api.model
  def name_create(self, name):
    return self.create({'operation_name':name}).name_get()[0]