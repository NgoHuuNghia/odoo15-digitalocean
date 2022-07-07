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
    'category': 'Human Resources/Services',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base_automation','fleet','mail','hr','hr_addons'],

    # always loaded
    'data': [
        'security/fleet_business_security.xml', #$ Security
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml', #$ Sequence
        'data/hr_department_data.xml', #$ Data
        'data/hr_job_data.xml',
        'data/fleet_business_tag_data.xml',
        'demo/hr_employee_demo.xml', #$ Demo
        'demo/hr_department_demo.xml',
        'demo/fleet_vehicle_demo.xml',
        'data/fleet_business_trip_automated.xml',#$ Automation
        'views/fleet_business_menu_views.xml', #$ Menu
        'views/fleet_business_tag_views.xml', #$ Views
        'views/fleet_vehicle_views.xml',
        'views/hr_employee_views.xml',
        'views/fleet_business_trip_views.xml',
    ],
    #! only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
