from odoo.tests import common

class MyFirstTest(common.TransactionCase):
  def test_first(self):
    print('test self', self)