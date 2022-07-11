# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api, exceptions, _
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

  # @api.model
  # def default_get(self, fields_list):
  #   res = super(FleetBusinessBase, self).default_get(fields_list)
  #   print('---res---',res)
  #   if not res['overseer_manager_id']:
  #     res['overseer_manager_id'] = self.env['hr.employee'].search([('department_id.name','=','Management'),('department_position','=','Manager')],limit=1).id
  #   return res

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
  #$ 5 available options ['manager','admin','creator',None]
  curr_logged_overseer = fields.Char('Current Logged In Overseer', compute='_compute_curr_logged_overseer')
  #$ all employees that need to approve this business trip
  #! overseer_manager_id = fields.Many2one('hr.employee',string='Creator\'s Manager', default=lambda self: self.env.user.employee_id.parent_id)
  overseer_manager_id = fields.Many2one('hr.employee',string='Creator\'s Manager', default=lambda self: self.env.user.employee_id.parent_id)
  overseer_manager_work_phone = fields.Char(related='overseer_manager_id.work_phone',string='Manager\'s Work Phone')
  overseer_manager_email = fields.Char(related='overseer_manager_id.work_email',string='Manager\'s Work Email')
  #! approval_manager = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision', readonly=True)
  approval_manager = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision', default=None, readonly=True)
  overseer_admin_id = fields.Many2one('hr.employee',string='Admin Assigned',
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Management')]")
  overseer_admin_work_phone = fields.Char(related='overseer_admin_id.work_phone',string='Admin\'s Work Phone')
  overseer_admin_email = fields.Char(related='overseer_admin_id.work_email',string='Admin\'s Work Email')
  approval_admin = fields.Selection(APPROVAL_SELECTIONS, string='Admin\'s Decision', default=None, readonly=True)
  overseer_creator_id = fields.Many2one('hr.employee',string='Creator',default=lambda self: self.env.user.employee_id)
  overseer_creator_work_phone = fields.Char(related='overseer_creator_id.work_phone',string='Creator\'s Work Phone')
  overseer_creator_email = fields.Char(related='overseer_creator_id.work_email',string='Creator\'s Work Email')
  approval_creator = fields.Selection(APPROVAL_SELECTIONS, string='Creator\'s Decision', default=None, readonly=True)
  #$ other fields
  intent = fields.Text('Intention', required=True, help='The intention of this business trip')
  note = fields.Text('Note/Comment', help='Any note, reminder or comments special to this business trip')
  state = fields.Selection(STATE_SELECTIONS,string='State',default='draft',compute='_compute_state',store=True)

  @api.depends()
  def _compute_curr_logged_overseer(self):
    for trip in self:
      if self.env.user == trip.overseer_manager_id.user_id:
        trip.curr_logged_overseer = "manager"
      elif self.env.user == trip.overseer_admin_id.user_id:
        trip.curr_logged_overseer = "admin"
      elif self.env.user == trip.overseer_creator_id.user_id:
        trip.curr_logged_overseer = "creator"
      else:
        trip.curr_logged_overseer = None

  def action_approval_manager_approved(self):
    self.approval_manager = "approved"
  def action_approval_manager_denied(self):
    self.approval_manager = "denied"

  def action_approval_admin_approved(self):
    self.approval_admin = "approved"
  def action_approval_admin_denied(self):
    self.approval_admin = "denied"

  def action_approval_creator_approved(self):
    self.approval_creator = "approved"
  def action_approval_creator_denied(self):
    self.approval_creator = "denied"

  def action_view_manager(self):
    return {
      'name': _('Manager'),
      'res_model': 'hr.employee.public',
      'view_mode': 'form',
      'res_id': self.overseer_manager_id.id,
      'target': 'current',
      'type': 'ir.actions.act_window',
    }
  def action_view_admin(self):
    return {
      'name': _('Admin'),
      'res_model': 'hr.employee.public',
      'view_mode': 'form',
      'res_id': self.overseer_admin_id.id,
      'target': 'current',
      'type': 'ir.actions.act_window',
    }
  def action_view_creator(self):
    return {
      'name': _('Creator'),
      'res_model': 'hr.employee.public',
      'view_mode': 'form',
      'res_id': self.overseer_creator_id.id,
      'target': 'current',
      'type': 'ir.actions.act_window',
    }

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

  # @api.constrains('overseer_manager_id','overseer_admin_id','overseer_creator_id')
  # def _check_time(self):
  #   for trip in self:
  #     if not trip.overseer_manager_id: 
  #       raise exceptions.ValidationError("Overseeing Manager can't be empty")
  #     elif not trip.overseer_admin_id: 
  #       raise exceptions.ValidationError("Overseeing Administrator can't be empty")
  #     elif not trip.overseer_creator_id: 
  #       raise exceptions.ValidationError("Overseeing Creator can't be empty")