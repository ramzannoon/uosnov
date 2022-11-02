# -*- coding: utf-8 -*-
import time
import json

# from odoo import http

from odoo.addons.web.controllers import main as report
from odoo.http import route, request, content_disposition, serialize_exception
from werkzeug.urls import url_decode
from odoo.tools import safe_eval, html_escape
import pdb


class ReportController(report.ReportController):
	# @http.route([
	# 	'/report/<converter>/<reportname>',
	# 	'/report/<converter>/<reportname>/<docids>',
	# ], type='http', auth='user', website=True)
	@route()
	def report_routes(self, reportname, docids=None, converter=None, **data):
		if converter in ('xml','xls','ppt','pptp','fillpdf','doc','docp'):
			report = request.env['ir.actions.report']._get_report_from_name(reportname)
			context = dict(request.env.context)
			
			if docids:
				docids = [int(i) for i in docids.split(',')]
			if data.get('options'):
				data.update(json.loads(data.pop('options')))
			if data.get('context'):
				# Ignore 'lang' here, because the context in data is the one
				# from the webclient *but* if the user explicitely wants to
				# change the lang, this mechanism overwrites it.
				data['context'] = json.loads(data['context'])
				if data['context'].get('lang'):
					del data['context']['lang']
				context.update(data['context'])
			if converter == 'xml':
				xml = report.with_context(context).render_qweb_xml(docids,data=data)[0]
				xmlhttpheaders = [('Content-Type', 'text/xml'),('Content-Length', len(xml))]
				return request.make_response(xml, headers=xmlhttpheaders)
			elif converter == 'xls':
				xls = report.with_context(context).render_qweb_xls(docids, data=data)
				xlshttpheaders = [('Content-Type', 'application/excel'), ('Content-Length', len(xls))]
				return request.make_response(xls, headers=xlshttpheaders)
			elif converter == 'ppt':
				ppt = report.with_context(context).render_qweb_ppt(docids, data=data)
				ppthttpheaders = [('Content-Type', 'application/powerpoint'), ('Content-Length', len(ppt))]
				return request.make_response(ppt, headers=ppthttpheaders)
			elif converter == 'pptp':
				pdf = report.with_context(context).render_qweb_ppt(docids, data=data)
				pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
				return request.make_response(pdf, headers=pdfhttpheaders)
			elif converter == 'doc':
				ppt = report.with_context(context).render_qweb_doc(docids, data=data)
				ppthttpheaders = [('Content-Type', 'application/word'), ('Content-Length', len(ppt))]
				return request.make_response(ppt, headers=ppthttpheaders)
			elif converter == 'docp':
				pdf = report.with_context(context).render_qweb_doc(docids, data=data)
				pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
				return request.make_response(pdf, headers=pdfhttpheaders)
			elif converter == 'fillpdf':
				pdf = report.with_context(context).render_fillpdf(docids, data=data)[0]
				pdfhttpheaders = [
					('Content-Type', 'application/pdf'),
					('Content-Length', len(pdf)),
					('Content-Disposition', content_disposition(report.report_file + '.pdf'))
				]
				return request.make_response(pdf, headers=pdfhttpheaders)
		else:
			return super().report_routes(reportname, docids, converter, **data)
	
	# @http.route(['/report/download'], type='http', auth="user")
	@route()
	def report_download(self, data, token):
		requestcontent = json.loads(data)
		url, report_type = requestcontent[0], requestcontent[1]
		if report_type == 'qweb-xml':
			try:
				reportname = url.split('/report/xml/')[1].split('?')[0]
				
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')
				
				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='xml')
				else:
					# Particular report:
					# decoding the args represented in JSON
					data = url_decode(url.split('?')[1]).items()
					response = self.report_routes(reportname, converter='xml', **dict(data))
				
				report_obj = request.env['ir.actions.report']
				report = report_obj._get_report_from_name(reportname)
				filename = "%s.xml" % (report.name)
				
				if docids:
					ids = [int(x) for x in docids.split(",")]
					records = request.env[report.model].browse(ids)
					if report.print_report_name and not len(records) > 1:
						report_name = safe_eval(report.print_report_name, {'object': records, 'time': time})
						filename = "{}.xml".format(report_name)
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			except Exception as e:
				se = serialize_exception(e)
				error = {
					'code': 200,
					'message': "Odoo Server Error",
					'data': se
				}
				return request.make_response(html_escape(json.dumps(error)))
		elif report_type == 'qweb-xls':
			try:
				reportname = url.split('/report/pdf/')[1].split('?')[0]
				
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')
				
				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='pdf')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='xls', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "xls")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			except Exception as e:
				se = serialize_exception(e)
				error = {
					'code': 200,
					'message': "Odoo Server Error",
					'data': se
				}
				return request.make_response(html_escape(json.dumps(error)))
		
		elif report_type == 'qweb-ppt':
			try:
				reportname = url.split('/report/pdf/')[1].split('?')[0]
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')
				
				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='ppt')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='ppt', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pptx")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pptx")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			except Exception as e:
				se = serialize_exception(e)
				error = {
					'code': 200,
					'message': "Odoo Server Error",
					'data': se
				}
				return request.make_response(html_escape(json.dumps(error)))
		
		elif report_type == 'qweb-pptp':
			try:
				reportname = url.split('/report/pdf/')[1].split('?')[0]
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')
				
				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='pptp')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='ppt', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pdf")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			except Exception as e:
				se = serialize_exception(e)
				error = {
					'code': 200,
					'message': "Odoo Server Error",
					'data': se
				}
				return request.make_response(html_escape(json.dumps(error)))
		elif report_type == 'qweb-doc':
			try:
				reportname = url.split('/report/pdf/')[1].split('?')[0]
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')
				
				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='doc')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='doc', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "docx")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "docx")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			except Exception as e:
				se = serialize_exception(e)
				error = {
					'code': 200,
					'message': "Odoo Server Error",
					'data': se
				}
				return request.make_response(html_escape(json.dumps(error)))
		
		elif report_type == 'qweb-docp':
			try:
				reportname = url.split('/report/docp/')[1].split('?')[0]
				docids = None
				if '/' in reportname:
					reportname, docids = reportname.split('/')
				
				if docids:
					# Generic report:
					response = self.report_routes(reportname, docids=docids, converter='docp')
				else:
					# Particular report:
					data = url_decode(url.split('?')[1]).items()  # decoding the args represented in JSON
					response = self.report_routes(reportname, converter='doc', **dict(data))
				
				report = request.env['ir.actions.report']._get_report_from_name(reportname)
				filename = "%s.%s" % (report.name, "pdf")
				if docids:
					ids = [int(x) for x in docids.split(",")]
					obj = request.env[report.model].browse(ids)
					if report.print_report_name and not len(obj) > 1:
						report_name = safe_eval(report.print_report_name, {'object': obj, 'time': time})
						filename = "%s.%s" % (report_name, "pdf")
				response.headers.add('Content-Disposition', content_disposition(filename))
				response.set_cookie('fileToken', token)
				return response
			except Exception as e:
				se = serialize_exception(e)
				error = {
					'code': 200,
					'message': "Odoo Server Error",
					'data': se
				}
				return request.make_response(html_escape(json.dumps(error)))
		else:
			return super(ReportController, self).report_download(data, token)


