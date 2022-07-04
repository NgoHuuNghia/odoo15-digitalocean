# -*- coding: utf-8 -*-
{
    'name': "Fleet Business",

    'summary': """
        Inherit the fleet module to create a business trip
        managing module, support company's cars and buying tickets for travels""",

    'description': """
        Inherit the fleet module to create a business trip
        managing module, support company's cars and buying tickets for travels
    """,

    'author': "Ngô Hữu Nghĩa",
    'website': "https://github.com/NgoHuuNghia/odoo15-digitalocean/tree/learning",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Fleet/Services/Appraisals',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','hr','hr_addons'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_business_menu_views.xml',
        'views/fleet_business_trip_views.xml',
        'views/fleet_business_tag_views.xml',
        'views/fleet_vehicle_views.xml',
        'data/ir_sequence_data.xml',
        'data/hr_department_data.xml',
        'data/hr_job_data.xml',
        'data/fleet_business_tag_data.xml',
        'demo/hr_employee_demo.xml',
        'demo/hr_department_data.xml',
    ],
    #! only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
