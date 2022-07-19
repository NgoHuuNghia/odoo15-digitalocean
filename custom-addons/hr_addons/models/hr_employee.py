# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
  _inherit = 'hr.employee'

  department_position = fields.Char('Department Position', compute='_compute_department_position',store=True)
  parent_id = fields.Many2one('hr.employee',
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('id', '!=', id)]")
  ratings = fields.Float('Employee\'s Ratings')
  driver_rating_line_ids = fields.One2many('hr.employee.fleet.driver.rating.line','driver_id',string='Driver Ratings')

  @api.depends('department_id')
  def _compute_department_position(self):
    for employee in self:
      if employee.department_id.manager_id.id == employee.id:
        employee.department_position = 'Manager'
      elif employee.department_id.vice_manager_id.id == employee.id:
        employee.department_position = 'Vice Manager'
      else:
        employee.department_position = 'Member'

class DriverRatingLine(models.Model):
  _name = 'hr.employee.fleet.driver.rating.line'
  _description = 'Fleet Driver Ratings'
  _order = 'id'

  driver_id = fields.Many2one('hr.employee',string="Driver Id",readonly=True)
  # fleet_business_trip_id = fields.Many2one('fleet.business.trip')
  rater_id = fields.Many2one('hr.employee')
  rated = fields.Selection(
    [
      ('1', 'Very Low'),
      ('2', 'Low'),
      ('3', 'Normal'),
      ('4', 'High'),
      ('5', 'Very High'),
    ], string="Rating given", default="3", required=True
  )
  note = fields.Text('Optional Rating Note')