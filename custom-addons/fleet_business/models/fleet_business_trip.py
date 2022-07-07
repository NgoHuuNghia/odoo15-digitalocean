# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]

class FleetBusinessTrip(models.Model):
  _name = 'fleet.business.trip'
  _description = "Business Trip"
  _inherit = ['fleet.business.base']

  @api.model
  def create(self, vals_list):
    vals_list['name'] = self.env['ir.sequence'].next_by_code('fleet.business.trip')
    return super(FleetBusinessTrip, self).create(vals_list)

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
  overseer_fleet_id = fields.Many2one('hr.employee',string='Fleet Captain',
    default=lambda self: self.env['hr.employee'].search([('department_id.name','=','Fleet'),('department_position','=','Manager')],limit=1),
    domain="['&','&','&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Fleet'),('department_position', 'in', ['Manager','Vice Manager']),('job_title', '=', 'Fleet Captain')]")
  overseer_fleet_work_phone = fields.Char(related='overseer_fleet_id.work_phone',string='Fleet\'s Work Phone')
  overseer_fleet_email = fields.Char(related='overseer_fleet_id.work_email',string='Fleet\'s Work Email')
  approval_fleet = fields.Selection(APPROVAL_SELECTIONS, string='Fleet\'s Decision', default='deciding', readonly=True)
  tag_ids = fields.Many2many(comodel_name='fleet.business.tag', relation="fleet_business_trip_tag_rel", column1="fleet_business_trip_id", column2="tag_id", string='Tags')
  journal_line_ids = fields.One2many('fleet.business.trip.journal.line','fleet_business_trip_id',string='Journal Line')
  journal_line_count = fields.Integer('Journal Count', compute='_compute_journal_line_count')

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
    return {'domain':{
      'attending_employee_ids': [
        ('id', '!=', self.driver_id.id),
      ],
    }}

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

  #? automated code, still figuring it out
  def action_create_first_journal(self):
    print('hello')
    curr_id = self.env['fleet.business.trip'].search([('id', '!=', False)], limit=1, order="id desc").id

    first_journal_val_list = {
      'fleet_business_trip_id': curr_id,
      'type': 'update',
      'note': f'{self.env.user.employee_id.name} have successfully created this trip, now awaiting approval.'
    }
    self.env['fleet.business.trip.journal.line'].create(first_journal_val_list)

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

class FleetBusinessTripJournalLine(models.Model):
  _inherit = 'fleet.business.journal.line'
  _name = 'fleet.business.trip.journal.line'
  _description = 'Business Trip Journal'

  fleet_business_trip_id = fields.Many2one('fleet.business.trip',readonly=True)