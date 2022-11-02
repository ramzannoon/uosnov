from odoo import http
from odoo.http import content_disposition, Controller, request, route
from datetime import datetime


class HelpdeskTickets(http.Controller):

    @http.route(['/helpdesk/tickets'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def helpdesk_tickets_form(self, **post):
        current_user = http.request.env.user
        # employee_id = request.env['helpdesk.ticket'].sudo().search([('employee_id', '=', current_user.name)])

        department_id = request.env['helpdesk.ticket.team'].sudo().search([])

        data = {
            'department_id': department_id,
            # 'requisition_type':product_id.requisition_type
        }

        return request.render("odoocms_employee_portal.tickets_helpdesk_form", data)


    @http.route(['/helpdesk/tickets/submit'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def helpdesk_tickets_form_submit(self, **post):

        current_user = http.request.env.user
        name = post.get('name')
        priority = post.get('priority')
        description = post.get('description')
        department_id = post.get('department_id')


        helpdesk = request.env['helpdesk.ticket'].sudo().create({
            # 'employee_id': current_user.employee_id.id,
            'name': name,
            'priority': priority,
            'description': description,
            'department_id': department_id,

        })
        return request.render("odoocms_employee_portal.tickets_helpdesk_submit", )


    @http.route(['/helpdesk/tickets/recs'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def helpdesk_tickets_recs(self, **post):
        current_user = http.request.env.user

        return request.render("odoocms_employee_portal.tickets_helpdesk_recs", )




    @http.route(['/helpdesk/tickets/back'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def helpdesk_tickets_back(self, **post):
        return request.redirect('/helpdesk/tickets')


class PurchaseRequests(http.Controller):

    @http.route(['/purchase/request/recs'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def purchase_recs(self, **post):
        return request.render("odoocms_employee_portal.purchase_request_recs")

    @http.route(['/purchase/request/form'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def purchase_request_form(self, **post):
        current_user = http.request.env.user
        product_id = request.env['product.product'].sudo().search([])

        data = {
            'product_id': product_id,
            # 'requisition_type': product_id.requisition_type
        }
        return request.render("odoocms_employee_portal.purchase_request_form_template",data)

    @http.route(['/purchase/request/form/submit'], type='http', auth="user", website=True, method=['GET','POST'], portal=True)
    def purchase_request_form_submit(self, **post):
        picking_type_id = request.env['stock.picking.type'].sudo().search([("name", '=', "Internal Transfers")])
        location_id = request.env['stock.location'].sudo().search([("name", '=', "Stock")])
        location_dest_id = request.env['stock.location'].sudo().search([("name", '=', "Employee Location")])

        product_id = post.get('product_id')
        products_qty_n = post.get('qty')
        picking_type_id = picking_type_id.id
        location_id = location_id.id
        location_dest_id = location_dest_id.id
        scheduled_date = post.get('scheduled_date')
        scheduled_date = post.get('scheduled_date')
        note = post.get('note')
        move_ids_without_package = post.get('move_ids_without_package')
        product_uom_qty = post.get('product_uom_qty')

        products = request.env['stock.move'].sudo().search([('id', '=', move_ids_without_package)])
        products_uom = request.env['product.template'].sudo().search([('id', '=', product_id)])
        purchase = request.env['stock.picking'].sudo().create({
            'picking_type_id': int(picking_type_id),
            'location_id': int(location_id),
            'location_dest_id': int(location_dest_id),
            'partner_id': 2706,
            'note': note,
            'move_lines': [(0, 0, {
                'name': 'pr',
                'product_id': int(product_id),
                'product_uom_qty': int(product_uom_qty),
                'product_uom': products_uom.uom_id.id,
                'location_id': int(location_id),
                'location_dest_id': int(location_dest_id),
                'picking_type_id': int(picking_type_id)
            })]
            # 'requisition_line_ids': list,
        })
        f = 9

        print(1111111111111111111111111111111111111, purchase)
        return request.render("odoocms_employee_portal.purchase_request_form_submit",)

    @http.route(['/purchase/request/form/back'], type='http', auth="user", website=True, method=['GET'], portal=True)
    def purchase_request_back(self, **post):
        return request.redirect('/purchase/request/form')

