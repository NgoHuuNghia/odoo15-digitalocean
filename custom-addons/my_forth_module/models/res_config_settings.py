# -*- coding: utf-8 -*-

from odoo import fields, models

#?107? as we can see this is a transient model so it won't store data in the database but store else where
class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    #?107? [config_parameter] is necessary for ir.config to add a entry with [module_name.setting_field] into the setting's database
    #? which you can see in odoo's UI in {setting/technical/system parameters}
    cancel_days = fields.Integer(string='Cancel Days', config_parameter='my_forth_module.cancel_days')
