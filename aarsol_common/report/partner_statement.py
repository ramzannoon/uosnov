
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo import api, fields, models, _

import pdb
import time

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')

try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
	
	

class PartnerStatementReport(models.AbstractModel):
	_name = 'report.aarsol_common.partner_statement'
	
	def get_date_formate(self,sdate):
		ss = datetime.strptime(sdate,'%Y-%m-%d')
		return ss.strftime('%d %b %Y')

	def _lines(self, dta=None):
		date_from = dta['form']['date_from'] and dta['form']['date_from']
		date_to = dta['form']['date_to'] and dta['form']['date_to']
		partner_id = dta['form']['partner_id'] and dta['form']['partner_id'][0]
		data = {}
		
		credit_total = 0
		debit_total = 0
		bal = 0
		ob = 0
		credit_ob = 0
		debit_ob = 0
		bal_ob = 0
		
		target_move = dta['form']['target_move']
		if target_move == 'posted':
			data['move_state'] = ['posted']
		if target_move == 'all':
			data['move_state'] = ['draft', 'posted']
		data['ACCOUNT_TYPE'] = ['payable', 'receivable']
		
		

		self.env.cr.execute("""
			SELECT a.id
			FROM account_account a
			WHERE a.internal_type IN %s
			AND NOT a.deprecated""", (tuple(data['ACCOUNT_TYPE']),))
		data['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
		
		full_account = []
		#query_get_data = self.env['account.move.line'].with_context({})._query_get()
		# so.name as so_name
		# so.client_order_ref as client_ref
		
		params1 = [partner_id, tuple(data['move_state']), tuple(data['account_ids']), date_from]
		
		query1 = """
			SELECT (sum(aml.debit)) - (sum(aml.credit)) as ob
			FROM account_move_line aml
			LEFT JOIN account_journal j ON (aml.journal_id = j.id)
			LEFT JOIN account_account acc ON (aml.account_id = acc.id)
			LEFT JOIN res_currency c ON (aml.currency_id=c.id)
			LEFT JOIN account_move m ON (m.id=aml.move_id)
			LEFT JOIN account_invoice ai ON (ai.id = aml.invoice_id)
			WHERE aml.partner_id = %s
				AND m.state IN %s
				AND aml.account_id IN %s
				AND aml.date < %s """
				
		
		self.env.cr.execute(query1, tuple(params1))
		ob = self.env.cr.dictfetchall()[0]['ob'] or 0
				
		if ob < 0.001:
			credit_ob = ob
			credit_total += abs(credit_ob)
			bal_ob = ob
		else:
			debit_ob = ob
			debit_total += debit_ob
			bal_ob = ob	
		
		
		
		params = [partner_id, tuple(data['move_state']), tuple(data['account_ids']), date_from, date_to] 
		query = """
			SELECT aml.id, aml.date, j.code, acc.code as a_code, acc.name as a_name, aml.ref, m.name as move_name, m.name as so_name, ' ' as client_ref,
				aml.name, aml.debit, aml.credit, aml.amount_currency,aml.currency_id, c.symbol AS currency_code
			FROM account_move_line aml
			LEFT JOIN account_journal j ON (aml.journal_id = j.id)
			LEFT JOIN account_account acc ON (aml.account_id = acc.id)
			LEFT JOIN res_currency c ON (aml.currency_id=c.id)
			LEFT JOIN account_move m ON (m.id=aml.move_id)
			LEFT JOIN account_invoice ai ON (ai.id = aml.invoice_id)
			WHERE aml.partner_id = %s
				AND m.state IN %s
				AND aml.account_id IN %s
				AND aml.date >= %s
				AND aml.date <= %s
				ORDER BY aml.date, aml.id"""
				
		
		self.env.cr.execute(query, tuple(params))
		res = self.env.cr.dictfetchall()
		
		sum = bal_ob or 0.0
		for r in res:
			r['displayed_name'] = '-'.join(
				r[field_name] for field_name in ('move_name', 'ref')
				if r[field_name] not in (None, '', '/')
			)
			sum += r['debit'] - r['credit']
			credit_total = credit_total + r['credit']
			debit_total = debit_total + r['debit']
			r['progress'] = sum
			full_account.append(r)
			
		bal = sum	
		return full_account,credit_total,debit_total,bal,credit_ob,debit_ob,bal_ob

	@api.model
	def get_report_values(self, docsid, data=None):			
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		
		lines,credit_total,debit_total,bal,credit_ob,debit_ob,bal_ob = self._lines(data)
		
		report = self.env['ir.actions.report']._get_report_from_name('aarsol_common.partner_statement')
		partners = self.env['res.partner'].browse(data['form']['partner_id'][0])
		
		docargs = {
			'doc_ids': [], 
			'doc_model': report.model,
			'docs': partners,
			'lines' : lines or False,
			'Credit' : credit_total,
			'Debit' : debit_total,
			'Bal' : bal,
			'Credit_OB': credit_ob or 0,
			'Debit_OB' : debit_ob or 0,
			'Bal_OB' : bal_ob or 0,
			'get_date_formate' : self.get_date_formate,
			'data' : data['form'],			
		}					
		return docargs
			
	
	#***** Excel Report *****#
	def make_excel(self, data):
		if not data.get('form'):
			raise UserError(_("Form content is missing, this report cannot be printed."))

		
		#***** Excel Related Statements *****#
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Partner Ledger")
		
		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header2 = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_date_col = xlwt.easyxf("font:height 170; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_table_totals2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz right;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour periwinkle;")

		
		#col width
		fifth_col = worksheet.col(4)
		fifth_col.width = 256 * 40
		
		worksheet.write_merge(0, 1, 0, 7,"Partner Ledger Report", style = style_title)
		row = 2
		col = 0
		
		#***** Table Heading *****#
		table_header = ['Sr#','Date','JRNL','Account','Ref','Debit','Credit','Balance']
		for i in range(8):
			worksheet.write(row,col,table_header[i], style=style_table_header)
			col+=1	
		
		dta = self.get_report_values(None,data)
		
		#Opening Balance
		row += 1
		col = 0	
		worksheet.write_merge(row, row, 0, 4, 'Opening Balance', style=style_table_totals)
		worksheet.write(row,5,format(dta['Debit_OB'],'.2f' or 0.00), style=style_table_totals)
		worksheet.write(row,6,format(dta['Credit_OB'],'.2f' or 0.00), style=style_table_totals)
		worksheet.write(row,7,format(dta['Bal_OB'],'.2f' or 0.00), style=style_table_totals)
		
		#Data
		i = 1
		for line in  dta['lines']:
			
			if line['progress'] < 0:
				prog = format(abs(line['progress']),'.2f' or 0.00)
				progress = "("+ str(prog) + ")"
			else:
				progress = format(line['progress'],'.2f' or 0.00)
			
			row += 1
			col = 0
			
			worksheet.write(row,col,i, style=style_date_col)
			col +=1
			worksheet.write(row,col,line['date'] and line['date']  or '', style=style_date_col)
			col +=1
			worksheet.write(row,col,line['code'] and line['code']  or '', style=style_date_col)
			col +=1
			worksheet.write(row,col,line['a_code'] and line['a_code']  or '', style=style_date_col)
			col +=1
			worksheet.write(row,col,line['displayed_name'] and line['displayed_name']  or '', style=style_date_col)
			col +=1
			worksheet.write(row,col,format(line['debit'],'.2f' or 0.00), style=style_date_col)
			col +=1
			worksheet.write(row,col,format(line['credit'],'.2f' or 0.00), style=style_date_col)
			col +=1
			worksheet.write(row,col, progress,style=style_date_col)
			col +=1
			i +=1
		
		
		#Total
		if dta['Bal'] < 0:
			blan = format(abs(dta['Bal']),'.2f' or 0.00)
			bal = "("+ str(blan) + ")"
		else:
			bal = format(dta['Bal'],'.2f' or 0.00)
		
		row += 1
		col = 0	
		worksheet.write_merge(row, row, 0, 4, 'Total', style=style_table_totals)
		worksheet.write(row,5,format(dta['Debit'],'.2f' or 0.00), style=style_table_totals)
		worksheet.write(row,6,format(dta['Credit'],'.2f' or 0.00), style=style_table_totals)
		worksheet.write(row,7,bal, style=style_table_totals)
		row += 1
		col = 0
		
		#Due Balance Line
		worksheet.write_merge(row, row, 0, 6, 'Balance Due', style=style_table_totals)
		worksheet.write(row,7,bal, style=style_table_totals)		
		
		row += 1
		col = 0
		
		file_data = io.BytesIO()		
		workbook.save(file_data)		
		return file_data.getvalue()	






