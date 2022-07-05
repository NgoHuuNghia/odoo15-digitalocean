from odoo import models,fields,api

TYPE_SELECTION = [('state','State'),('update','Update'),('approval','Approval'),('special','Special')]

class FleetBusinessJournalLine(models.AbstractModel):
  _name = 'fleet.business.journal.line'
  _description = 'Journal records for a business trip'
  _order = 'id'

  type = fields.Selection(TYPE_SELECTION,required=True)
  note = fields.Text('Journal\'s Note',required=True)
  #? create_date - use the odoo's basefield