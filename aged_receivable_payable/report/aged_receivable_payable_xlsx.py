# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta
import pandas as pd
from datetime import datetime
import datetime
from urllib.request import urlopen
import io
import os
from odoo import api, models, fields

dirname = os.path.dirname(__file__)


class AgedReceivablePayableXlsx(models.AbstractModel):
	_name = 'report.aged_receivable_payable.aged_rece_pay_xls_temp_id'
	_description = 'Aged Receivable Payable XlsxReports'
	_inherit = 'report.report_xlsx.abstract'

	@api.model
	def generate_xlsx_report(self, workbook, data, wizard_data):
		company_id = self.env['res.company'].search([], limit=1)

		partner_ids = wizard_data.partner_ids
		report_type = wizard_data.report_type
		date = wizard_data.date
		with_detail = wizard_data.with_detail
		include_draft = wizard_data.include_draft

		user = self.env.user
		company = self.env.company

		rece_type = 0
		pay_type = 0
		if report_type == 'Both':
			rece_type = 1
			pay_type = 1
		if report_type == 'Receivable':
			rece_type = 1
			pay_type = 0
		if report_type == 'Payable':
			rece_type = 0
			pay_type = 1

		head = 'Aged Receivable Payable Report'
		as_of = "Current"
		one = "1 - 30"
		two = "31 - 60"
		three = "61 - 90"
		four = "91 - 120"
		five = "121 - 150"
		six = "151 - 180"
		seven = "181 - 210"
		eight = "211 - 240"
		nine = "241 - 270"
		ten = "271 - 300"
		eleven = "301 - 330"
		twelve = "331 - 360"
		older = "> 360"

		head = 'Aged Receivable Payable Report'
		as_of_pay = "Current"
		one_pay = "1 - 30"
		two_pay = "31 - 60"
		three_pay = "61 - 90"
		four_pay = "91 - 120"
		five_pay = "121 - 150"
		six_pay = "151 - 180"
		seven_pay = "181 - 210"
		eight_pay = "211 - 240"
		nine_pay = "241 - 270"
		ten_pay = "271 - 300"
		eleven_pay = "301 - 330"
		twelve_pay = "331 - 360"
		older_pay = "> 360"

		newdate1 = date - relativedelta(days=30)
		newdate2 = date - relativedelta(days=60)
		newdate3 = date - relativedelta(days=90)
		newdate4 = date - relativedelta(days=120)
		newdate5 = date - relativedelta(days=150)
		newdate6 = date - relativedelta(days=180)
		newdate7 = date - relativedelta(days=210)
		newdate8 = date - relativedelta(days=240)
		newdate9 = date - relativedelta(days=270)
		newdate10 = date - relativedelta(days=300)
		newdate11 = date - relativedelta(days=330)
		newdate12 = date - relativedelta(days=360)

		moveline_obj = self.env['account.move.line']
		domain = [('date','<=',date)]
		if partner_ids:
			domain.append(('partner_id', 'in', partner_ids.ids))
			
		if report_type:
			if report_type == 'Receivable':
				domain.append(('account_id.user_type_id.type', '=', 'receivable'))
			elif report_type == 'Payable':
				domain.append(('account_id.user_type_id.type', '=', 'payable'))
			else:
				domain.append(('account_id.user_type_id.type', 'in', ('receivable','payable')))
				
		if not include_draft:
			domain.append(('move_id.state', '<>', 'draft'))
		
		movelines = moveline_obj.search(domain)

		recivable_line = movelines.filtered(lambda p: p.account_id.user_type_id.type == 'receivable')
		payable_line = movelines.filtered(lambda p: p.account_id.user_type_id.type == 'payable')

		lst = []
		for line in recivable_line:
			if line.date and date:

				debit = line.debit - line.credit
				m_d_amt=0
				m_c_amt=0
				for m in line.matched_debit_ids:
					c_date =m.max_date
					if c_date <= date:
						m_d_amt += m.amount

				for m in line.matched_credit_ids:
					c_date =m.max_date
					if c_date <= date:
						m_c_amt += m.amount
						
				p_amt= m_d_amt - m_c_amt  
				debit = debit + p_amt

				lst.append({
					'partner_id':line.partner_id and line.partner_id.id or False,
					'number':line.move_id and line.move_id.name or False,
					'date_due':(line.date),
					'residual':debit,
					'jrnl_code':line.move_id.journal_id.code,
				})

		invoice_data = pd.DataFrame(lst)
		unique_partners = []

		if len(invoice_data) > 0:
			invoice_data = invoice_data.loc[(invoice_data['residual'] != 0)]
			# invoice_data = invoice_data.sort_values('date_due',ascending=False)
			# invoice_data = invoice_data.sort('date_due', ascending=False)
			unique_partners = invoice_data.partner_id.unique()

		main_data = []
		as_of_tot = 0
		one_tot = 0
		two_tot = 0
		three_tot = 0
		four_tot = 0
		five_tot = 0
		six_tot = 0
		seven_tot = 0
		eight_tot = 0
		nine_tot = 0
		ten_tot = 0
		eleven_tot = 0
		twelve_tot = 0
		older_tot = 0
		tot_amt_tot = 0
		for x in unique_partners:

			partner_data = self.env['res.partner'].search([('id', '=', int(x))], limit=1)
			ven_code = ""
			cust_code = ""
			partner_name = str(partner_data.name)
			act_name = str(partner_data.property_account_receivable_id.code) + str(
				partner_data.property_account_receivable_id.name)

			tot_inv = invoice_data.loc[(invoice_data['partner_id'] == x)]
			tot_inv = tot_inv.groupby(['partner_id'], as_index=False).sum()
			tot_amt = 0
			if len(tot_inv) > 0:
				for index, line in tot_inv.iterrows():
					tot_amt = line['residual']

			as_of_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] >= date)]

			as_of_inv_list = as_of_inv.T.to_dict().values()
			as_of_inv = as_of_inv.groupby(['partner_id'], as_index=False).sum()
			as_of_amt = 0
			if len(as_of_inv) > 0:
				for index, line in as_of_inv.iterrows():
					as_of_amt = line['residual']

			one_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < date) & (
					invoice_data['date_due'] >= newdate1)]
			one_inv_list = one_inv.T.to_dict().values()
			one_inv = one_inv.groupby(['partner_id'], as_index=False).sum()
			one_amt = 0
			if len(one_inv) > 0:
				for index, line in one_inv.iterrows():
					one_amt = line['residual']

			two_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate1) & (
					invoice_data['date_due'] >= newdate2)]
			two_inv_list = two_inv.T.to_dict().values()
			two_inv = two_inv.groupby(['partner_id'], as_index=False).sum()
			two_amt = 0
			if len(two_inv) > 0:
				for index, line in two_inv.iterrows():
					two_amt = line['residual']

			three_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate2) & (
					invoice_data['date_due'] >= newdate3)]
			three_inv_list = three_inv.T.to_dict().values()
			three_inv = three_inv.groupby(['partner_id'], as_index=False).sum()
			three_amt = 0
			if len(three_inv) > 0:
				for index, line in three_inv.iterrows():
					three_amt = line['residual']

			four_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate3) & (
					invoice_data['date_due'] >= newdate4)]
			four_inv_list = four_inv.T.to_dict().values()
			four_inv = four_inv.groupby(['partner_id'], as_index=False).sum()
			four_amt = 0
			if len(four_inv) > 0:
				for index, line in four_inv.iterrows():
					four_amt = line['residual']

			five_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate4) & (
					invoice_data['date_due'] >= newdate5)]
			five_inv_list = five_inv.T.to_dict().values()
			five_inv = five_inv.groupby(['partner_id'], as_index=False).sum()
			five_amt = 0
			if len(five_inv) > 0:
				for index, line in five_inv.iterrows():
					five_amt = line['residual']

			six_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate5) & (
					invoice_data['date_due'] >= newdate6)]
			six_inv_list = six_inv.T.to_dict().values()
			six_inv = six_inv.groupby(['partner_id'], as_index=False).sum()
			six_amt = 0
			if len(six_inv) > 0:
				for index, line in six_inv.iterrows():
					six_amt = line['residual']

			seven_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate6) & (
					invoice_data['date_due'] >= newdate7)]
			seven_inv_list = seven_inv.T.to_dict().values()
			seven_inv = seven_inv.groupby(['partner_id'], as_index=False).sum()
			seven_amt = 0
			if len(seven_inv) > 0:
				for index, line in seven_inv.iterrows():
					seven_amt = line['residual']

			eight_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate7) & (
					invoice_data['date_due'] >= newdate8)]
			eight_inv_list = eight_inv.T.to_dict().values()
			eight_inv = eight_inv.groupby(['partner_id'], as_index=False).sum()
			eight_amt = 0
			if len(eight_inv) > 0:
				for index, line in eight_inv.iterrows():
					eight_amt = line['residual']

			nine_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate8) & (
					invoice_data['date_due'] >= newdate9)]
			nine_inv_list = nine_inv.T.to_dict().values()
			nine_inv = nine_inv.groupby(['partner_id'], as_index=False).sum()
			nine_amt = 0
			if len(nine_inv) > 0:
				for index, line in nine_inv.iterrows():
					nine_amt = line['residual']

			ten_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate9) & (
					invoice_data['date_due'] >= newdate10)]
			ten_inv_list = ten_inv.T.to_dict().values()
			ten_inv = ten_inv.groupby(['partner_id'], as_index=False).sum()
			ten_amt = 0
			if len(ten_inv) > 0:
				for index, line in ten_inv.iterrows():
					ten_amt = line['residual']

			eleven_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate10) & (
					invoice_data['date_due'] >= newdate11)]
			eleven_inv_list = eleven_inv.T.to_dict().values()
			eleven_inv = eleven_inv.groupby(['partner_id'], as_index=False).sum()
			eleven_amt = 0
			if len(eleven_inv) > 0:
				for index, line in eleven_inv.iterrows():
					eleven_amt = line['residual']

			twelve_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate11) & (
					invoice_data['date_due'] >= newdate12)]
			twelve_inv_list = twelve_inv.T.to_dict().values()
			twelve_inv = twelve_inv.groupby(['partner_id'], as_index=False).sum()
			twelve_amt = 0
			if len(twelve_inv) > 0:
				for index, line in twelve_inv.iterrows():
					twelve_amt = line['residual']

			older_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate12)]
			older_inv_list = older_inv.T.to_dict().values()
			older_inv = older_inv.groupby(['partner_id'], as_index=False).sum()
			older_amt = 0
			if len(older_inv) > 0:
				for index, line in older_inv.iterrows():
					older_amt = line['residual']

			as_of_tot = as_of_tot + as_of_amt
			one_tot = one_tot + one_amt
			two_tot = two_tot + two_amt
			three_tot = three_tot + three_amt
			four_tot = four_tot + four_amt
			five_tot = five_tot + five_amt
			six_tot = six_tot + six_amt
			seven_tot = seven_tot + seven_amt
			eight_tot = eight_tot + eight_amt
			nine_tot = nine_tot + nine_amt
			ten_tot = ten_tot + ten_amt
			eleven_tot = eleven_tot + eleven_amt
			twelve_tot = twelve_tot + twelve_amt
			older_tot = older_tot + older_amt
			tot_amt_tot = tot_amt_tot + tot_amt

			main_data.append({
				'name': partner_name,
				'act_name': act_name,
				'cust_code': cust_code,
				'ven_code': ven_code,
				'as_of_amt': as_of_amt,
				'one_amt': one_amt,
				'two_amt': two_amt,
				'three_amt': three_amt,
				'four_amt': four_amt,
				'five_amt': five_amt,
				'six_amt': six_amt,
				'seven_amt': seven_amt,
				'eight_amt': eight_amt,
				'nine_amt': nine_amt,
				'ten_amt': ten_amt,
				'eleven_amt': eleven_amt,
				'twelve_amt': twelve_amt,
				'older_amt': older_amt,
				'tot_amt': tot_amt,
				'as_of_inv_list': as_of_inv_list,
				'one_inv_list': one_inv_list,
				'two_inv_list': two_inv_list,
				'three_inv_list': three_inv_list,
				'four_inv_list': four_inv_list,
				'five_inv_list': five_inv_list,
				'six_inv_list': six_inv_list,
				'seven_inv_list': seven_inv_list,
				'eight_inv_list': eight_inv_list,
				'nine_inv_list': nine_inv_list,
				'ten_inv_list': ten_inv_list,
				'eleven_inv_list': eleven_inv_list,
				'twelve_inv_list': twelve_inv_list,
				'older_inv_list': older_inv_list,
			})

			if len(main_data) > 0:
				main_data = sorted(main_data, key=lambda v: v['name'])

		lst = []
		for line in payable_line:
			if line.date and date:

				debit = line.debit - line.credit
				m_d_amt=0
				m_c_amt=0
				for m in line.matched_debit_ids:
					c_date =m.max_date
					if c_date <= date:
						m_d_amt += m.amount
						
						
				for m in line.matched_credit_ids:
					c_date =m.max_date
					if c_date <= date:
						m_c_amt += m.amount
						
				p_amt= m_d_amt - m_c_amt  
				debit = debit + p_amt

				lst.append({
					'partner_id':line.partner_id and line.partner_id.id or False,
					'number':line.move_id and line.move_id.name or False,
					'date_due':(line.date),
					'residual':debit,
					'jrnl_code':line.move_id.journal_id.code,
				})

		if lst:
			lst = sorted(lst, key=lambda v: v['date_due'])
		invoice_data = pd.DataFrame(lst)
		unique_vendors = []

		if len(invoice_data) > 0:
			invoice_data = invoice_data.loc[(invoice_data['residual'] != 0)]
			# invoice_data = invoice_data.sort_values('date_due',ascending=False)
			# invoice_data = invoice_data.sort('date_due', ascending=False)
			unique_vendors = invoice_data.partner_id.unique()

		main_data_pay = []
		as_of_tot_pay = 0
		one_tot_pay = 0
		two_tot_pay = 0
		three_tot_pay = 0
		four_tot_pay = 0
		five_tot_pay = 0
		six_tot_pay = 0
		seven_tot_pay = 0
		eight_tot_pay = 0
		nine_tot_pay = 0
		ten_tot_pay = 0
		eleven_tot_pay = 0
		twelve_tot_pay = 0
		older_tot_pay = 0
		tot_amt_tot_pay = 0
		for x in unique_vendors:

			partner_data = self.env['res.partner'].search([('id', '=', int(x))], limit=1)
			ven_code = ""
			cust_code = ""
			partner_name = str(partner_data.name)
			act_name = str(partner_data.property_account_payable_id.code) + str(
				partner_data.property_account_payable_id.name)

			tot_inv = invoice_data.loc[(invoice_data['partner_id'] == x)]
			tot_inv = tot_inv.groupby(['partner_id'], as_index=False).sum()
			tot_amt = 0
			if len(tot_inv) > 0:
				for index, line in tot_inv.iterrows():
					tot_amt = line['residual']

			# as_of_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] == date)]
			# credit_as_of_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['pay_term_type'] == 'Credit') & (invoice_data['date_due'] >= date)]
			# cash_of_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['pay_term_type'] == 'Cash') & (invoice_data['date_due'] == date)]
			# as_of_inv_frames = [credit_as_of_inv, cash_of_inv]
			# as_of_inv = pd.concat(as_of_inv_frames)
			as_of_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] >= date)]
			as_of_inv_list = as_of_inv.T.to_dict().values()
			as_of_inv = as_of_inv.groupby(['partner_id'], as_index=False).sum()
			as_of_amt = 0
			if len(as_of_inv) > 0:
				for index, line in as_of_inv.iterrows():
					as_of_amt = line['residual']

			one_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < date) & (
					invoice_data['date_due'] >= newdate1)]
			one_inv_list = one_inv.T.to_dict().values()
			one_inv = one_inv.groupby(['partner_id'], as_index=False).sum()
			one_amt = 0
			if len(one_inv) > 0:
				for index, line in one_inv.iterrows():
					one_amt = line['residual']

			two_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate1) & (
					invoice_data['date_due'] >= newdate2)]
			two_inv_list = two_inv.T.to_dict().values()
			two_inv = two_inv.groupby(['partner_id'], as_index=False).sum()
			two_amt = 0
			if len(two_inv) > 0:
				for index, line in two_inv.iterrows():
					two_amt = line['residual']

			three_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate2) & (
					invoice_data['date_due'] >= newdate3)]
			three_inv_list = three_inv.T.to_dict().values()
			three_inv = three_inv.groupby(['partner_id'], as_index=False).sum()
			three_amt = 0
			if len(three_inv) > 0:
				for index, line in three_inv.iterrows():
					three_amt = line['residual']

			four_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate3) & (
					invoice_data['date_due'] >= newdate4)]
			four_inv_list = four_inv.T.to_dict().values()
			four_inv = four_inv.groupby(['partner_id'], as_index=False).sum()
			four_amt = 0
			if len(four_inv) > 0:
				for index, line in four_inv.iterrows():
					four_amt = line['residual']

			five_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate4) & (
					invoice_data['date_due'] >= newdate5)]
			five_inv_list = five_inv.T.to_dict().values()
			five_inv = five_inv.groupby(['partner_id'], as_index=False).sum()
			five_amt = 0
			if len(five_inv) > 0:
				for index, line in five_inv.iterrows():
					five_amt = line['residual']

			six_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate5) & (
					invoice_data['date_due'] >= newdate6)]
			six_inv_list = six_inv.T.to_dict().values()
			six_inv = six_inv.groupby(['partner_id'], as_index=False).sum()
			six_amt = 0
			if len(six_inv) > 0:
				for index, line in six_inv.iterrows():
					six_amt = line['residual']

			seven_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate6) & (
					invoice_data['date_due'] >= newdate7)]
			seven_inv_list = seven_inv.T.to_dict().values()
			seven_inv = seven_inv.groupby(['partner_id'], as_index=False).sum()
			seven_amt = 0
			if len(seven_inv) > 0:
				for index, line in seven_inv.iterrows():
					seven_amt = line['residual']

			eight_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate7) & (
					invoice_data['date_due'] >= newdate8)]
			eight_inv_list = eight_inv.T.to_dict().values()
			eight_inv = eight_inv.groupby(['partner_id'], as_index=False).sum()
			eight_amt = 0
			if len(eight_inv) > 0:
				for index, line in eight_inv.iterrows():
					eight_amt = line['residual']

			nine_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate8) & (
					invoice_data['date_due'] >= newdate9)]
			nine_inv_list = nine_inv.T.to_dict().values()
			nine_inv = nine_inv.groupby(['partner_id'], as_index=False).sum()
			nine_amt = 0
			if len(nine_inv) > 0:
				for index, line in nine_inv.iterrows():
					nine_amt = line['residual']

			ten_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate9) & (
					invoice_data['date_due'] >= newdate10)]
			ten_inv_list = ten_inv.T.to_dict().values()
			ten_inv = ten_inv.groupby(['partner_id'], as_index=False).sum()
			ten_amt = 0
			if len(ten_inv) > 0:
				for index, line in ten_inv.iterrows():
					ten_amt = line['residual']

			eleven_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate10) & (
					invoice_data['date_due'] >= newdate11)]
			eleven_inv_list = eleven_inv.T.to_dict().values()
			eleven_inv = eleven_inv.groupby(['partner_id'], as_index=False).sum()
			eleven_amt = 0
			if len(eleven_inv) > 0:
				for index, line in eleven_inv.iterrows():
					eleven_amt = line['residual']

			twelve_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate11) & (
					invoice_data['date_due'] >= newdate12)]
			twelve_inv_list = twelve_inv.T.to_dict().values()
			twelve_inv = twelve_inv.groupby(['partner_id'], as_index=False).sum()
			twelve_amt = 0
			if len(twelve_inv) > 0:
				for index, line in twelve_inv.iterrows():
					twelve_amt = line['residual']

			older_inv = invoice_data.loc[(invoice_data['partner_id'] == x) & (invoice_data['date_due'] < newdate12)]
			older_inv_list = older_inv.T.to_dict().values()
			older_inv = older_inv.groupby(['partner_id'], as_index=False).sum()
			older_amt = 0
			if len(older_inv) > 0:
				for index, line in older_inv.iterrows():
					older_amt = line['residual']

			as_of_tot_pay = as_of_tot_pay + as_of_amt
			one_tot_pay = one_tot_pay + one_amt
			two_tot_pay = two_tot_pay + two_amt
			three_tot_pay = three_tot_pay + three_amt
			four_tot_pay = four_tot_pay + four_amt
			five_tot_pay = five_tot_pay + five_amt
			six_tot_pay = six_tot_pay + six_amt
			seven_tot_pay = seven_tot_pay + seven_amt
			eight_tot_pay = eight_tot_pay + eight_amt
			nine_tot_pay = nine_tot_pay + nine_amt
			ten_tot_pay = ten_tot_pay + ten_amt
			eleven_tot_pay = eleven_tot_pay + eleven_amt
			twelve_tot_pay = twelve_tot_pay + twelve_amt
			older_tot_pay = older_tot_pay + older_amt
			tot_amt_tot_pay = tot_amt_tot_pay + tot_amt

			main_data_pay.append({
				'name': partner_name,
				'act_name': act_name,
				'cust_code': cust_code,
				'ven_code': ven_code,
				'as_of_amt': as_of_amt,
				'one_amt': one_amt,
				'two_amt': two_amt,
				'three_amt': three_amt,
				'four_amt': four_amt,
				'five_amt': five_amt,
				'six_amt': six_amt,
				'seven_amt': seven_amt,
				'eight_amt': eight_amt,
				'nine_amt': nine_amt,
				'ten_amt': ten_amt,
				'eleven_amt': eleven_amt,
				'twelve_amt': twelve_amt,
				'older_amt': older_amt,
				'tot_amt': tot_amt,
				'as_of_inv_list': as_of_inv_list,
				'one_inv_list': one_inv_list,
				'two_inv_list': two_inv_list,
				'three_inv_list': three_inv_list,
				'four_inv_list': four_inv_list,
				'five_inv_list': five_inv_list,
				'six_inv_list': six_inv_list,
				'seven_inv_list': seven_inv_list,
				'eight_inv_list': eight_inv_list,
				'nine_inv_list': nine_inv_list,
				'ten_inv_list': ten_inv_list,
				'eleven_inv_list': eleven_inv_list,
				'twelve_inv_list': twelve_inv_list,
				'older_inv_list': older_inv_list,
			})

			if len(main_data_pay) > 0:
				main_data_pay = sorted(main_data_pay, key=lambda v: v['name'])

		x = datetime.date.today()
		date = date.strftime("%d/%m/%Y")
		current_date = x.strftime("%d/%m/%Y")

		def get_date_format(date):
			return date.strftime("%d/%m/%Y")

		# Create Designs
		header_title = workbook.add_format({
			'bold': 1,
			'size': 10,
			'align': 'center',
			'valign': 'vcenter'})

		header_title_left = workbook.add_format({
			'bold': 1,
			'size': 10,
			'align': 'left',
			'valign': 'vcenter'})

		header_format = workbook.add_format({
			'bold': 1,
			'border': 1,
			'size': 10,
			'align': 'center',
			'valign': 'vcenter',
			'fg_color': '#8EA9DB'})

		main_data_font = workbook.add_format({
			'bold': 1,
			'size': 8,
			'align': 'left',
			'valign': 'vcenter'})

		main_data_font_center = workbook.add_format({
			'bold': 1,
			'size': 8,
			'align': 'center',
			'valign': 'vcenter'})

		main_data_right = workbook.add_format({
			'bold': 1,
			'size': 8,
			'align': 'right',
			'valign': 'vcenter'})

		data = workbook.add_format({
			"align": 'left',
			"valign": 'vcenter',
			'font_size': '8',
		})
		values = workbook.add_format({
			"align": 'right',
			"valign": 'vcenter',
			'font_size': '8',
		})
		center = workbook.add_format({
			"align": 'center',
			"valign": 'vcenter',
			'font_size': '8',
		})
		# header_title.set_text_wrap()
		# Add Worksheet
		worksheet = workbook.add_worksheet("Partner Purchase Detail")
		worksheet.set_column('A:A', 40)
		worksheet.set_column('B:E', 8)
		worksheet.set_column('F:S', 7)
		worksheet.set_row(7, 20)

		# CompanyLogo
		worksheet.merge_range('A1:A6', " ")

		# Image get from company logo
		web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		url = web_base_url + '/logo.png?company=%d' % company.id
		image_data = io.BytesIO(urlopen(url).read())
		worksheet.insert_image('A1:B5', url,
							   {'image_data': image_data, 'x_scale': 1.2, 'y_scale': 0.8, "align": 'center'})

		# Title
		worksheet.merge_range('E1:I2', company.name, header_title)
		worksheet.merge_range('E3:I5', 'Aged Receivable and Payable Report', header_title)
		worksheet.write('G6', date, header_title)
		worksheet.merge_range('P1:Q1', "Report Date", center)
		worksheet.merge_range('R1:S1', current_date, center)

		row = 8
		if report_type == 'Receivable' or report_type == 'Both':

			# Table Title
			worksheet.write('A7', 'Aged Receivable', header_title_left)

			# Table Headings
			worksheet.write('A8', 'Partner', header_format)
			worksheet.write('B8', 'Invoice Date', header_format)
			worksheet.write('C8', 'Journal', header_format)
			worksheet.write('D8', 'Account', header_format)
			worksheet.write('E8', 'Current', header_format)
			worksheet.write('F8', '1-30', header_format)
			worksheet.write('G8', '31-60', header_format)
			worksheet.write('H8', '61-90', header_format)
			worksheet.write('I8', '91-120', header_format)
			worksheet.write('J8', '121-150', header_format)
			worksheet.write('K8', '151-180', header_format)
			worksheet.write('L8', '181-210', header_format)
			worksheet.write('M8', '211-240', header_format)
			worksheet.write('N8', '241-270', header_format)
			worksheet.write('O8', '271-300', header_format)
			worksheet.write('P8', '301-330', header_format)
			worksheet.write('Q8', '331-360', header_format)
			worksheet.write('R8', '>360', header_format)
			worksheet.write('S8', 'Total', header_format)

			# Declaring row
			# Loop for main partner details
			for rec in main_data:
				worksheet.write(row, 0, rec['name'], main_data_font)
				worksheet.write(row, 1, "", main_data_right)
				worksheet.write(row, 2, "", main_data_right)
				worksheet.write(row, 3, "", main_data_right)
				worksheet.write(row, 4, rec['as_of_amt'], main_data_right)
				worksheet.write(row, 5, rec['one_amt'], main_data_right)
				worksheet.write(row, 6, rec['two_amt'], main_data_right)
				worksheet.write(row, 7, rec['three_amt'], main_data_right)
				worksheet.write(row, 8, rec['four_amt'], main_data_right)
				worksheet.write(row, 9, rec['five_amt'], main_data_right)
				worksheet.write(row, 10, rec['six_amt'], main_data_right)
				worksheet.write(row, 11, rec['seven_amt'], main_data_right)
				worksheet.write(row, 12, rec['eight_amt'], main_data_right)
				worksheet.write(row, 13, rec['nine_amt'], main_data_right)
				worksheet.write(row, 14, rec['ten_amt'], main_data_right)
				worksheet.write(row, 15, rec['eleven_amt'], main_data_right)
				worksheet.write(row, 16, rec['twelve_amt'], main_data_right)
				worksheet.write(row, 17, rec['older_amt'], main_data_right)
				worksheet.write(row, 18, rec['tot_amt'], main_data_right)
				row += 1

				if with_detail == True:
					# Sub data of partners
					for as_of in rec['as_of_inv_list']:
						worksheet.write(row, 0, as_of['number'], data)
						worksheet.write(row, 1, as_of['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, as_of['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, as_of['residual'], values)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for one in rec['one_inv_list']:
						worksheet.write(row, 0, one['number'], data)
						worksheet.write(row, 1, one['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, one['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, one['residual'], values)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for two in rec['two_inv_list']:
						worksheet.write(row, 0, two['number'], data)
						worksheet.write(row, 1, two['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, two['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, two['residual'], values)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for three in rec['three_inv_list']:
						worksheet.write(row, 0, three['number'], data)
						worksheet.write(row, 1, three['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, three['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, three['residual'], values)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for four in rec['four_inv_list']:
						worksheet.write(row, 0, four['number'], data)
						worksheet.write(row, 1, four['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, four['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, four['residual'], values)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for five in rec['five_inv_list']:
						worksheet.write(row, 0, five['number'], data)
						worksheet.write(row, 1, five['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, five['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, five['residual'], values)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for six in rec['six_inv_list']:
						worksheet.write(row, 0, six['number'], data)
						worksheet.write(row, 1, six['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, six['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, six['residual'], values)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for seven in rec['seven_inv_list']:
						worksheet.write(row, 0, seven['number'], data)
						worksheet.write(row, 1, seven['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, seven['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, seven['residual'], values)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for eight in rec['eight_inv_list']:
						worksheet.write(row, 0, eight['number'], data)
						worksheet.write(row, 1, eight['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, eight['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, eight['residual'], values)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for nine in rec['nine_inv_list']:
						worksheet.write(row, 0, nine['number'], data)
						worksheet.write(row, 1, nine['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, nine['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, nine['residual'], values)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for ten in rec['ten_inv_list']:
						worksheet.write(row, 0, ten['number'], data)
						worksheet.write(row, 1, ten['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, ten['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, ten['residual'], values)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for eleven in rec['eleven_inv_list']:
						worksheet.write(row, 0, eleven['number'], data)
						worksheet.write(row, 1, eleven['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, eleven['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, eleven['residual'], values)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for twelve in rec['twelve_inv_list']:
						worksheet.write(row, 0, twelve['number'], data)
						worksheet.write(row, 1, twelve['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, twelve['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 15, twelve['residual'], values)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for older in rec['older_inv_list']:
						worksheet.write(row, 0, older['number'], data)
						worksheet.write(row, 1, older['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, older['jrnl_code'], data)
						worksheet.write(row, 3, rec['cust_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, older['residual'], values)
						worksheet.write(row, 18, '-', center)
						row += 1

			# Total
			worksheet.write(row, 0, 'Total', main_data_font_center)
			worksheet.write(row, 1, "", main_data_right)
			worksheet.write(row, 2, "", main_data_right)
			worksheet.write(row, 3, "", main_data_right)
			worksheet.write(row, 4, float(as_of_tot), main_data_right)
			worksheet.write(row, 5, float(one_tot), main_data_right)
			worksheet.write(row, 6, float(two_tot), main_data_right)
			worksheet.write(row, 7, float(three_tot), main_data_right)
			worksheet.write(row, 8, float(four_tot), main_data_right)
			worksheet.write(row, 9, float(five_tot), main_data_right)
			worksheet.write(row, 10, float(six_tot), main_data_right)
			worksheet.write(row, 11, float(seven_tot), main_data_right)
			worksheet.write(row, 12, float(eight_tot), main_data_right)
			worksheet.write(row, 13, float(nine_tot), main_data_right)
			worksheet.write(row, 14, float(ten_tot), main_data_right)
			worksheet.write(row, 15, float(eleven_tot), main_data_right)
			worksheet.write(row, 16, float(twelve_tot), main_data_right)
			worksheet.write(row, 17, float(older_tot), main_data_right)
			worksheet.write(row, 18, float(tot_amt_tot), main_data_right)
			row += 2


		if report_type == 'Payable' or report_type == 'Both':
			# Table Title
			worksheet.write(row, 0, 'Aged Payable', header_title_left)
			row += 1
			# Table Headings
			worksheet.write(row, 0, 'Partner', header_format)
			worksheet.write(row, 1, 'Invoice Date', header_format)
			worksheet.write(row, 2, 'Journal', header_format)
			worksheet.write(row, 3, 'Account', header_format)
			worksheet.write(row, 4, 'Current', header_format)
			worksheet.write(row, 5, '1-30', header_format)
			worksheet.write(row, 6, '31-60', header_format)
			worksheet.write(row, 7, '61-90', header_format)
			worksheet.write(row, 8, '91-120', header_format)
			worksheet.write(row, 9, '121-150', header_format)
			worksheet.write(row, 10, '151-180', header_format)
			worksheet.write(row, 11, '181-210', header_format)
			worksheet.write(row, 12, '211-240', header_format)
			worksheet.write(row, 13, '241-270', header_format)
			worksheet.write(row, 14, '271-300', header_format)
			worksheet.write(row, 15, '301-330', header_format)
			worksheet.write(row, 16, '331-360', header_format)
			worksheet.write(row, 17, '>360', header_format)
			worksheet.write(row, 18, 'Total', header_format)
			row += 1

			# Sub data of partners Aged Payable
			for rec in main_data_pay:
				worksheet.write(row, 0, rec['name'], data)
				worksheet.write(row, 1, '', center)
				worksheet.write(row, 2, '', center)
				worksheet.write(row, 3, '', center)
				worksheet.write(row, 4, rec['as_of_amt'], values)
				worksheet.write(row, 5, rec['one_amt'], values)
				worksheet.write(row, 6, rec['two_amt'], values)
				worksheet.write(row, 7, rec['three_amt'], values)
				worksheet.write(row, 8, rec['four_amt'], values)
				worksheet.write(row, 9, rec['five_amt'], values)
				worksheet.write(row, 10, rec['six_amt'], values)
				worksheet.write(row, 11, rec['seven_amt'], values)
				worksheet.write(row, 12, rec['eight_amt'], values)
				worksheet.write(row, 13, rec['nine_amt'], values)
				worksheet.write(row, 14, rec['ten_amt'], values)
				worksheet.write(row, 15, rec['eleven_amt'], values)
				worksheet.write(row, 16, rec['twelve_amt'], values)
				worksheet.write(row, 17, rec['older_amt'], values)
				worksheet.write(row, 18, rec['tot_amt'], values)
				row += 1


				if with_detail == True:
					# Sub data of partners
					for as_of in rec['as_of_inv_list']:
						worksheet.write(row, 0, as_of['number'], data)
						worksheet.write(row, 1, as_of['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, as_of['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, as_of['residual'], values)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for one in rec['one_inv_list']:
						worksheet.write(row, 0, one['number'], data)
						worksheet.write(row, 1, one['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, one['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, one['residual'], values)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for two in rec['two_inv_list']:
						worksheet.write(row, 0, two['number'], data)
						worksheet.write(row, 1, two['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, two['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, two['residual'], values)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for three in rec['three_inv_list']:
						worksheet.write(row, 0, three['number'], data)
						worksheet.write(row, 1, three['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, three['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, three['residual'], values)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for four in rec['four_inv_list']:
						worksheet.write(row, 0, four['number'], data)
						worksheet.write(row, 1, four['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, four['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, four['residual'], values)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for five in rec['five_inv_list']:
						worksheet.write(row, 0, five['number'], data)
						worksheet.write(row, 1, five['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, five['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, five['residual'], values)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for six in rec['six_inv_list']:
						worksheet.write(row, 0, six['number'], data)
						worksheet.write(row, 1, six['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, six['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, six['residual'], values)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for seven in rec['seven_inv_list']:
						worksheet.write(row, 0, seven['number'], data)
						worksheet.write(row, 1, seven['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, seven['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, seven['residual'], values)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for eight in rec['eight_inv_list']:
						worksheet.write(row, 0, eight['number'], data)
						worksheet.write(row, 1, eight['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, eight['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, eight['residual'], values)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for nine in rec['nine_inv_list']:
						worksheet.write(row, 0, nine['number'], data)
						worksheet.write(row, 1, nine['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, nine['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, nine['residual'], values)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for ten in rec['ten_inv_list']:
						worksheet.write(row, 0, ten['number'], data)
						worksheet.write(row, 1, ten['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, ten['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, ten['residual'], values)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for eleven in rec['eleven_inv_list']:
						worksheet.write(row, 0, eleven['number'], data)
						worksheet.write(row, 1, eleven['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, eleven['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, eleven['residual'], values)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for twelve in rec['twelve_inv_list']:
						worksheet.write(row, 0, twelve['number'], data)
						worksheet.write(row, 1, twelve['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, twelve['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 15, twelve['residual'], values)
						worksheet.write(row, 17, '-', center)
						worksheet.write(row, 18, '-', center)
						row += 1

					# Sub data of partners
					for older in rec['older_inv_list']:
						worksheet.write(row, 0, older['number'], data)
						worksheet.write(row, 1, older['date_due'].strftime("%d/%m/%Y"), data)
						worksheet.write(row, 2, older['jrnl_code'], data)
						worksheet.write(row, 3, rec['ven_code'], data)
						worksheet.write(row, 4, '-', center)
						worksheet.write(row, 5, '-', center)
						worksheet.write(row, 6, '-', center)
						worksheet.write(row, 7, '-', center)
						worksheet.write(row, 8, '-', center)
						worksheet.write(row, 9, '-', center)
						worksheet.write(row, 10, '-', center)
						worksheet.write(row, 11, '-', center)
						worksheet.write(row, 12, '-', center)
						worksheet.write(row, 13, '-', center)
						worksheet.write(row, 14, '-', center)
						worksheet.write(row, 15, '-', center)
						worksheet.write(row, 16, '-', center)
						worksheet.write(row, 17, older['residual'], values)
						worksheet.write(row, 18, '-', center)
						row += 1

			# Total Aged Payable
			worksheet.write(row, 0, 'Total', main_data_font_center)
			worksheet.write(row, 1, '', main_data_right)
			worksheet.write(row, 2, '', main_data_right)
			worksheet.write(row, 3, '', main_data_right)
			worksheet.write(row, 4, float(as_of_tot_pay), main_data_right)
			worksheet.write(row, 5, float(one_tot_pay), main_data_right)
			worksheet.write(row, 6, float(two_tot_pay), main_data_right)
			worksheet.write(row, 7, float(three_tot_pay), main_data_right)
			worksheet.write(row, 8, float(four_tot_pay), main_data_right)
			worksheet.write(row, 9, float(five_tot_pay), main_data_right)
			worksheet.write(row, 10, float(six_tot_pay), main_data_right)
			worksheet.write(row, 11, float(seven_tot_pay), main_data_right)
			worksheet.write(row, 12, float(eight_tot_pay), main_data_right)
			worksheet.write(row, 13, float(nine_tot_pay), main_data_right)
			worksheet.write(row, 14, float(ten_tot_pay), main_data_right)
			worksheet.write(row, 15, float(eleven_tot_pay), main_data_right)
			worksheet.write(row, 16, float(twelve_tot_pay), main_data_right)
			worksheet.write(row, 17, float(older_tot_pay), main_data_right)
			worksheet.write(row, 18, float(tot_amt_tot_pay), main_data_right)
			row += 2

		worksheet.write(row, 0, "Printed by: ", data)
		worksheet.write(row, 1, user.name, data)
