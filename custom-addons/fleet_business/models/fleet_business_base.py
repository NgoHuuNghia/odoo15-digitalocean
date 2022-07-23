# -*- coding: utf-8 -*-

from email.policy import default
from pprint import pprint
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
DUE_TIME_SETTING = 7 #days
SETTING_TIME_CONSTRAINS = 4 #months
#$ i really want to rework the overseer as it separated many2many model, to make it more customizable and dynamic
class FleetBusinessBase(models.AbstractModel):
  _name = 'fleet.business.base'
  _description = 'Base model for other business model'
  _inherit = 'mail.thread'

  @api.model
  def create(self, vals_list):
    vals_list['approval_manager'] = 'deciding'
    vals_list['name'] = self.env['ir.sequence'].next_by_code(self._name)
    vals_list['state'] = 'draft'
    return super(FleetBusinessBase, self).create(vals_list)

  def write(self, vals_list):
    if vals_list.get('overseer_admin_id'):
      self.curr_deciding_overseer_id = vals_list.get('overseer_admin_id')
      self.curr_deciding_overseer_role = 'Administrator'
      self.approval_admin = 'deciding'
      self.action_send_email()
    return super(FleetBusinessBase, self).write(vals_list)

  @api.model
  def default_get(self, vals_list):
    res = super(FleetBusinessBase, self).default_get(vals_list)
    if not res.get('overseer_creator_id'):
      raise exceptions.UserError('You are not an employee in this company, please contact admins for supports')
    if not res.get('overseer_manager_id'):
      #! searching for the 1st hit of Manager of the Management Department, have to be better way of doing this
      optional_manager = self.env['hr.employee.public'].search(['&','&','|',('company_id', '=', False),('company_id', '=', res.get('company_id')),('department_id.name','=','Management'),('department_position','=','Manager')],limit=1)
      res['overseer_manager_id'] = optional_manager.id
    res['curr_deciding_overseer_id'] = res.get('overseer_manager_id')
    res['curr_deciding_overseer_role'] = 'Manager'
    return res
    
  name = fields.Char()
  pick_time = fields.Datetime('Pick Up Time', default=fields.Datetime.now(),required=True)
  return_time = fields.Datetime('Return By Time', required=True)
  due_for_approval_time = fields.Datetime('Due For Approval By', compute='_compute_due_for_approval_time', readonly=True, store=True)
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
  #$ current deciding overseer
  curr_deciding_overseer_id = fields.Many2one('hr.employee.public',string='Current Deciding Overseer',help='Current Overseer That Need To Approve',readonly=True)
  curr_deciding_overseer_role = fields.Char(string="Current Deciding Overseer's Role",help='Current Overseer Role That Need To Approve',readonly=True)
  #$ all employees that need to approve this business trip
  overseer_manager_id = fields.Many2one('hr.employee.public',string='Creator\'s Manager', default=lambda self: self.env.user.employee_id.parent_id.id, readonly=True)
  overseer_manager_work_phone = fields.Char(related='overseer_manager_id.work_phone',string='Manager\'s Work Phone')
  overseer_manager_email = fields.Char(related='overseer_manager_id.work_email',string='Manager\'s Work Email')
  approval_manager = fields.Selection(APPROVAL_SELECTIONS, string='Manager\'s Decision', default=None, store=True, readonly=True)
  overseer_admin_id = fields.Many2one('hr.employee.public',string='Admin Assigned',
    domain="['&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Management')]")
  overseer_admin_work_phone = fields.Char(related='overseer_admin_id.work_phone',string='Admin\'s Work Phone')
  overseer_admin_email = fields.Char(related='overseer_admin_id.work_email',string='Admin\'s Work Email')
  approval_admin = fields.Selection(APPROVAL_SELECTIONS, string='Admin\'s Decision', default=None, store=True, readonly=True)
  overseer_creator_id = fields.Many2one('hr.employee.public',string='Creator',default=lambda self: self.env.user.employee_id.id, readonly=True)
  overseer_creator_work_phone = fields.Char(related='overseer_creator_id.work_phone',string='Creator\'s Work Phone')
  overseer_creator_email = fields.Char(related='overseer_creator_id.work_email',string='Creator\'s Work Email')
  approval_creator = fields.Selection(APPROVAL_SELECTIONS, string='Creator\'s Decision', default=None, readonly=True, store=True)
  #$ other fields
  intent = fields.Text('Intention', required=True, help='The intention of this business trip')
  note = fields.Text('Note/Comment', help='Any note, reminder or comments special to this business trip')
  state = fields.Selection(STATE_SELECTIONS,string='State',default=None,compute='_compute_state',store=True)
  #$ none-stored technical fields
  active = fields.Boolean(string='active', default=True)
  record_url = fields.Text("Record's url",compute="_compute_record_url")
  edit_hide_css_user = fields.Html(string='CSS', sanitize=False, compute='_compute_edit_hide_css_user')
  overseer_manager_logged = fields.Boolean(string="Manager In View",compute='_compute_logged_overseer', default=False)
  overseer_admin_logged = fields.Boolean(string="Administrator In View",compute='_compute_logged_overseer', default=False)
  overseer_creator_logged = fields.Boolean(string="Creator In View",compute='_compute_logged_overseer', default=False)

  @api.depends()
  def _compute_logged_overseer(self):
    for trip in self:
      if self.env.user == trip.overseer_manager_id.user_id:
        trip.overseer_manager_logged = True
      else: trip.overseer_manager_logged = False
      if self.env.user == trip.overseer_admin_id.user_id:
        trip.overseer_admin_logged = True
      else: trip.overseer_admin_logged = False
      if self.env.user == trip.overseer_creator_id.user_id:
        trip.overseer_creator_logged = True
      else: trip.overseer_creator_logged = False
  def _compute_record_url(self):
    web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    for rec in self:
      rec.record_url = """{}/web#id={}&model={}&view_type=form""".format(web_base_url,self.id,rec._name)
  def _compute_edit_hide_css_user(self):
    if self.env.user.has_group('fleet.fleet_group_manager'):
      self.edit_hide_css_user = False
    else:
      self.edit_hide_css_user = '<style>.o_form_button_edit {display: none !important;}</style>'

  @api.depends('pick_time')
  def _compute_due_for_approval_time(self):
    self.due_for_approval_time = self.pick_time - relativedelta.relativedelta(days=DUE_TIME_SETTING)

  #! see if it necessary to reboot the approval system when archive and unarchive 
  # @api.onchange('active')
  # def onchange_archive_curr_deciding_overseer_id(self):

  # @api.onchange('overseer_admin_id')

  def action_approval_manager_approved(self):
    self.ensure_one()
    self.approval_manager = "approved"
    self.action_send_email(special='request_admin_overseer_assignment')
  def action_approval_manager_denied(self):
    self.ensure_one()
    self.approval_manager = "denied"
    self.state = 'not_approved'
    self.action_send_email()

  def action_approval_admin_approved(self):
    self.ensure_one()
    self.approval_admin = "approved"
  #! kind of want to make a separate action for asking fleet to rework the infomation instead
  def action_approval_admin_denied(self):
    self.ensure_one()
    self.approval_admin = "denied"
    self.state = 'not_approved'
    self.action_send_email()
    
  def action_approval_creator_approved(self):
    self.ensure_one()
    self.approval_creator = "approved"
  #! will probably need to create a wizard to store excuses infomations for canceling
  def action_approval_creator_cancel(self):
    self.ensure_one()
    self.approval_creator = "denied"
    self.state = 'not_approved'
    self.curr_deciding_overseer_id = None
    self.curr_deciding_overseer_role = None

  def action_view_overseer(self):
    view_overseer = self.env.context.get('view_overseer')
    view_overseer_id = self.env.context.get('view_overseer_id')

    return {
      'name': _(view_overseer.capitalize()),
      'res_model': 'hr.employee.public',
      'view_mode': 'form',
      'res_id': view_overseer_id,
      'target': 'current',
      'type': 'ir.actions.act_window',
    }

  #? automated action to create the first journal run when record is 1st created
  def action_create_first_journal(self):
    first_journal_val_list = {
      f"{self._name.replace('.','_')}_id": self.id,
      'type': 'update',
      'note': f'{self.env.user.employee_id.name} have successfully created this trip, now awaiting approval.'
    }
    self.env[f'{self._name}.journal.line'].create(first_journal_val_list)

  def action_update_state_and_send_mass_mail_reminder(self,state):
    self.state = state
    self.action_send_email_mass(
      DUE_TIME=DUE_TIME_SETTING if state == 'ready' else None,
      special='alert_overseers' if state == 'late' else None,
    )
    
  def action_update_state_returned(self):
    self.state = 'returned'
    
  #! rating/state testing
  # def action_update_state_returning(self):
  #   self.state = 'returning'
  # def action_update_state_ready(self):
  #   self.state = 'ready'
  # def action_update_state_departing(self):
  #   self.state = 'departing'
  # def action_update_state_late(self):
  #   self.state = 'late'
  # def action_update_and_mail_ready(self):
  #   state = 'ready'
  #   self.state = state
  #   self.action_send_email_mass(DUE_TIME=DUE_TIME_SETTING if state == 'ready' else None)
  # def action_update_and_mail_departing(self):
  #   state = 'departing'
  #   self.state = state
  #   self.action_send_email_mass(DUE_TIME=DUE_TIME_SETTING if state == 'ready' else None)
  # def action_update_and_mail_late(self):
  #   state = 'late'
  #   self.state = state
  #   self.action_send_email_mass(
  #     DUE_TIME=DUE_TIME_SETTING if state == 'ready' else None,
  #     special='alert_overseers' if state == 'late' else None,
  #   )

  #? automated action to send mail depends on [curr_deciding_overseer_id] field not [None]
  def action_send_email(self, special=None):
    curr_admin_manager = None
    if self.state in ['canceled','not_approved']:
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_cancelation')
    elif special == 'request_admin_overseer_assignment':
      curr_admin_manager = self.env['hr.employee.public'].search(['&','&','|',('company_id', '=', False),('company_id', '=', self.company_id.id),('department_id.name','=','Management'),('department_position','=','Manager')],limit=1)
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_request_admin_overseer_assignment')
    elif special == 'request_admin_overseer_cancellation':
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_request_admin_overseer_cancellation')
    elif special == 'request_fleet_overseer_rework':
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_request_admin_overseer_rework')
    else:
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_approval')
      
    approval_email_template.with_context({
      'admin_manager': curr_admin_manager,
    }).send_mail(self.id, force_send=True)
    if self.state == ['canceled','not_approved']:
      self.curr_deciding_overseer_id = None
      self.curr_deciding_overseer_role = None

  #! gotta be a better way of sending mass mail
  def action_send_email_mass(self, DUE_TIME=None,special=None):
    if special == 'alert_overseers':
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_mass_overseers')
      receiver_recordset = self.overseer_manager_id | self.overseer_admin_id
    else:
      approval_email_template = self.env.ref('fleet_business.email_template_fleet_business_mass_attendees')
      receiver_recordset = self.attending_employee_ids

    for receiver in receiver_recordset:
      approval_email_template.with_context({
        'receiver': receiver,
        'DUE_TIME': DUE_TIME,
      }).send_mail(self.id, force_send=True, raise_exception=False)
  
  def action_request_reapproval(self):
    self.curr_deciding_overseer_id = self.overseer_manager_id.id
    self.curr_deciding_overseer_role = 'Manager'
    self.approval_manager = 'deciding'
    self.state = 'draft'
    self.approval_creator = None
    self.approval_admin = None
    self.overseer_admin_id = None

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