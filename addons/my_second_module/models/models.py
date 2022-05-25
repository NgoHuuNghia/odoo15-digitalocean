# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
  _inherit = 'sale.order'

  spokenToClient = fields.Boolean("Spoken to client", required=True)