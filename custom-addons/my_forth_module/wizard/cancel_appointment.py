from odoo import _
from odoo.models import TransientModel
from odoo.api import model
from odoo.fields import Many2one, Text, Date
from odoo.exceptions import ValidationError
from dateutil import relativedelta

# ? instead of the normal Model this is a Transient Model or i like to call it the wizard model
# ? these model won't be added to the database, they will be use and remove after, or after a set amount of time
class HospitalCancelAppointmentWizard(TransientModel):
  _name = "hospital.cancel.appointment.wizard"
  _description = "Cancel Appointment"

  #? this odoo'd method is use to get the defaults fields for a record, defaults that we specify only
  @model
  def default_get(self, fields_list):
    res = super(HospitalCancelAppointmentWizard, self).default_get(fields_list)
    #? also use the datetime package that odoo requires to get current date, the odoo.fields.Date.context_today won't work here
    res['date_cancel'] = Date.today()
    #?87? using the context in the [default_get] method we can get the [rec_name] more or less and manipulate it
    #? either get the id using the context.get or pass it with active_id in the view
    if self.env.context.get("active_id"):
      res['appointment_id'] = self.env.context.get("active_id")
    return res

  #?90? the domain to hard filter can also be apply to a Many2one field search using a list with tuples containing conditions
  #$ remember that in the domain's list all conditions will have an AND condition toward eachother, if you want an 
  #$ OR condition add ['|'] in front depend on how many tuples 2 for 3 tuples and etc... (prefix notation)
  # appointment_id = Many2one(comodel_name="hospital.appointment", string="Appointment", domain=[('state','=','draft'),('priority','in',('0','1',False))])
  appointment_id = Many2one(comodel_name="hospital.appointment", string="Appointment")
  reason = Text(string="Reason", default="None specify...")
  date_cancel = Date(string="Cancellation Date")

  #? using odoo's [ValidationError] method will let us raise a error base on some condition
  #? remember to import the underscore from odoo for translation purposes
  def action_cancel(self):
    #?114? to access the setting modules access the ['ir.config_parameter'] environment then use the [get_param(module_name.setting_field)]
    #? same as [config_parameter] in this modules's res_config_settings.py file 
    cancelable_days = self.env['ir.config_parameter'].get_param('my_forth_module.cancel_days')
    #? for some reason after pass back from setting module it will return a string, so convert it back into a integer with int()
    allowed_date = self.appointment_id.booking_date - relativedelta.relativedelta(days=int(cancelable_days))

    if allowed_date < Date.today():
      raise ValidationError(_(f"Can only cancel appointments before {cancelable_days} days of agreed booking"))
    self.appointment_id.state = 'cancel'

    #?120? returning a dictionary with [type] and [tag] like bellow to reload the page, for it won't visual change
    #? the state without reload, because we are changing the record of another many2one's model from this wizard
    return {
      'type':'ir.actions.client',
      'tag' :'reload',
    }