from odoo import _
from odoo.models import TransientModel
from odoo.api import model
from odoo.fields import Many2one, Text, Date
from odoo.exceptions import ValidationError

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
    #? using the context in the [default_get] method we can get the [rec_name] more or less and manipulate it
    if self.env.context.get("active_id"):
      res['appointment_id'] = self.env.context.get("active_id")
    return res

  #?90? the domain to hard filter can also be apply to a Many2one field search using a list with tuples containing conditions
  #$ remember that in the domain's list all conditions will have an AND condition toward eachother, if you want an 
  #$ OR condition add ['|'] in front depend on how many tuples 2 for 3 tuples and etc...
  # appointment_id = Many2one(comodel_name="hospital.appointment", string="Appointment", domain=[('state','=','draft'),('priority','in',('0','1',False))])
  appointment_id = Many2one(comodel_name="hospital.appointment", string="Appointment")
  reason = Text(string="Reason", default="None specify...")
  date_cancel = Date(string="Cancellation Date")

  #? using odoo's [ValidationError] method will let us raise a error base on some condition
  #? remember to import the underscore from odoo for translation purposes
  def action_cancel(self):
    if self.appointment_id.booking_date == Date.today():
      raise ValidationError(_("Cannot cancel an appointment on the same day of booking"))
    return