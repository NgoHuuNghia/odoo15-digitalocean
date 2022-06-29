from odoo import models, fields, api

class User(models.Model):
  _inherit = ['res.users']

  department_position = fields.Char('Department Position', related='employee_id.department_position')