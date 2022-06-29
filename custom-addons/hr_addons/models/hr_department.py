# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Department(models.Model):
  _inherit = 'hr.department'

  manager_id = fields.Many2one('hr.employee',
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.id', '=', id)]")
  vice_manager_id = fields.Many2one('hr.employee', string='Vice manager', tracking=True, 
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.id', '=', id)]")

  #? organizations and manager functionality plan to add to vice manager also
  
  def write(self, vals):
    if 'vice_manager_id' in vals:
      vice_manager_id = vals.get("vice_manager_id")
      self._update_employee_vice_manager(vice_manager_id)
    return super(Department, self).write(vals)
  
  def _update_employee_manager(self, manager_id):
    #$ updated version for this model
    employees = self.env['hr.employee']
    for department in self:
      employees = employees | self.env['hr.employee'].search([
        ('id', '!=', manager_id),
        ('department_id', '=', department.id),
        ('parent_id', '=', department.manager_id.id)
      ])
      old_manager = self.env['hr.employee'].search([
        ('id', '=', department.manager_id.id),
        ('department_id', '=', department.id),
      ])
      new_manager = self.env['hr.employee'].search([
        ('id', '=', manager_id),
        ('department_id', '=', department.id),
      ])
    employees.write({'parent_id': manager_id})
    old_manager.write({'department_position': 'Member'})
    new_manager.write({'department_position': 'Manager'})

  def _update_employee_vice_manager(self, vice_manager_id):
    # switch the vice positions
    for department in self:
      old_manager = self.env['hr.employee'].search([
        ('id', '=', department.vice_manager_id.id),
        ('department_id', '=', department.id),
      ])
      new_manager = self.env['hr.employee'].search([
        ('id', '=', vice_manager_id),
        ('department_id', '=', department.id),
      ])
    old_manager.write({'department_position': 'Member'})
    new_manager.write({'department_position': 'Vice Manager'})