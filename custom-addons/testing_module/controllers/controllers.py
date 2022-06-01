# -*- coding: utf-8 -*-
# from odoo import http


# class TestingModule(http.Controller):
#     @http.route('/testing_module/testing_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/testing_module/testing_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('testing_module.listing', {
#             'root': '/testing_module/testing_module',
#             'objects': http.request.env['testing_module.testing_module'].search([]),
#         })

#     @http.route('/testing_module/testing_module/objects/<model("testing_module.testing_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('testing_module.object', {
#             'object': obj
#         })
