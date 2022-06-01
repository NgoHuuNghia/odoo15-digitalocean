# -*- coding: utf-8 -*-
# from odoo import http


# class MyForthModuleInheritence(http.Controller):
#     @http.route('/my_forth_module_inheritence/my_forth_module_inheritence', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_forth_module_inheritence/my_forth_module_inheritence/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_forth_module_inheritence.listing', {
#             'root': '/my_forth_module_inheritence/my_forth_module_inheritence',
#             'objects': http.request.env['my_forth_module_inheritence.my_forth_module_inheritence'].search([]),
#         })

#     @http.route('/my_forth_module_inheritence/my_forth_module_inheritence/objects/<model("my_forth_module_inheritence.my_forth_module_inheritence"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_forth_module_inheritence.object', {
#             'object': obj
#         })
