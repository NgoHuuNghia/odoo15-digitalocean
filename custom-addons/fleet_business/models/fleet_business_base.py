# -*- coding: utf-8 -*-

from odoo import models, fields, api

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]
STATE_SELECTIONS = [
  ('draft','Draft'),('not_approved','Not Approved'),('approved','Approved'),('ready','Ready'),
  ('departing','Departing'),('returning','Returning'),('late','Late'),('returned','Returned'),
  ('car_na','Car N/a'),('driver_na','Driver N/a'),('car_driver_na','Car & Driver N/a'),
  ('canceled','Canceled'),('incident','Incident')
]

class FleetBusinessBase(models.Model):
  _name = 'fleet.business.base'
  _description = 'Base module for other business module'

  # attending_employee_ids = fields.One2many('hr.employee', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
  #   help='All attending employees, can be from different department')
  pick_time = fields.Datetime('Pick Up Time', default=fields.Datetime.now(),required=True)
  return_time = fields.Datetime('Return By Time', required=True)
  #$ these 2 Datetime fields is still experimental
  arrive_time = fields.Datetime('Estimated Arrive Time', readonly=True, compute='_compute_arrive_time')
  back_time = fields.Datetime('Estimated Back Time', readonly=True, compute='_compute_back_time')
  #$ location 
  company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
  to_street = fields.Char('To Street 1')
  to_street2 = fields.Char('To Street 2')
  to_zip = fields.Char('To Country\'s Zip Code',change_default=True)
  to_city = fields.Char('To City')
  to_state_id = fields.Many2one("res.country.state", string='To State/Province', domain="[('country_id', '=?', country_id)]")
  to_country_id = fields.Many2one('res.country', string='To Country')
  intent = fields.Text('Intention', required=True, help='The intention of this business trip')
  note = fields.Text('Note/Comment', help='Any note, reminder or comments special to this business trip')
  tag_ids = fields.Many2many(comodel_name='fleet.business.tag', relation="fleet_business_tag_rel", column1="fleet_business_id", column2="tag_id", string='Tags')
  #$ all employees that need to approve this business trip
  overseer_manager_id = fields.Many2one('hr.employee',string='Creator\'s Manager',related='create_uid.employee_id.parent_id')
  overseer_manager_work_phone = fields.Char(related='overseer_manager_id.work_phone')
  overseer_manager_email = fields.Char(related='overseer_manager_id.work_email')
  approval_manager = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision')
  overseer_admin_id = fields.Many2one('hr.employee',domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Management')]")
  overseer_admin_work_phone = fields.Char(related='overseer_admin_id.work_phone')
  overseer_admin_email = fields.Char(related='overseer_admin_id.work_email')
  approval_admin = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision')
  overseer_creator_id = fields.Many2one('hr.employee',string='Creator',related='create_uid.employee_id')
  overseer_creator_work_phone = fields.Char(related='overseer_creator_id.work_phone')
  overseer_creator_email = fields.Char(related='overseer_creator_id.work_email')
  approval_creator = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision')
  #$ other fields
  state = fields.Selection(STATE_SELECTIONS,string='Business State',default='draft',compute='_compute_state',store=True)
  journal_line_ids = fields.One2many('fleet.business.journal.line','fleet_business_base_id',string='Journal Line')