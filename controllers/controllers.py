# -*- coding: utf-8 -*-
# from odoo import http


# class ZeroInvoicedCustomers(http.Controller):
#     @http.route('/zero_invoiced_customers/zero_invoiced_customers', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zero_invoiced_customers/zero_invoiced_customers/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('zero_invoiced_customers.listing', {
#             'root': '/zero_invoiced_customers/zero_invoiced_customers',
#             'objects': http.request.env['zero_invoiced_customers.zero_invoiced_customers'].search([]),
#         })

#     @http.route('/zero_invoiced_customers/zero_invoiced_customers/objects/<model("zero_invoiced_customers.zero_invoiced_customers"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zero_invoiced_customers.object', {
#             'object': obj
#         })
