from odoo import models, api, fields
from odoo.tools.safe_eval import safe_eval

# $ This whole module is just a playground to explain wtf is odoo's environment [self.env]
class MyPlayground(models.Model):
  _name = 'my.playground'
  _description = 'Learning playground'

  DEFAULT_ENV_VARIABLES = """# available varibles
  # also the class is declared in [source]/odoo/api.py check it for all the functions
  # - self: Current Object/record set where the code execute happens
  # - self.env: Odoo Enviroment on which the action is triggered
  # - self.env.user: Return the current user (as an instance)
  # - self.env.is_system: Return whether the current user has group "Setting", or is in superuser mode.
  # - self.env.is_admin: Return whether the current user has a group "Access Rights", or is in superuser mode.
  # - self.env.is_superuser: Return whether the enviromment is in superuser mode.
  # - self.env.company: Return the current company (as an instance)
  # - self.env.companies: Return a recordset of the enabled companies by the user
  # - self.env.lange: Return the current language code \n\n
  """
  model_id = fields.Many2one(comodel_name='ir.model', string='Model')
  code = fields.Text(string='Code', default=DEFAULT_ENV_VARIABLES)
  result = fields.Text(string='Result')

  def action_execute(self):
    try:
      if self.model_id:
        model = self.env[self.model_id.model]
      else:
        model = self
      self.result = safe_eval(self.code.strip(), {'self':model})
    except Exception as e:
      self.result = str(e)