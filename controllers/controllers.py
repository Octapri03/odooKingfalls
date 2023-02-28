# -*- coding: utf-8 -*-
# from odoo import http


# class Kingfalls(http.Controller):
#     @http.route('/kingfalls/kingfalls', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kingfalls/kingfalls/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kingfalls.listing', {
#             'root': '/kingfalls/kingfalls',
#             'objects': http.request.env['kingfalls.kingfalls'].search([]),
#         })

#     @http.route('/kingfalls/kingfalls/objects/<model("kingfalls.kingfalls"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kingfalls.object', {
#             'object': obj
#         })
