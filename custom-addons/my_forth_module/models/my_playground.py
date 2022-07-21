from odoo import models, api, fields
from odoo.tools.safe_eval import safe_eval

# $ This whole module is just a playground to explain wtf is odoo's environment [self.env]
class MyPlayground(models.Model):
  _name = 'my.playground'
  _description = 'Learning playground'

  # ? remember [DEFAULT_ENV_VARIABLES] is not a field just a python varible
  DEFAULT_ENV_VARIABLES = """# available variables
  ### also the class is declared in [source]/odoo/api.py check it for all the functions
  # - self                                   Current Object/record/record set where the code execute happens
  # - self.browse([id_integer]).[field_name] Use the ORM's browse method to access a specific record with it's id, allowing us to return a field or use a function
  # - self.browse([id_integer]).read()       Read all available fields from a record
  # - self.env[module_name]                  Specify the module name to access it's environment (use the model selection above instead)
  # - self.env.ref([xml_id_from_metadata])   From the environment we can access record/record set with it's external id (so mostly record loaded from xml or csv)
  # - self.env                               Current Odoo Environment class on which the action is triggered
  # - self.env.user                          Return the current user (as an instance)
  # - self.env.is_system                     Return whether the current user has group "Setting", or is in superuser mode.
  # - self.env.is_admin                      Return whether the current user has a group "Access Rights", or is in superuser mode.
  # - self.env.is_superuser                  Return whether the environment is in superuser mode.
  # - self.env.company                       Return the current company (as an instance)
  # - self.env.companies                     Return a recordset of the enabled companies by the user
  # - self.env.lang                          Return the current language code
  # - self.env.cr                            Return the sql cursor class by which let us perform queries operations in postgres
  # - self.env.context                       Return a dictionary of the environment's action context (language,timezone,model(fields,name,...),company,...)
  #
  ### these are ORM methods use for different situations, allowing us to interact with the database in code
  # - self.env['hospital.patient'].create({'name':'test patient', 'gender':'female','age':99}) - hospital.patient(24,)  # Created a new record
  # - self.env['hospital.patient'].browse(24).name - 'test patient'                                                     # Return the record with id, Remember to loop if it a recordset
  # - self.env['hospital.patient'].browse(24).write({'age':999})                                                        # use with browse to update a record or recordset
  # - self.env['hospital.patient'].browse(24).unlink()                                                                  # delete a record or recordset
  # - self.env['hospital.patient'].browse(24).get_metadata()[0].get('xmlid')                                            # get the metadata of a record or recordset as a list
  # - self.env['hospital.patient'].search([('gender','=','male')], limit=5, order='id')                                 # return a recordset with provided conditions
  # - self.env['hospital.patient'].search([]).mapped('name')                                                            # with mapped will return a list of value if normal field or recordset if many relation field
  # - self.env['hospital.patient'].search_count(['|',('gender','=','male'),('gender','=','female')])                    # just like search but return counts instead
  # - self.env['hospital.patient'].browse(24).get_metadata()[0].get('id')                                               # with browse we can get the metadata of any record useful for records created through data files, remember to specify 1st index
  # - self.env['hospital.patient'].fields_get(['name','gender'],['type','float'])                                       # with this method we can get the fields and it properties with 2nd parameter to specify the conditions\n\n"""
  model_id = fields.Many2one(comodel_name='ir.model', string='Model')
  code = fields.Text(string='Code', default=DEFAULT_ENV_VARIABLES)
  result = fields.Text(string='Result')

  # ? button function to print results in the ui
  def action_execute(self):
    try:
      if self.model_id:
        model = self.env[self.model_id.model]
      else:
        model = self
      self.result = safe_eval(self.code.strip(), {'self':model})
    except Exception as e:
      self.result = str(e)

  def action_clear(self):
    self.result = ''