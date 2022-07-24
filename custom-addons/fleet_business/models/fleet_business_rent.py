# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]
class FleetBusinessTrip(models.Model):
  _inherit = ['fleet.business.base']
  _name = 'fleet.business.rent'
  _description = "Supported Business Trip"

  name = fields.Char('Sequence Name',readonly=True)
  attending_employee_ids = fields.Many2many(comodel_name='hr.employee.public', relation='fleet_business_rent_employees_rel', 
    column1='business_rent_id', column2='employee_id', string='Attending Employees', required=True)
  attending_employee_count = fields.Integer(string="Attendees Count", compute="_compute_attending_employee_count", store=True)
  pick_address_id = fields.Many2one('res.partner','Pick Up Company',compute='_compute_address_id', store=True, readonly=False,
    #! domain="[('is_company', '=', True),('company_id','!=',False)]" for just company in the system, but need work
    domain="[('is_company', '=', True)]"
  )
  pick_stations_address_id = fields.Many2one('res.partner','Pick Up Station',compute='_compute_address_id', store=True, readonly=False, domain="[('is_company', '=', True)]")
  journal_line_ids = fields.One2many('fleet.business.rent.journal.line','fleet_business_rent_id',string='Journal Line')
  journal_line_count = fields.Integer('Journal Count', compute='_compute_journal_line_count')

  @api.depends('attending_employee_ids')
  def _compute_attending_employee_count(self):
    for trip in self: trip.attending_employee_count = len(trip.attending_employee_ids)

  @api.depends('company_id')
  def _compute_address_id(self):
    for trip in self:
      address = trip.company_id.partner_id.address_get(['default'])
      trip.pick_address_id = address['default'] if address else False

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

class FleetBusinessTripJournalLine(models.Model):
  _inherit = 'fleet.business.journal.line'
  _name = 'fleet.business.rent.journal.line'
  _description = 'Supported Business Trips Journal'

  fleet_business_rent_id = fields.Many2one('fleet.business.rent',readonly=True)