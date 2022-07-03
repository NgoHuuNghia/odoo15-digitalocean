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
    if 'manager_id' in vals:
      old_manager_id = self.manager_id.id
      new_manager_id = vals.get("manager_id")
      if new_manager_id:
          manager = self.env['hr.employee'].browse(new_manager_id)
          # subscribe the manager user
          if manager.user_id:
              self.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
      # set the employees's parent to the new manager
      self._update_employee_manager(new_manager_id,old_manager_id)
    #? A hack to override an existing write override in hr_department
    return models.Model.write(self, vals)
  
  def _update_employee_manager(self, new_manager_id,old_manager_id):
    employees = self.env['hr.employee']
    for department in self:
      employees = employees | self.env['hr.employee'].search([
        ('id', '!=', new_manager_id),
        ('department_id', '=', department.id),
        ('parent_id', '=', old_manager_id)
      ])
    employees.write({'parent_id': new_manager_id})
    employees.browse(old_manager_id).write({'department_position': 'Member'})

    new_manager_parent_id = employees.browse(new_manager_id).parent_id.id
    if new_manager_parent_id == new_manager_id:
      employees.browse(new_manager_id).write({'department_position': 'Manager','parent_id':None})
    else:
      employees.browse(new_manager_id).write({'department_position': 'Manager'})

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