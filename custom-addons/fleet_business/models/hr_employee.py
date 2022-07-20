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

  @api.model
  def default_get(self, fields_list):
    res = super(DriverRatingLine, self).default_get(fields_list)
    print('---context')
    print(self.env.context)
    if self.env.context.get("active_id") and self.env.context.get('active_model') == 'fleet.business.trip':
      res['fleet_business_trip_id'] = self.env.context.get("active_id")
      res['driver_id'] = self.env.context.get("driver_id")
      res['rater_id'] = self.env.user.employee_id.id
    return res

  fleet_business_trip_id = fields.Many2one('fleet.business.trip',readonly=True)
  driver_id = fields.Many2one('hr.employee',string="Driver Id",readonly=True)
  rater_id = fields.Many2one('hr.employee',readonly=True)
  rated = fields.Selection([
      ('1', 'Very Low'),
      ('2', 'Low'),
      ('3', 'Normal'),
      ('4', 'High'),
      ('5', 'Very High'),
    ], string="Rating given", required=True)
  note = fields.Text('Optional Rating Note')

  #! make constrains