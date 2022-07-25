# -*- coding: utf-8 -*-

from email.policy import default
from tokenize import String
from odoo import models, fields, api, exceptions, _

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]
TRANSPORTATION_SELECTIONS = [('plane','Plane'),('ship','Ship'),('train','Train')]
class FleetBusinessRent(models.Model):
  _inherit = ['fleet.business.base']
  _name = 'fleet.business.rent'
  _description = "Supported Business Trip"
  
  @api.model
  def create(self, vals_list):
    vals_list['approval_manager'] = 'deciding'
    vals_list['name'] = self.env['ir.sequence'].next_by_code(self._name)
    vals_list['state'] = 'draft'
    return super(FleetBusinessRent, self).create(vals_list)

  name = fields.Char('Sequence Name',readonly=True)
  #! gonna need to make attending_employee_ids to be readonly after creation
  attending_employee_ids = fields.Many2many(comodel_name='hr.employee.public', relation='fleet_business_rent_employees_rel', 
    column1='business_rent_id', column2='employee_id', string='Attending Employees', required=True)
  attending_employee_count = fields.Integer(string="Attendees Count", compute="_compute_attending_employee_count", store=True)
  pick_station_address_id = fields.Many2one('res.partner','Pick Up Station', store=True, domain="[('is_company', '=', True)]")
  to_country_id = fields.Many2one(comodel_name='res.country', string='To Country')
  drop_off_station_street = fields.Char('Station Street 1')
  drop_off_station_street2 = fields.Char('Station Street 2')
  drop_off_station_zip = fields.Char('Station Country\'s Zip Code',change_default=True)
  drop_off_station_city = fields.Char('Station City')
  drop_off_station_state_id = fields.Many2one("res.country.state", string='Station State/Province', domain="[('country_id', '=?', drop_off_station_country_id)]")
  drop_off_station_country_id = fields.Many2one(comodel_name='res.country', string='Station Country')
  type_of_transportation = fields.Selection(TRANSPORTATION_SELECTIONS,'Type Of Transportation',required=True)
  going_ticket_ids = fields.One2many('fleet.business.rent.going.ticket','fleet_business_rent_id',string='Going Tickets')
  going_ticket_count = fields.Integer(string='Going Ticket Count',compute='_compute_going_ticket_count')
  returning_ticket_ids = fields.One2many('fleet.business.rent.returning.ticket','fleet_business_rent_id',string='Returning Tickets')
  returning_ticket_count = fields.Integer(string='Returning Ticket Count',compute='_compute_returning_ticket_count')
  two_way_ticket_ids = fields.One2many('fleet.business.rent.two.way.ticket','fleet_business_rent_id',string='Two Way Tickets')
  two_way_ticket_count = fields.Integer(string='Two Way Ticket Count',compute='_compute_two_way_ticket_count')
  journal_line_ids = fields.One2many('fleet.business.rent.journal.line','fleet_business_rent_id',string='Journal Line')
  journal_line_count = fields.Integer('Journal Count', compute='_compute_journal_line_count')
  tag_ids = fields.Many2many(comodel_name='fleet.business.tag', relation="fleet_business_rent_tag_rel", column1="fleet_business_rent_id", column2="tag_id", string='Tags')

  @api.depends('attending_employee_ids')
  def _compute_attending_employee_count(self):
    for trip in self: trip.attending_employee_count = len(trip.attending_employee_ids)

  @api.depends('journal_line_ids')
  def _compute_journal_line_count(self):
    for trip in self:
      trip.journal_line_count = len(trip.journal_line_ids)

  @api.depends('going_ticket_ids')
  def _compute_going_ticket_count(self):
    for trip in self:
      trip.going_ticket_count = len(trip.going_ticket_ids)
  @api.depends('returning_ticket_ids')
  def _compute_returning_ticket_count(self):
    for trip in self:
      trip.returning_ticket_count = len(trip.returning_ticket_ids)
  @api.depends('two_way_ticket_ids')
  def _compute_two_way_ticket_count(self):
    for trip in self:
      trip.two_way_ticket_count = len(trip.two_way_ticket_ids)

  def action_update_state_returned(self):
    if self.env.user.employee_id.id == self.overseer_admin_id.id:
      self.state = 'returned'
    else: raise exceptions.UserError('You are not authorized to confirm returned')

  def action_prepare_going_and_returning_ticket_template(self):
    if self.env.user.employee_id.id != self.overseer_admin_id.id:
      raise exceptions.UserError('You are not authorized for this')
    if self.two_way_ticket_count >= 1:
      self.two_way_ticket_ids.unlink()
    ticket_list = []
    for attendee in self.attending_employee_ids:
      ticket_list.append({
        f"{self._name.replace('.','_')}_id": self.id,
        "attendee_id": attendee.id,
      })
    self.going_ticket_ids.create(ticket_list)
    self.returning_ticket_ids.create(ticket_list)
  def action_prepare_two_way_ticket_template(self):
    if self.env.user.employee_id.id != self.overseer_admin_id.id:
      raise exceptions.UserError('You are not authorized for this')
    if self.going_ticket_count >= 1:
      self.going_ticket_ids.unlink()
    if self.returning_ticket_count >= 1:
      self.returning_ticket_ids.unlink()
    ticket_list = []
    for attendee in self.attending_employee_ids:
      ticket_list.append({
        f"{self._name.replace('.','_')}_id": self.id,
        "attendee_id": attendee.id,
      })
    self.two_way_ticket_ids.create(ticket_list)

  def action_approval_admin_approved(self):
    super(FleetBusinessRent, self).action_approval_admin_approved()
    self.curr_deciding_overseer_id = self.overseer_creator_id.id
    self.curr_deciding_overseer_role = 'Creator'
    self.approval_creator = "deciding"
    self.action_send_email()
    
  def action_approval_creator_approved(self):
    super(FleetBusinessRent, self).action_approval_creator_approved()
    if self.approval_manager == 'approved'\
    and self.approval_admin == 'approved'\
    and self.approval_creator == 'approved':
      self.curr_deciding_overseer_id = None
      self.curr_deciding_overseer_role = None
      self.state = 'approved'
      self.action_send_email_mass()
    else: raise exceptions.ValidationError('A approval steps was bugged, please contact the administrator about this bug')

  def action_view_attendees(self):
    attending_employee_ids_list = self.attending_employee_ids.ids

    return {
        'name': _('Employees'),
        'res_model': 'hr.employee.public',
        'view_mode': 'kanban,tree,activity,form',
        'domain': [('id','in',attending_employee_ids_list)],
        'target': 'current',
        'type': 'ir.actions.act_window',
    }
