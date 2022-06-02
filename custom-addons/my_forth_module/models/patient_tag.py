from odoo import _
from odoo.models import Model
from odoo.api import returns
from odoo.fields import Char, Boolean, Integer

class HospitalPatientTag(Model):
  _name = "hospital.patient.tag"
  _description = "Patient Tag"

  name = Char(string="Name", required=True)
  #?93? with the copy parameter, let us configure the when duplicate, it won't copy this field too
  active = Boolean(string="Active", default=True, copy=False)
  #* these color field will later be use with an options attribute later to add colors to tags
  color = Integer(string="color")
  color_2 = Char(string="Color 2")
  sequence = Integer(string="Sequence", default=1)

  #?93? the return decorator and copy method will let us manipulate the duplicate function in the odoo UI 
  @returns('self', lambda value: value.id)
  #? with this function will let user know that the newly duplicated record should be rename something unique
  def copy(self, default=None):
    if default is None:
      default = {}
    if not default.get('name'):
      default['name'] = _(f"{self.name} (COPY)")
    default['sequence'] = 10
    return super(HospitalPatientTag, self).copy(default)

  #?91? for giving constraints for any field, there 2 way, sql or python. bellow is the sql constraints, also always bellow field declaration
  #$ the syntax is [_sql_constraints] contain a list of constraints in which it a tuple with 3 string value
  #$ parameter in order is (constraint name, sql query, error message on violation)
  _sql_constraints = [
    #$ sql query demand that name is unique and active not true
    ('tag_name_archive_uniq', 'UNIQUE (name,active)', 'Tag name must be unique. And not active'),
    #$ sql query demand that integer is greater than 0
    ('sequence_check', 'CHECK (sequence > 0)', 'Sequence must be greater than 0'),
  ]