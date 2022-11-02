# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class PurchaseRequisitionWiz(models.TransientModel):
    _name = 'purchase.req.wiz'

    def _compute_vendor_ids(self):
        purchase_req = self.env[self._context.get('active_model')].sudo().search([('id', '=', self._context.get('active_id'))])
        if purchase_req:
            list = []
            for line in purchase_req.requisition_line_ids:
                list.append(line.partner_id.id)
            return list

    vendor_ids = fields.Many2many('res.partner', string='Vendors', default=_compute_vendor_ids)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    partner_ids = fields.Many2many('res.partner', 'partner_ids_res_partner_rel', column1='vendor_id',
                                   column2='partner_id', required=True, string='Partners')

    @api.model
    def _prepare_po_line(self, vendor=False, purchase_order=False, requisition=False):
        lines_list = []
        for line in requisition.filtered(lambda l: l.partner_id == vendor):
            po_line_vals = {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_qty': line.qty,
                'product_uom': line.uom.id,
                'warranty': line.warranty,
                'date_planned': fields.Date.today(),
                'price_unit': line.cost_price,
                'order_id': purchase_order.id,
                'custom_requisition_line_id': line.id
            }
            lines_list.append(po_line_vals)

        return lines_list

    def request_stock(self):
        purchase_req = self.env[self._context.get('active_model')].sudo().search(
            [('id', '=', self._context.get('active_id'))])

        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']

        po_dict = {}
        for partner in self.partner_ids:
            if partner not in po_dict:
                notes = ''
                for line in purchase_req.requisition_line_ids:
                    if line.partner_id.id == partner.id:
                        purchase_req_line = line
                        notes += line.terms_and_conditions + '\n'

                po_vals = {
                    'partner_id': partner.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'date_order': fields.Date.today(),
                    'company_id': self.env.company.id,
                    'custom_requisition_id': purchase_req.id,
                    'origin': purchase_req.name,
                    'notes': notes,
                }
                purchase_order = purchase_obj.create(po_vals)
                po_dict.update({partner: purchase_order})

                po_line_vals = self._prepare_po_line(partner, purchase_order, purchase_req.requisition_line_ids)
                purchase_line_obj.sudo().create(po_line_vals)
            else:
                purchase_order = po_dict.get(partner)
                po_line_vals = self._prepare_po_line(line, purchase_order)
                purchase_line_obj.sudo().create(po_line_vals)
        purchase_req.state = 'stock'
