# -*- coding: utf-8 -*-

from email.policy import default
from tokenize import String
from odoo import models, fields, api, exceptions, _

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]
TRANSPORTATION_SELECTIONS = [('plane','Plane'),('ship','Ship'),('train','Train')]
TICKET_TYPE_SELECTIONS = [('going','Going'),('returning','Returning'),('two_way','Two way')]
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
  going_ticket_ids = fields.One2many('fleet.business.rent.ticket','fleet_business_rent_id',string='Going Tickets',domain=[('type', '=', 'going')])
  returning_ticket_ids = fields.One2many('fleet.business.rent.ticket','fleet_business_rent_id',string='Returning Tickets',domain=[('type', '=', 'returning')])
  two_way_ticket_ids = fields.One2many('fleet.business.rent.ticket','fleet_business_rent_id',string='Two Way Tickets',domain=[('type', '=', 'two_way')])
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

  def action_update_state_returned(self):
    if self.env.user.employee_id.id == self.overseer_admin_id.id:
      self.state = 'returned'
    else: raise exceptions.UserError('You are not authorized to confirm returned')

  def action_prepare_going_and_returning_ticket_template(self):
    if self.env.user.employee_id.id != self.overseer_admin_id.id:
      raise exceptions.UserError('You are not authorized for this')
    ticket_list = []
    for attendee in self.attending_employee_ids:
      ticket_list.append([
        {
          'type': 'going',
          f"{self._name.replace('.','_')}_id": self.id,
          "attendee_id": attendee.id,
        },
        {
          'type': 'returning',
          f"{self._name.replace('.','_')}_id": self.id,
          "attendee_id": attendee.id,
        }
      ])
    self.env['fleet.business.rent.ticket'].create(ticket_list)

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
class FleetBusinessRentBaseTicket(models.Model):
  _name = 'fleet.business.rent.ticket'
  _description = 'Tickets that belong to business rent, distinguish by type'

  type = fields.Selection(TICKET_TYPE_SELECTIONS,'type Of ticket')
  name = fields.Char("Ticket's Serial")
  fleet_business_rent_id = fields.Many2one('fleet.business.rent',required=True)
  attendee_id = fields.Many2one('hr.employee.public', string="Ticket's Owner",required=True)
  ready = fields.Boolean('Ticket Readiness',readonly=True,default=False)
  #! ticket_pdf = fields.Image Maybe print a pdf of the ticket

# class FleetBusinessRentGoingTicket(models.Model):
#   _inherit = 'fleet.business.rent.base.ticket'
#   _name = 'fleet.business.rent.going.ticket'
class FleetBusinessRentJournalLine(models.Model):
  _inherit = 'fleet.business.journal.line'
  _name = 'fleet.business.rent.journal.line'
  _description = 'Supported Business Trips Journal'

  fleet_business_rent_id = fields.Many2one('fleet.business.rent',readonly=True)