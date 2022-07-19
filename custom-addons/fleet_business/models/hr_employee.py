# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
  _inherit = 'hr.employee'

  business_trip_ids = fields.Many2many(comodel_name='fleet.business.trip', relation='business_trip_employees_rel', 
    column1='employee_id', column2='business_trip_id', string='Attended Business Trips', readonly=True)
  #! business_trip_count
  #! business_rent_count
  #! business_rent_ids
  #! driver_rating_line_ids
  ratings = fields.Float('Employee\'s Ratings')
  driver_rating_line_ids = fields.One2many('hr.employee.fleet.driver.rating.line','driver_id',string='Driver Ratings',readonly=True)
class DriverRatingLine(models.Model):
  _name = 'hr.employee.fleet.driver.rating.line'
  _description = 'Fleet Driver Ratings'
  _order = 'id'

  driver_id = fields.Many2one('hr.employee',string="Driver Id",readonly=True)
  fleet_business_trip_id = fields.Many2one('fleet.business.trip')
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