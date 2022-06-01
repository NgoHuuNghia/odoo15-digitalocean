{
  'name': 'Hospital Patient',
  'version': '0.9',
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
    'security/ir.model.access.csv',
    'data/sequence_data.xml',
    'data/hospital_patient_tag_data.xml',
    'data/hospital.patient.tag.csv',
    'wizard/cancel_appointment_view.xml',
    'views/menu.xml',
    'views/patient_view.xml',
    'views/patient_tag_view.xml',
    'views/female_patient_view.xml',
    'views/appointment_view.xml',
  ],
  'demo': [
    
  ],
  #? auto install duh!
  'auto_install': False,
  #? Show as a main application on app module
  'application': True,
  #? If main module than make sure it true
  'installable': True,
}