# @route([
	# 	'/zebra/report/<converter>/<reportname>',
	# 	'/zebra/report/<converter>/<reportname>/<docids>',
	# ], type='json')
	# def report_routes_cusrome(self, reportname, docids=None, **data):
	# 	context = dict(request.env.context)
	# 	if docids:
	# 		docids = [int(i) for i in docids.split(',')]
	# 	if data.get('options'):
	# 		data.update(json.loads(data.pop('options')))
	# 	if data.get('context'):
	# 		data['context'] = json.loads(data['context'])
	# 		if data['context'].get('lang'):
	# 			del data['context']['lang']
	# 		context.update(data['context'])
	# 	data = []
	# 	if reportname == 'label_zebra_printer.report_zebra_shipmentlabel':
	# 		for picking in request.env['stock.picking'].browse(docids):
	# 			data.append({
	# 				'label': picking.name,
	# 			})
	# 	if reportname == 'dokkan_ext.report_orderlabel':
	# 		for picking in request.env['sale.order'].browse(docids).mapped('picking_ids'):
	# 			data.append({
	# 				'label': picking.name,
	# 				'ordername': picking.origin,
	# 				'picker': picking.sale_id.picker_id.name,
	# 				'shipper': picking.sale_id.carrier_id.name,
	# 				'items': picking.sale_id.products_count,
	# 			})
	# 	elif reportname == 'stock.report_location_barcode':
	# 		for location in request.env['stock.location'].browse(docids):
	# 			data.append({
	# 				'name': location.name,
	# 				'barcode': location.barcode,
	# 			})
	# 	#elif reportname == 'product.report_product_template_label':
	# 	elif reportname == 'product.report_producttemplatelabel':
	# 		for product in request.env['product.template'].browse(docids):
	#
	# 			data.append({
	# 				'name': product.name,
	# 				'barcode': product.barcode or product.default_code or product.oc_sku,
	# 				'price': product.list_price,
	# 			})
	# 	#elif reportname == 'product.report_product_label':
	# 	elif reportname == 'product.report_productlabel':
	# 		for product in request.env['product.product'].browse(docids):
	# 			vars = ''
	# 			for var in product.attribute_value_ids:
	# 				vars += (var.attribute_id.name + ': ' + var.name)
	#
	# 			data.append({
	# 				'name': product.name,
	# 				'barcode': product.barcode or product.default_code or product.oc_sku,
	# 				'price': product.list_price,
	# 				'variants': vars,
	# 			})
	#
	# 	return {'data': data}
