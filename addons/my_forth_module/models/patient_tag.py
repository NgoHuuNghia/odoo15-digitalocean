from odoo.models import Model
from odoo.fields import Char, Boolean, Integer

class HospitalPatientTag(Model):
  _name = "hospital.patient.tag"
  _description = "Patient Tag"

  name = Char(string="Name", required=True)
  active = Boolean(string="Active", default=True)
  #* these color field will later be use with an options attribute later to add colors to tags
  color = Integer(string="color")
  color_2 = Char(string="Color 2")