class FleetBusinessRentBaseTicket(models.TransientModel):
  _name = 'fleet.business.rent.base.ticket'
  _description = 'Base Tickets that belong to business rent'

  name = fields.Char("Ticket's Serial")
  fleet_business_rent_id = fields.Many2one('fleet.business.rent',required=True)
  attendee_id = fields.Many2one('hr.employee.public', string="Ticket's Owner",required=True)
  ready = fields.Boolean('Ticket Readiness',readonly=True,default=False)
  #! ticket_pdf = fields.Image Maybe print a pdf of the ticket
class FleetBusinessRentGoingTicket(models.Model):
  _inherit = 'fleet.business.rent.base.ticket'
  _name = 'fleet.business.rent.going.ticket'
  _description = 'Going Tickets that belong to business rent'
class FleetBusinessRentReturningTicket(models.Model):
  _inherit = 'fleet.business.rent.base.ticket'
  _name = 'fleet.business.rent.returning.ticket'
  _description = 'Returning Tickets that belong to business rent'
class FleetBusinessRentTwoWayTicket(models.Model):
  _inherit = 'fleet.business.rent.base.ticket'
  _name = 'fleet.business.rent.two.way.ticket'
  _description = 'Two Way Tickets that belong to business rent'
class FleetBusinessRentJournalLine(models.Model):
  _inherit = 'fleet.business.journal.line'
  _name = 'fleet.business.rent.journal.line'
  _description = 'Supported Business Trips Journal'

  fleet_business_rent_id = fields.Many2one('fleet.business.rent',readonly=True)