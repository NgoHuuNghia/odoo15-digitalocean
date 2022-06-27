# -*- coding: utf-8 -*-
{
    'name': "Fleet Business",

    'summary': """
        Inherit both the employee and fleet module to create a business trip
        manager module, support company's cars and buying tickets for travels""",

    'description': """
        Inherit both the employee and fleet module to create a business trip
        manager module, support company's cars and buying tickets for travels
    """,

    'author': "Ngô Hữu Nghĩa",
    'website': "https://github.com/NgoHuuNghia/odoo15-digitalocean/tree/learning",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Fleet/Services/Appraisals',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
