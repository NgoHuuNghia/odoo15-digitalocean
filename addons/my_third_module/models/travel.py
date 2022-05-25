from odoo import models, fields, api

class Travel(models.Model):
  _name = 'travel.travel'

  name = fields.Char(string="Name")
  destination = fields.Char(string="Destination")
  start_date = fields.Date(string="Start date")
  end_date = fields.Date(string="End date")