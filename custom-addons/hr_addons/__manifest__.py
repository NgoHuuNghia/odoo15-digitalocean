# -*- coding: utf-8 -*-
{
    'name': "HR business addons",

    'summary': """
        Inherit both the employee module to expand on it
        better suit for my current project""",

    'description': """
        Inherit both the employee module to expand on it
        better suit for my current project
    """,

    'author': "Ngô Hữu Nghĩa",
    'website': "https://github.com/NgoHuuNghia/odoo15-digitalocean/tree/learning",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        # 'views/res_user_views.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'auto_install': True,
    'installable': True,
    # 'application': True,
}
