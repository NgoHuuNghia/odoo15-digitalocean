import datetime
from odoo.models import TransientModel
from odoo.api import model
from odoo.fields import Many2one, Text, Date

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
    res['date_cancel'] = datetime.date.today()
    return res

  appointment_id = Many2one(comodel_name="hospital.appointment", string="Appointment")
  reason = Text(string="Reason", default="None specify...")
  date_cancel = Date(string="Cancellation Date")

  def action_cancel(self):
    print(self)