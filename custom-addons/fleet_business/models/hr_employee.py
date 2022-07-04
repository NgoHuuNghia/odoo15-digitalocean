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