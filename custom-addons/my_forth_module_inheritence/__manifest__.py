# -*- coding: utf-8 -*-
# $ using the odoo's cli command [python .\odoo-bin scaffold my_forth_module_inheritence .\addons] we can create a base module
{
    'name': "my_forth_module_inheritence",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'NgoHuuNghia',
    'website': 'www.ngohuunghia.tech',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    #? auto install duh!
    'auto_install': False,
    #? Show as a main application on app module
    'application': True,
    #? If main module than make sure it true
    'installable': True,
}
