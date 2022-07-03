# -*- coding: utf-8 -*-

from odoo import models, fields

class FleetBusinessTag(models.Model):
    _name = 'fleet.business.tag'
    _description = 'Business Tag'

    name = fields.Char('Tag Name', required=True, trim=False)
    active = fields.Boolean('Active', default=True, copy=False)
    color = fields.Integer('Color Index')

    _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists !")]