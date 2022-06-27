# -*- coding: utf-8 -*-
# from odoo import http


# class FleetBusiness(http.Controller):
#     @http.route('/fleet_business/fleet_business', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_business/fleet_business/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_business.listing', {
#             'root': '/fleet_business/fleet_business',
#             'objects': http.request.env['fleet_business.fleet_business'].search([]),
#         })

#     @http.route('/fleet_business/fleet_business/objects/<model("fleet_business.fleet_business"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_business.object', {
#             'object': obj
#         })
