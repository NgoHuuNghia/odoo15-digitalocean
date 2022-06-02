# -*- coding: utf-8 -*-
# from odoo import http


# class MySecondModule(http.Controller):
#     @http.route('/my_second_module/my_second_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_second_module/my_second_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_second_module.listing', {
#             'root': '/my_second_module/my_second_module',
#             'objects': http.request.env['my_second_module.my_second_module'].search([]),
#         })

#     @http.route('/my_second_module/my_second_module/objects/<model("my_second_module.my_second_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_second_module.object', {
#             'object': obj
#         })
