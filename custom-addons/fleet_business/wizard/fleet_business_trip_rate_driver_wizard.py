from odoo import models, api, fields, exceptions, _
from dateutil import relativedelta

class FleetBusinessTripRateDriverWizard(models.TransientModel):
  _name = "fleet.business.trip.rate.driver.wizard"
  _description = "Rate Driver"

  @api.model
  def default_get(self, fields_list):
    res = super(FleetBusinessTripRateDriverWizard, self).default_get(fields_list)
    res['date_cancel'] = fields.Date.today()
    if self.env.context.get("active_id"):
      res['appointment_id'] = self.env.context.get("active_id")
    return res

  driver_id = fields.Many2one('hr.employee',string="Driver Id",readonly=True)
  fleet_business_trip_id = fields.Many2one('fleet.business.trip')
  rater_id = fields.Many2one('hr.employee')
  rated = fields.Selection([
      ('1', 'Very Low'),
      ('2', 'Low'),
      ('3', 'Normal'),
      ('4', 'High'),
      ('5', 'Very High'),
    ], string="Rating given", default="3", required=True)
  note = fields.Text('Optional Rating Note')

  #? using odoo's [ValidationError] method will let us raise a error base on some condition
  #? remember to import the underscore from odoo for translation purposes
  def action_cancel(self):
    #?114? to access the setting modules access the ['ir.config_parameter'] environment then use the [get_param(module_name.setting_field)]
    #? same as [config_parameter] in this modules's res_config_settings.py file 
    cancelable_days = self.env['ir.config_parameter'].get_param('my_forth_module.cancel_days')
    #? for some reason after pass back from setting module it will return a string, so convert it back into a integer with int()
    allowed_date = self.appointment_id.booking_date - relativedelta.relativedelta(days=int(cancelable_days))

    if allowed_date < fields.Date.today():
      raise exceptions.ValidationError(_(f"Can only cancel appointments before {cancelable_days} days of agreed booking"))
    self.appointment_id.state = 'cancel'

    #?120? returning a dictionary with [type] and [tag] like bellow to reload the page, for it won't visual change
    #? the state without reload, because we are changing the record of another many2one's model from this wizard
    return {
      'type':'ir.actions.act_window',
      'view_mode':'form',
      'res_model':'hospital.cancel.appointment.wizard',
      'target':'new',
      'res_id':self.id,
    }
    # return {
    #   'type':'ir.actions.client',
    #   'tag' :'reload',
    # }