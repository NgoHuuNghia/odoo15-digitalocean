# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
  _inherit = 'hr.employee'

  # business_trip_ids = 
  #! driver_rating_line_ids
  #! business_trip_count
  #! business_trip_ids
  #! business_rent_count
  #! business_rent_ids

  @api.depends('department_id')
  def _compute_department_position(self):
    for employee in self:
      if employee.department_id.manager_id.id == employee.id:
        employee.department_position = 'Manager'
      elif employee.department_id.vice_manager_id.id == employee.id:
        employee.department_position = 'Vice Manager'
      else:
        employee.department_position = 'Member'