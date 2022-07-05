# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api, exceptions
from dateutil import relativedelta

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]
STATE_SELECTIONS = [
  ('draft','Draft'),('not_approved','Not Approved'),('approved','Approved'),('ready','Ready'),
  ('departing','Departing'),('returning','Returning'),('late','Late'),('returned','Returned'),
  ('car_na','Car N/a'),('driver_na','Driver N/a'),('car_driver_na','Car & Driver N/a'),
  ('canceled','Canceled'),('incident','Incident')
]
#! Add the setting properly to setting module
SETTING_TIME_CONSTRAINS = 4

class FleetBusinessBase(models.AbstractModel):
  _name = 'fleet.business.base'
  _description = 'Base model for other business model'
  _inherit = 'mail.thread'

  name = fields.Char()
  pick_time = fields.Datetime('Pick Up Time', default=fields.Datetime.now(),required=True)
  return_time = fields.Datetime('Return By Time', required=True)
  #$ these 2 Datetime fields is still experimental
  arrive_time = fields.Datetime('Estimated Arrive Time', readonly=True)
  back_time = fields.Datetime('Estimated Back Time', readonly=True)
  #$ location 
  company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company, readonly=True)
  to_street = fields.Char('To Street 1')
  to_street2 = fields.Char('To Street 2')
  to_zip = fields.Char('To Country\'s Zip Code',change_default=True)
  to_city = fields.Char('To City')
  to_state_id = fields.Many2one("res.country.state", string='To State/Province', domain="[('country_id', '=?', to_country_id)]")
  to_country_id = fields.Many2one('res.country', string='To Country')
  #$ all employees that need to approve this business trip
  overseer_manager_id = fields.Many2one('hr.employee',string='Creator\'s Manager', default=lambda self: self.env.user.employee_id.parent_id)
  overseer_manager_work_phone = fields.Char(related='overseer_manager_id.work_phone',string='Manager\'s Work Phone')
  overseer_manager_email = fields.Char(related='overseer_manager_id.work_email',string='Manager\'s Work Email')
  approval_manager = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision', default='deciding', readonly=True)
  overseer_admin_id = fields.Many2one('hr.employee',string='Admin Assigned',
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Management')]")
  overseer_admin_work_phone = fields.Char(related='overseer_admin_id.work_phone',string='Admin\'s Work Phone')
  overseer_admin_email = fields.Char(related='overseer_admin_id.work_email',string='Admin\'s Work Email')
  approval_admin = fields.Selection(APPROVAL_SELECTIONS, string='Admin\'s Decision', default='deciding', readonly=True)
  overseer_creator_id = fields.Many2one('hr.employee',string='Creator',readonly=True,
    default=lambda self: self.env.user.employee_id)
  overseer_creator_work_phone = fields.Char(related='overseer_creator_id.work_phone',string='Creator\'s Work Phone')
  overseer_creator_email = fields.Char(related='overseer_creator_id.work_email',string='Creator\'s Work Email')
  approval_creator = fields.Selection(APPROVAL_SELECTIONS, string='Creator\'s Decision', default='deciding', readonly=True)
  #$ other fields
  intent = fields.Text('Intention', required=True, help='The intention of this business trip')
  note = fields.Text('Note/Comment', help='Any note, reminder or comments special to this business trip')
  state = fields.Selection(STATE_SELECTIONS,string='State',default='draft',compute='_compute_state',store=True)

  #? Temp using this exeptions way to throw error, want to use the notification and highlight way instead
  @api.constrains('pick_time','return_time')
  def _check_time(self):
    for trip in self:
      if not trip.return_time: 
        raise exceptions.UserError("Return By Time can't be empty")
      elif trip.return_time < trip.pick_time:
        raise exceptions.ValidationError("Return By Time can't be before Pick Up Time")
      elif trip.return_time > trip.pick_time + relativedelta.relativedelta(months=SETTING_TIME_CONSTRAINS):
        raise exceptions.ValidationError(f"Return By Time can't {SETTING_TIME_CONSTRAINS} months in the future")