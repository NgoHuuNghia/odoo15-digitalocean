# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleOrder(models.Model):
  # ? when inheriting a model we don't have to specify a name
  _inherit = ['sale.order']
  _description = 'inheriting sale.order model from sale module'

  confirmed_user_id = fields.Many2one('res.users', string='Confirm Users')

  # ? using the super class we can inherit a function from origintal model
  def action_confirm(self):
    super(SaleOrder, self).action_confirm()
    self.confirmed_user_id = self.env.user.id

  #? 149 how to inherit a function from sale.order add new fields
  def _prepare_invoice(self):
    invoice_vals = super(SaleOrder, self)._prepare_invoice()
    invoice_vals['so_confirm_user_id'] = self.confirmed_user_id.id
    # print('invoice_vals',invoice_vals)

    return invoice_vals