# -*- coding: utf-8 -*-

from odoo import models, fields, api

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]

class FleetBusinessTrip(models.Model):
  _name = 'fleet.business.trip'
  _description = "Model for creating and supervising a business trip with a company's car"
  _inherit = ['fleet.business.base']

  name = fields.Char('Sequence Name',readonly=True)
  attending_employee_ids = fields.Many2many(comodel_name='hr.employee', relation='business_trip_employees_rel', 
    column1='business_trip_id', column2='employee_id', string='All Attending Employees')
  pick_address_id = fields.Many2one('res.partner',compute='_compute_address_id',domain="[('company_id', '=', True), ('company_id', '=', self.env.company.id)]")
  vehicle_id = fields.Many2one('fleet.vehicle','Vehicle Used')
  model_id = fields.Many2one(related='vehicle_id.model_id',string='Model')
  license_plate = fields.Char(related='vehicle_id.license_plate',string='License Plate')
  seats = fields.Integer(related='vehicle_id.seats',string='Seats')
  self_driving_employee = fields.Many2one('hr.employee',string='Self Driver')
  driver_id = fields.Many2one('hr.employee',string="Company's Driver")
  overseer_fleet_id = fields.Many2one('hr.employee',string='Fleet Captain',
    default=lambda self: self.env['hr.employee'].search([('department_id.name','=','Fleet'),('department_position','=','Manager')],limit=1),
    domain="['&','&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Fleet'),('department_position', 'in', ['Manager','Vice Manager'])]")
  overseer_fleet_work_phone = fields.Char(related='overseer_fleet_id.work_phone',string='Fleet\'s Work Phone')
  overseer_fleet_email = fields.Char(related='overseer_fleet_id.work_email',string='Fleet\'s Work Email')
  approval_fleet = fields.Selection(APPROVAL_SELECTIONS, string='Fleet\'s Decision', default='deciding')
  tag_ids = fields.Many2many(comodel_name='fleet.business.tag', relation="fleet_business_trip_tag_rel", column1="fleet_business_trip_id", column2="tag_id", string='Tags')