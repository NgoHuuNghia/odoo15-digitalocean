# -*- coding: utf-8 -*-
# from odoo import http


# class HrAddons(http.Controller):
#     @http.route('/hr_addons/hr_addons', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_addons/hr_addons/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_addons.listing', {
#             'root': '/hr_addons/hr_addons',
#             'objects': http.request.env['hr_addons.hr_addons'].search([]),
#         })

#     @http.route('/hr_addons/hr_addons/objects/<model("hr_addons.hr_addons"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_addons.object', {
#             'object': obj
#         })
