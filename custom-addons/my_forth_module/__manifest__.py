{
  'name': 'Hospital Patient',
  'version': '1.1',
  'description': 'module to learn odoo',
  'summary': 'UNFINISHED',
  'author': 'NgoHuuNghia',
  'website': 'www.ngohuunghia.tech',
  'license': 'LGPL-3',
  'category': 'Learning odoo',
  #? pick and choose which modules does this module itself depends on (check in addons file in source and odoo)
  'depends': [
    'base',
    'mail',
    'product',
  ],
  #? importing security rules, views and datas from top to bottom (the lowest will overwrite any collision)
  'data': [
    'security/ir.model.access.csv', #$ security
    'data/sequence_data.xml', #$ sequence
    'data/hospital_patient_tag_data.xml', #$ data
    'data/hospital.patient.tag.csv',
    'wizard/cancel_appointment_view.xml', #$ wizard
    'views/menu.xml', #$ view - menu
    'views/patient_view.xml', #$ view - views
    'views/patient_tag_view.xml',
    'views/female_patient_view.xml',
    'views/appointment_view.xml',
    'views/my_playground_view.xml',
    'views/operation_view.xml',
    'views/res_config_settings_views.xml', #$ view - setting
  ],
  # 'demo': [
    
  # ],
  #? auto install duh!
  'auto_install': False,
  #? Show as a main application on app module
  'application': True,
  #? If main module than make sure it true
  'installable': True,
}