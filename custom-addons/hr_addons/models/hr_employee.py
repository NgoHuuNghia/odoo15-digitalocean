# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
  _inherit = 'hr.employee'

  department_position = fields.Char('Department Position', compute='_compute_department_position',store=True)
  parent_id = fields.Many2one('hr.employee',
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('id', '!=', id)]")
  ratings = fields.Float('Employee\'s Ratings')

  @api.depends('department_id')
  def _compute_department_position(self):
    for employee in self:
      if employee.department_id.manager_id.id == employee.id:
        employee.department_position = 'Manager'
      elif employee.department_id.vice_manager_id.id == employee.id:
        employee.department_position = 'Vice Manager'
      else:
        employee.department_position = 'Member'