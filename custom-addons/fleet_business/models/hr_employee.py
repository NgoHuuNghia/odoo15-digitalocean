# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

RATING_SELECTIONS = [('0','None'),('1','VeryLow'),('2','Low'),('3','Normal'),('4','High'),('5','Very High'),]
#! gotta convert the fleet_business view from hr.employee to public
class Employee(models.Model):
  _inherit = 'hr.employee'

  business_trip_ids = fields.Many2many(comodel_name='fleet.business.trip', relation='fleet_business_trip_employees_rel', 
    column1='employee_id', column2='business_trip_id', string='Active Business Trip', readonly=True, domain=[('state', 'in', ['draft','approved','ready','departing','returning'])])
  #! business_trip_count
  #! business_rent_count
  #! business_rent_ids
  driver_ratings = fields.Selection(RATING_SELECTIONS,'Driver\'s Ratings', compute='_compute_driver_ratings',default="0",readonly=True,store=True)
  driver_rating_line_ids = fields.One2many('hr.employee.fleet.driver.rating.line','driver_id',string='Driver Ratings',readonly=True)

  @api.depends('driver_rating_line_ids')
  def _compute_driver_ratings(self):
    list_of_string_ratings = self.driver_rating_line_ids.mapped('rated')
    if len(list_of_string_ratings) <= 0:
      self.driver_ratings = '0'
    else:
      list_of_integer_ratings = list(map(int, list_of_string_ratings))
      rating_average_string = str(round(sum(list_of_integer_ratings)/len(list_of_integer_ratings)))
      self.driver_ratings = rating_average_string
class DriverRatingLine(models.Model):
  _name = 'hr.employee.fleet.driver.rating.line'
  _description = 'Fleet Driver Ratings'
  _order = 'id'

  #! Maybe the postsql constraint is the better way
  @api.model
  def default_get(self, fields_list):
    res = super(DriverRatingLine, self).default_get(fields_list)
    if self.env.context.get("active_id") and self.env.context.get('active_model') == 'fleet.business.trip':
      driver_rating_lines_of_same_business_trip_recordset = self.env['hr.employee.fleet.driver.rating.line'].search([
        ('fleet_business_trip_id','=', self.env.context.get('active_id')),
        ('driver_id','=', self.env.context.get('driver_id')),
      ])
      if self.env.context.get('rater_id') in driver_rating_lines_of_same_business_trip_recordset.rater_id.ids:
        raise exceptions.UserError("You can't rate the same driver on the same business trip")

      res['fleet_business_trip_id'] = self.env.context.get('active_id')
      res['driver_id'] = self.env.context.get('driver_id')
      res['rater_id'] = self.env.context.get('rater_id')
    return res

  fleet_business_trip_id = fields.Many2one('fleet.business.trip',readonly=True)
  driver_id = fields.Many2one('hr.employee',string="Driver Id",readonly=True)
  rater_id = fields.Many2one('hr.employee',readonly=True)
  rated = fields.Selection(RATING_SELECTIONS, string="Rating given", required=True)
  note = fields.Text('Optional Rating Note')

class EmployeePublic(models.Model):
  _inherit = 'hr.employee.public'

  driver_ratings = fields.Selection(RATING_SELECTIONS,'Driver\'s Ratings', related='employee_id.driver_ratings',readonly=True)