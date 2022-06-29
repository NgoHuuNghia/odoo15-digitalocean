from odoo import models,fields,api

TYPE_SELECTION = [('state','State'),('update','Update'),('approval','Approval'),('special','Special')]

class FleetBusinessJournalLine(models.Model):
  _name = 'fleet.business.journal.line'
  _description = 'Journal records for a business trip'

  name = fields.Char('Journal Sequence')
  fleet_business_base_id = fields.Many2one('fleet.business.base',readonly=True)
  type = fields.Selection(TYPE_SELECTION,required=True)
  note = fields.Text('Journal\'s Note')
  #? create_date - use the odoo's basefield