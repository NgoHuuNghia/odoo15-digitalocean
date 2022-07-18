# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]

class FleetBusinessTrip(models.Model):
  _name = 'fleet.business.trip'
  _description = "Business Trip"
  _inherit = ['fleet.business.base']

  def write(self, vals_list):
    if vals_list.get('approval_admin') == 'approved':
      self.curr_deciding_overseer_id = self.overseer_fleet_id.id
      self.curr_deciding_overseer_role = 'Fleet Captain'
      self.approval_fleet = 'deciding'
      self.action_send_email()
    return super(FleetBusinessTrip, self).write(vals_list)

  name = fields.Char('Sequence Name',readonly=True)
  attending_employee_ids = fields.Many2many(comodel_name='hr.employee', relation='fleet_business_trip_employees_rel', 
    column1='business_trip_id', column2='employee_id', string='Attending Employees', required=True)
  attending_employee_count = fields.Integer(string="Attendees Count", compute="_compute_attending_employee_count", store=True)
  pick_address_id = fields.Many2one('res.partner','Pick Up Company',compute='_compute_address_id', store=True, readonly=False,
    #! domain="[('is_company', '=', True),('company_id','!=',False)]" for just company in the system, but need work
    domain="[('is_company', '=', True)]"
  )
  to_country_id = fields.Many2one(related='pick_address_id.country_id', string='To Country')
  vehicle_id = fields.Many2one('fleet.vehicle','Vehicle Used',required=True)
  model_id = fields.Many2one(related='vehicle_id.model_id',string='Model')
  license_plate = fields.Char(related='vehicle_id.license_plate',string='License Plate')
  seats = fields.Integer(related='vehicle_id.seats',string='Seats',store=True)
  self_driving_employee_id = fields.Many2one('hr.employee',string='Attendee Driver',domain="[('id', 'in', attending_employee_ids)]")
  driver_id = fields.Many2one('hr.employee',string="Company's Driver")
  overseer_fleet_id = fields.Many2one('hr.employee',string='Fleet Captain', readonly=True,
    default=lambda self: self.env['hr.employee'].search([('department_id.name','=','Fleet'),('department_position','=','Manager')],limit=1,order='id').ensure_one(),
    domain="['&','&','&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Fleet'),('department_position', 'in', ['Manager','Vice Manager']),('job_title', '=', 'Fleet Captain')]")
  overseer_fleet_work_phone = fields.Char(related='overseer_fleet_id.work_phone',string='Fleet\'s Work Phone')
  overseer_fleet_email = fields.Char(related='overseer_fleet_id.work_email',string='Fleet\'s Work Email')
  overseer_fleet_logged = fields.Boolean(string="Fleet Captain In View",compute='_compute_logged_overseer', default=False)
  approval_fleet = fields.Selection(APPROVAL_SELECTIONS, string='Fleet\'s Decision', default=None, readonly=True)
  tag_ids = fields.Many2many(comodel_name='fleet.business.tag', relation="fleet_business_trip_tag_rel", column1="fleet_business_trip_id", column2="tag_id", string='Tags')
  journal_line_ids = fields.One2many('fleet.business.trip.journal.line','fleet_business_trip_id',string='Journal Line')
  journal_line_count = fields.Integer('Journal Count', compute='_compute_journal_line_count')

  @api.depends()
  def _compute_logged_overseer(self):
    super(FleetBusinessTrip, self)._compute_logged_overseer()
    for trip in self:
      if self.env.user == trip.overseer_fleet_id.user_id:
        trip.overseer_fleet_logged = True
      else: trip.overseer_fleet_logged = False

  @api.depends('attending_employee_ids','driver_id')
  def _compute_attending_employee_count(self):
    for trip in self:
      if trip.driver_id:
        trip.attending_employee_count = len(trip.attending_employee_ids) + 1
      else:
        trip.attending_employee_count = len(trip.attending_employee_ids)

  @api.depends('journal_line_ids')
  def _compute_journal_line_count(self):
    for trip in self:
      trip.journal_line_count = len(trip.journal_line_ids)

  @api.depends('company_id')
  def _compute_address_id(self):
    for trip in self:
      address = trip.company_id.partner_id.address_get(['default'])
      trip.pick_address_id = address['default'] if address else False

  @api.onchange('driver_id')
  def onchange_attending_employee_ids_exclude_driver(self):
    return {'domain':{ 'attending_employee_ids': [('id', '!=', self.driver_id.id),],}}

  @api.onchange('attending_employee_ids')
  def onchange_self_driving_employee_id_in_attendees(self):
    attending_employee_ids_list = self.attending_employee_ids.ids

    return {'domain': {
      'self_driving_employee_id': [
        ('id', 'in', attending_employee_ids_list)
      ],
      'driver_id': ['&','&','&','&','|',
        ('company_id', '=', False),('company_id', '=', self.company_id.id),
        ('department_id', '=', self.env.ref('fleet_business.dep_fleet').id),
        ('department_position', '=', 'Member'),
        ('job_id', '=', self.env.ref('fleet_business.job_fleet_driver').id),
        ('id', '!=', attending_employee_ids_list),
      ],
    }}

  def action_approval_fleet_approved(self):
    self.ensure_one()
    self.approval_fleet = "approved"

    self.curr_deciding_overseer_id = self.overseer_creator_id.id
    self.curr_deciding_overseer_role = 'Creator'
    self.approval_creator = "deciding"
    self.action_send_email()
  def action_approval_fleet_denied(self):
    self.ensure_one()
    self.approval_fleet = 'denied'
    self.action_send_email(special='request_admin_overseer_cancellation')

    self.curr_deciding_overseer_id = self.overseer_admin_id.id
    self.curr_deciding_overseer_role = 'Administrator'
    self.approval_admin = 'deciding'

  def action_approval_creator_request_rework(self):
    self.ensure_one()
    self.approval_creator = 'denied'
    self.action_send_email(special='request_fleet_overseer_rework')

    self.curr_deciding_overseer_id = self.overseer_fleet_id.id
    self.curr_deciding_overseer_role = 'Fleet Captain'
    self.approval_fleet = 'deciding'
  def action_approval_creator_approved(self):
    super(FleetBusinessTrip, self).action_approval_creator_approved()
    if self.approval_manager == 'approved' and self.approval_admin == 'approved' and self.approval_creator == 'approved' and self.approval_fleet == 'approved':
      self.curr_deciding_overseer_id = None
      self.curr_deciding_overseer_role = None
      self.state = 'approved'
    else: raise exceptions.ValidationError('A approval steps was bugged, please contact the administrator about this bug')

  def action_request_reapproval(self):
    super(FleetBusinessTrip, self).action_request_reapproval()
    self.approval_fleet = None
    self.action_send_email()

  def action_view_fleet(self):
    return {
      'name': _('Fleet'),
      'res_model': 'hr.employee',
      'view_mode': 'form',
      'res_id': self.overseer_fleet_id.id,
      'target': 'current',
      'type': 'ir.actions.act_window',
    }

  def action_view_attendees(self):
    attending_employee_ids_list = self.attending_employee_ids.ids
    if self.driver_id:
      attending_employee_ids_list.append(self.driver_id.id)

    return {
        'name': _('Employees'),
        'res_model': 'hr.employee',
        'view_mode': 'kanban,tree,activity,form',
        'domain': [('id','in',attending_employee_ids_list)],
        'target': 'current',
        'type': 'ir.actions.act_window',
    }

  @api.constrains('self_driving_employee_id','driver_id')
  def _check_driver(self):
    for trip in self:
      if not trip.self_driving_employee_id and not trip.driver_id: 
        raise exceptions.UserError("Must choose either a Company's Driver Or Attendee Driver")
      elif trip.self_driving_employee_id and trip.driver_id: 
        raise exceptions.ValidationError("Please either choose a Company's Driver Or Attendee Driver")

  @api.constrains('attending_employee_count','seats')
  def _check_seats(self):
    for trip in self:
      if trip.attending_employee_count > trip.seats: 
        raise exceptions.UserError("Number of employees can't be more than the seats (driver included)")

  # @api.constrains('overseer_fleet_id')
  # def _check_time(self):
  #   for trip in self:
  #     if not trip.overseer_fleet_id: 
  #       raise exceptions.ValidationError("Overseeing Fleet Captain can't be empty")
class FleetBusinessTripJournalLine(models.Model):
  _inherit = 'fleet.business.journal.line'
  _name = 'fleet.business.trip.journal.line'
  _description = 'Business Trip Journal'

  fleet_business_trip_id = fields.Many2one('fleet.business.trip',readonly=True)