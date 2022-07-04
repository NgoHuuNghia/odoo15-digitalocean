# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

APPROVAL_SELECTIONS = [('deciding','Deciding'),('denied','Denied'),('approved','Approved')]

class FleetBusinessTrip(models.Model):
  _name = 'fleet.business.trip'
  _description = "Model for creating and supervising a business trip with a company's car"
  _inherit = ['fleet.business.base']

  name = fields.Char('Sequence Name',readonly=True)
  attending_employee_ids = fields.Many2many(comodel_name='hr.employee', relation='fleet_business_trip_employees_rel', 
    column1='business_trip_id', column2='employee_id', string='Attending Employees')
  attending_employee_count = fields.Integer(string="Attendees Count", compute="_compute_attending_employee_count", store=True)
  pick_address_id = fields.Many2one('res.partner','Pick Up Company',compute='_compute_address_id', store=True, readonly=False,
    #! domain="['&',('is_company', '=', True),('company_id', '!=', None)]"
    #! working on domain that filter only system's company (res.company)
    domain="[('is_company', '=', True)]"
  )
  vehicle_id = fields.Many2one('fleet.vehicle','Vehicle Used')
  model_id = fields.Many2one(related='vehicle_id.model_id',string='Model')
  license_plate = fields.Char(related='vehicle_id.license_plate',string='License Plate')
  seats = fields.Integer(related='vehicle_id.seats',string='Seats')
  self_driving_employee_id = fields.Many2one('hr.employee',string='Self Driver',domain="[('id', 'in', attending_employee_ids)]")
  driver_id = fields.Many2one('hr.employee',string="Company's Driver",domain="['&','&','&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Fleet'),('department_position', '=', 'Member'),('job_title', '=', 'Driver')]")
  overseer_fleet_id = fields.Many2one('hr.employee',string='Fleet Captain',
    default=lambda self: self.env['hr.employee'].search([('department_id.name','=','Fleet'),('department_position','=','Manager')],limit=1),
    domain="['&','&','&','|',('company_id', '=', False),('company_id', '=', company_id),('department_id.name', '=', 'Fleet'),('department_position', 'in', ['Manager','Vice Manager']),('job_title', '=', 'Fleet Captain')]")
  overseer_fleet_work_phone = fields.Char(related='overseer_fleet_id.work_phone',string='Fleet\'s Work Phone')
  overseer_fleet_email = fields.Char(related='overseer_fleet_id.work_email',string='Fleet\'s Work Email')
  approval_fleet = fields.Selection(APPROVAL_SELECTIONS, string='Fleet\'s Decision', default='deciding', readonly=True)
  tag_ids = fields.Many2many(comodel_name='fleet.business.tag', relation="fleet_business_trip_tag_rel", column1="fleet_business_trip_id", column2="tag_id", string='Tags')
  journal_line_ids = fields.One2many('fleet.business.trip.journal.line','fleet_business_trip_id',string='Journal Line')
  journal_line_count = fields.Integer('Journal Count', compute='_compute_journal_line_count')

  @api.model
  def create(self, vals_list):
    vals_list['name'] = self.env['ir.sequence'].next_by_code('fleet.business.trip')
    return super(FleetBusinessTrip, self).create(vals_list)

  @api.depends('attending_employee_ids')
  def _compute_attending_employee_count(self):
    for trip in self:
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

  def action_view_attendees(self):
    return {
        'name': _('Employees'),
        'res_model': 'hr.employee',
        'view_mode': 'kanban,tree,activity,form',
        #? 'context': {'default_id':self.id},
        'domain': [('id','in',self.attending_employee_ids.ids)],
        'target': 'current',
        'type': 'ir.actions.act_window',
    }

  @api.onchange('attending_employee_ids')
  def onchange_product_list(self):
    return {'domain': {'self_driving_employee_id': [
      ('id', 'in', self.attending_employee_ids.ids)
    ]}}

  #$ a method to run a function on view load, just not getting it to work yet
  # @api.model
  # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
  #   res = super(FleetBusinessTrip, self).fields_view_get(view_id=view_id, view_type=view_type, 
  #     toolbar=toolbar, submenu=submenu)
  #   # Write your code here which should be executed on view load
  #   res['fields']['self_driving_employee_id']['domain'] = [('id', 'in', self.attending_employee_ids.ids)]
  #   print('--------res=',res['fields'])
  #   return res

class FleetBusinessTripJournalLine(models.Model):
  _inherit = 'fleet.business.journal.line'
  _name = 'fleet.business.trip.journal.line'

  fleet_business_trip_id = fields.Many2one('fleet.business.trip',readonly=True)