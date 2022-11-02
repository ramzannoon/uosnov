# #-*- coding:utf-8 -*-


from datetime import date, timedelta, datetime
from odoo import api, models, fields, _
from dateutil.relativedelta import *
import calendar


class AgedReceivablePayablePDF(models.AbstractModel):
    _name = 'report.aged_receivable_payable.template_balance_sheet_pdf'
    _description = 'Aged Receivable Payable Reports PDF'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        active_record = self.env[self.model].browse(self.env.context.get('active_id'))
        
        partner_ids = self.env['res.partner'].search([])
        
        domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]

        # =========================== Non Current assets ================================
        nc_asset_list = self.env['account.account'].search([('user_type_id.name','=','Non-current Assets'),('move_line_ids','!=',False)])

        def get_non_current_asset(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            return sum(journal_item_ids.mapped('balance'))

        # =========================== Current assets ================================
        asset_list = self.env['account.account'].search([('user_type_id.name','=','Current Assets'),('move_line_ids','!=',False)])

        def get_current_asset(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            return sum(journal_item_ids.mapped('balance'))
        
        # # =========================== PARTNERS’ EQUITY ================================
        equity_list = self.env['account.account'].search([('user_type_id.name','=','Equity'),('move_line_ids','!=',False)])

        def get_equity(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            return sum(journal_item_ids.mapped('balance'))
        
        # # =========================== NON-CURRENT LIABILITIES ================================
        non_liabity_list = self.env['account.account'].search([('user_type_id.name','=','Non-current Liabilities'),('move_line_ids','!=',False)])

        def get_nc_liabity(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            return sum(journal_item_ids.mapped('balance'))
        
        # # =========================== CURRENT LIABILITIES ================================
        liabity_list = self.env['account.account'].search([('user_type_id.name','=','Current Liabilities'),('move_line_ids','!=',False)])
        
        def get_liabity(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            return sum(journal_item_ids.mapped('balance'))

        return {
            'doc_ids': docids,
            'active_record':active_record,
            'nc_asset_list':nc_asset_list,
            'asset_list':asset_list,
            'equity_list':equity_list,
            'non_liabity_list':non_liabity_list,
            'liabity_list':liabity_list,
            'get_non_current_asset':get_non_current_asset,
            'get_current_asset':get_current_asset,
            'get_equity':get_equity,
            'get_nc_liabity':get_nc_liabity,
            'get_liabity':get_liabity,
            }


# last month record in report
class ReportBalanceSheetPDF(models.AbstractModel):
    _name = 'report.aged_receivable_payable.template_aged_balance_sheet_pdf'
    _description = 'Aged Receivable Payable Reports PDF'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        active_record = self.env[self.model].browse(self.env.context.get('active_id'))
        partner_ids = self.env['res.partner'].search([])

        # previous record find
        prev_month_date = active_record.comparison_date
        prev_domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                prev_domain += [('move_id.date','<=',prev_month_date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                prev_domain += [('move_id.date','<=',prev_month_date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                prev_domain += [('move_id.date','<=',prev_month_date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                prev_domain += [('move_id.date','<=',prev_month_date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]

        # current record find
        domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]
                
        # =========================== Non Current assets ================================
        nc_asset_list = self.env['account.account'].search([('user_type_id.name','=','Non-current Assets'),('move_line_ids','!=',False)])

        def get_non_current_asset(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            pre_journal_item_ids = self.env['account.move.line'].search(prev_domain + [('account_id','=',int(account))])
            current_amount = sum(journal_item_ids.mapped('balance'))
            previous_amount = sum(pre_journal_item_ids.mapped('balance'))
            variance = current_amount - previous_amount
            
            return [current_amount,previous_amount,variance]

        # =========================== Current assets ================================
        asset_list = self.env['account.account'].search([('user_type_id.name','=','Current Assets'),('move_line_ids','!=',False)])

        def get_current_asset(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            pre_journal_item_ids = self.env['account.move.line'].search(prev_domain + [('account_id','=',int(account))])
            current_amount = sum(journal_item_ids.mapped('balance'))
            previous_amount = sum(pre_journal_item_ids.mapped('balance'))
            variance = current_amount - previous_amount
            
            return [current_amount,previous_amount,variance]

        # =========================== PARTNERS’ EQUITY ================================
        equity_list = self.env['account.account'].search([('user_type_id.name','=','Equity'),('move_line_ids','!=',False)])

        def get_equity(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            pre_journal_item_ids = self.env['account.move.line'].search(prev_domain + [('account_id','=',int(account))])
            current_amount = sum(journal_item_ids.mapped('balance'))
            previous_amount = sum(pre_journal_item_ids.mapped('balance'))
            variance = current_amount - previous_amount
            
            return [current_amount,previous_amount,variance]

        # =========================== NON-CURRENT LIABILITIES ================================
        non_liabity_list = self.env['account.account'].search([('user_type_id.name','=','Non-current Liabilities'),('move_line_ids','!=',False)])

        def get_nc_liabity(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            pre_journal_item_ids = self.env['account.move.line'].search(prev_domain + [('account_id','=',int(account))])
            current_amount = sum(journal_item_ids.mapped('balance'))
            previous_amount = sum(pre_journal_item_ids.mapped('balance'))
            variance = current_amount - previous_amount
            
            return [current_amount,previous_amount,variance]

        # =========================== CURRENT LIABILITIES ================================
        liabity_list = self.env['account.account'].search([('user_type_id.name','=','Current Liabilities'),('move_line_ids','!=',False)])
        
        def get_liabity(account):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            pre_journal_item_ids = self.env['account.move.line'].search(prev_domain + [('account_id','=',int(account))])
            current_amount = sum(journal_item_ids.mapped('balance'))
            previous_amount = sum(pre_journal_item_ids.mapped('balance'))
            variance = current_amount - previous_amount
            
            return [current_amount,previous_amount,variance]

        return {
            'doc_ids': docids,
            'active_record':active_record,
            'nc_asset_list':nc_asset_list,
            'asset_list':asset_list,
            'equity_list':equity_list,
            'non_liabity_list':non_liabity_list,
            'liabity_list':liabity_list,
            'get_non_current_asset':get_non_current_asset,
            'get_current_asset':get_current_asset,
            'get_equity':get_equity,
            'get_nc_liabity':get_nc_liabity,
            'get_liabity':get_liabity,
            }


# Month wise record get on PDF report
class MonthwiseBalanceSheet(models.AbstractModel):
    _name = 'report.aged_receivable_payable.template_month_wise_sheet_pdf'
    _description = 'report.aged_receivable_payable.template_month_wise_sheet_pdf'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        active_record = self.env[self.model].browse(self.env.context.get('active_id'))
        
        # get month and year
        def get_month_year():
            month_year = []
            start_date = active_record.from_date
            end_date = active_record.to_date

            cur_date = start = datetime.strptime(str(start_date), '%Y-%m-%d').date()
            end = datetime.strptime(str(end_date), '%Y-%m-%d').date()

            while cur_date < end:
                list = [str(cur_date.month),calendar.month_abbr[cur_date.month],str(cur_date.year)]
                month_year.append(list)
                cur_date += relativedelta(months=1) 
            return month_year

        partner_ids = self.env['res.partner'].search([])
        
        domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                domain += [('move_id.date','>=',active_record.from_date),('move_id.date','<=',active_record.to_date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','>=',active_record.from_date),('move_id.date','<=',active_record.to_date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                domain += [('move_id.date','>=',active_record.from_date),('move_id.date','<=',active_record.to_date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','>=',active_record.from_date),('move_id.date','<=',active_record.to_date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]

        # =========================== Non Current assets ================================
        nc_asset_list = self.env['account.account'].search([('user_type_id.name','=','Non-current Assets'),('move_line_ids','!=',False)])

        # check account record
        def check_nc_asset_record(nc_asset):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(nc_asset))])
            return journal_item_ids

        # return record on report
        def get_non_current_asset(month,account,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            total_balance = 0.0
            for line in journal_item_ids:
                total_balance += line.balance if line.date.year == int(year) and line.date.month == int(month) else 0.0
            return {'balance': total_balance}

        # =========================== Current assets ================================
        asset_list = self.env['account.account'].search([('user_type_id.name','=','Current Assets'),('move_line_ids','!=',False)])

        # check account record
        def check_asset_record(asset):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(asset))])
            return journal_item_ids

        # return record on report
        def get_current_asset(month,account,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            total_balance = 0.0
            for line in journal_item_ids:
                total_balance += line.balance if line.date.year == int(year) and line.date.month == int(month) else 0.0
            return {'balance': total_balance}
        
        # # =========================== PARTNERS’ EQUITY ================================
        equity_list = self.env['account.account'].search([('user_type_id.name','=','Equity'),('move_line_ids','!=',False)])

        # check account record
        def check_equity_record(equity):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(equity))])
            return journal_item_ids

        # return record on report
        def get_equity(month,account,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            total_balance = 0.0
            for line in journal_item_ids:
                total_balance += line.balance if line.date.year == int(year) and line.date.month == int(month) else 0.0
            return {'balance': total_balance}
        
        # # =========================== NON-CURRENT LIABILITIES ================================
        non_liabity_list = self.env['account.account'].search([('user_type_id.name','=','Non-current Liabilities'),('move_line_ids','!=',False)])

        # check account record
        def check_nc_liabity_record(non_liabity):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(non_liabity))])
            return journal_item_ids

        # return record on report
        def get_nc_liabity(month,account,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            total_balance = 0.0
            for line in journal_item_ids:
                total_balance += line.balance if line.date.year == int(year) and line.date.month == int(month) else 0.0
            return {'balance': total_balance}
        
        # # =========================== CURRENT LIABILITIES ================================
        liabity_list = self.env['account.account'].search([('user_type_id.name','=','Current Liabilities'),('move_line_ids','!=',False)])
        
        # check account record
        def check_liabity_record(liabity):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(liabity))])
            return journal_item_ids

        # return record on report
        def get_liabity(month,account,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','=',int(account))])
            total_balance = 0.0
            for line in journal_item_ids:
                total_balance += line.balance if line.date.year == int(year) and line.date.month == int(month) else 0.0
            return {'balance': total_balance}

        # # =========================== All line total ================================
        # get non current asset total
        def get_nc_asset_total(month,nc_asset_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',nc_asset_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_nc_asset_list = sum(final_journal_ids.mapped('balance'))
            return {'total_nc_asset_list': total_nc_asset_list}

        # get current asset total
        def get_c_asset_total(month,asset_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',asset_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_asset_list = sum(final_journal_ids.mapped('balance'))
            return {'total_asset_list': total_asset_list}

        # get asset total
        def get_asset_total(month,nc_asset_list,asset_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',nc_asset_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_nc_asset_list = sum(final_journal_ids.mapped('balance'))

            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',asset_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_asset_list = sum(final_journal_ids.mapped('balance'))

            total_asset = total_nc_asset_list + total_asset_list
            return {'total_asset':total_asset}

        # get equity total
        def get_equity_total(month,equity_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',equity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_equity_list = sum(final_journal_ids.mapped('balance'))
            return {'total_equity_list':total_equity_list}

        # get non current liabity total
        def get_nc_liabity_total(month,non_liabity_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',non_liabity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_non_liabity_list = sum(final_journal_ids.mapped('balance'))
            return {'total_non_liabity_list':total_non_liabity_list}

        # get current liabity total
        def get_c_liabity_total(month,liabity_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',liabity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_liabity_list = sum(final_journal_ids.mapped('balance'))
            return {'total_liabity_list':total_liabity_list}

        # get liabity total
        def get_liabity_total(month,non_liabity_list,liabity_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',non_liabity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_non_liabity_list = sum(final_journal_ids.mapped('balance'))

            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',liabity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_liabity_list = sum(final_journal_ids.mapped('balance'))

            total_liabity = total_non_liabity_list + total_liabity_list
            return {'total_liabity':total_liabity}

        # get equity and liabity total
        def get_total(month,equity_list,non_liabity_list,liabity_list,year):
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',equity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_equity_list = sum(final_journal_ids.mapped('balance'))

            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',non_liabity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_non_liabity_list = sum(final_journal_ids.mapped('balance'))

            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',liabity_list.ids)])
            final_journal_ids = journal_item_ids.filtered(lambda x: x.date.month == int(month) and x.date.year == int(year))
            total_liabity_list = sum(final_journal_ids.mapped('balance'))

            total_liabity = total_non_liabity_list + total_liabity_list
            total_equity_liabity = total_equity_list + total_liabity
            return {'total_equity_liabity':total_equity_liabity}

        return {
            'doc_ids': docids,
            'active_record':active_record,
            'get_month_year':get_month_year,
            'nc_asset_list':nc_asset_list,
            'asset_list':asset_list,
            'equity_list':equity_list,
            'non_liabity_list':non_liabity_list,
            'liabity_list':liabity_list,
            'get_non_current_asset':get_non_current_asset,
            'get_current_asset':get_current_asset,
            'get_equity':get_equity,
            'get_nc_liabity':get_nc_liabity,
            'get_liabity':get_liabity,
            'get_nc_asset_total':get_nc_asset_total,
            'get_c_asset_total':get_c_asset_total,
            'get_asset_total':get_asset_total,
            'get_equity_total':get_equity_total,
            'get_nc_liabity_total':get_nc_liabity_total,
            'get_c_liabity_total':get_c_liabity_total,
            'get_liabity_total':get_liabity_total,
            'get_total':get_total,
            'check_nc_asset_record':check_nc_asset_record,
            'check_asset_record':check_asset_record,
            'check_equity_record':check_equity_record,
            'check_nc_liabity_record':check_nc_liabity_record,
            'check_liabity_record':check_liabity_record,
            }


# report for customer income statement
class CustomerIncomeStatement(models.AbstractModel):
    _name = 'report.aged_receivable_payable.template_income_statement'
    _description = 'report.aged_receivable_payable.template_income_statement'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        active_record = self.env[self.model].browse(self.env.context.get('active_id'))
        
        partner_ids = self.env['res.partner'].search([])
        
        domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]

        # =========================== Revenue ================================
        def get_revenue():
            account_ids = self.env['account.account'].search([('user_type_id.name','=','Income'),('move_line_ids','!=',False)])
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',account_ids.ids)])
            return sum(journal_item_ids.mapped('balance'))

        # =========================== Cost of Revenue ================================
        def get_cost_revenue():
            account_ids = self.env['account.account'].search([('user_type_id.name','=','Cost of Revenue'),('move_line_ids','!=',False)])
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',account_ids.ids)])
            return sum(journal_item_ids.mapped('balance'))

        # =========================== Other income ================================
        def get_other_income():
            account_ids = self.env['account.account'].search([('user_type_id.name','=','Other Income'),('move_line_ids','!=',False)])
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',account_ids.ids)])
            return sum(journal_item_ids.mapped('balance'))

        return {
            'doc_ids': docids,
            'active_record':active_record,
            'get_revenue':get_revenue,
            'get_cost_revenue':get_cost_revenue,
            'get_other_income':get_other_income,
            }


# report for customer income statement with last month
class CustomerIncomeStatement(models.AbstractModel):
    _name = 'report.aged_receivable_payable.template_income_statement_month'
    _description = 'report.aged_receivable_payable.template_income_statement_month'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        active_record = self.env[self.model].browse(self.env.context.get('active_id'))
        
        partner_ids = self.env['res.partner'].search([])
        
        domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                domain += [('move_id.date','<=',active_record.date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]

        pre_domain = []
        if active_record.partner_ids:    
            if active_record.include_draft == True:
                pre_domain += [('move_id.date','<=',active_record.comparison_date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                pre_domain += [('move_id.date','<=',active_record.comparison_date),('partner_id','in',active_record.partner_ids.ids),('move_id.state','=','posted')]
        else:
            if active_record.include_draft == True:
                pre_domain += [('move_id.date','<=',active_record.comparison_date),('partner_id','in',partner_ids.ids),('move_id.state','in',['draft','posted'])]
            else:
                pre_domain += [('move_id.date','<=',active_record.comparison_date),('partner_id','in',partner_ids.ids),('move_id.state','=','posted')]

        # =========================== Revenue ================================
        def get_revenue():
            account_ids = self.env['account.account'].search([('user_type_id.name','=','Income'),('move_line_ids','!=',False)])
            pre_journal_item_ids = self.env['account.move.line'].search(pre_domain + [('account_id','in',account_ids.ids)])
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',account_ids.ids)])
            
            previous_total = sum(pre_journal_item_ids.mapped('balance'))
            current_total = sum(journal_item_ids.mapped('balance'))
            variance = current_total - previous_total
            return {'previous_total':previous_total,'current_total':current_total,'variance':variance}

        # =========================== Cost of Revenue ================================
        def get_cost_revenue():
            account_ids = self.env['account.account'].search([('user_type_id.name','=','Cost of Revenue'),('move_line_ids','!=',False)])
            pre_journal_item_ids = self.env['account.move.line'].search(pre_domain + [('account_id','in',account_ids.ids)])
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',account_ids.ids)])
            
            previous_total = sum(pre_journal_item_ids.mapped('balance'))
            current_total = sum(journal_item_ids.mapped('balance'))
            variance = current_total - previous_total
            return {'previous_total':previous_total,'current_total':current_total,'variance':variance}

        # =========================== Other income ================================
        def get_other_income():
            account_ids = self.env['account.account'].search([('user_type_id.name','=','Other Income'),('move_line_ids','!=',False)])
            pre_journal_item_ids = self.env['account.move.line'].search(pre_domain + [('account_id','in',account_ids.ids)])
            journal_item_ids = self.env['account.move.line'].search(domain + [('account_id','in',account_ids.ids)])
            
            previous_total = sum(pre_journal_item_ids.mapped('balance'))
            current_total = sum(journal_item_ids.mapped('balance'))
            variance = current_total - previous_total
            return {'previous_total':previous_total,'current_total':current_total,'variance':variance}

        return {
            'doc_ids': docids,
            'active_record':active_record,
            'get_revenue':get_revenue,
            'get_cost_revenue':get_cost_revenue,
            'get_other_income':get_other_income,
            }


class AgedReceivablePayableReport(models.TransientModel):
    _name = "aged.receivable.payable"
    _description = 'Aged Receivable Payable Report'

    partner_ids = fields.Many2many(comodel_name="res.partner",string='Select Partner')
    report_type = fields.Selection([('Both', 'Both(Receivable/Payable)'), ('Receivable', 'Receivable'),('Payable','Payable')], string='Report Type', required=True,default="Both") #,('balance','Balance Sheet'),('income','Income Statement')
    date = fields.Date(string="Date",default=date.today())
    with_detail = fields.Boolean(string="With Detail")
    include_draft = fields.Boolean(string="Include Draft Invoice/Bill")
    file = fields.Binary(string='File')
    comparison_date = fields.Date(string='Comparison Date')
    is_month_wise = fields.Boolean(string='Month Wise')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

    # @api.onchange('report_type')
    # def get_partner_ids(self):
    #     partners = []
    #     if self.report_type == 'Both': # self.report_type == 'balance' or self.report_type == 'income':
    #         partner_data = self.env['res.partner'].search(['|',('customer_approval','=', 'Customer Validated'),('vendor_approval','=', 'Vendor Validated')]).ids
    #
    #     if self.report_type == 'Receivable':
    #         partner_data = self.env['res.partner'].search([('customer_approval','=', 'Customer Validated')]).ids
    #
    #     if self.report_type == 'Payable':
    #         partner_data = self.env['res.partner'].search([('vendor_approval','=', 'Vendor Validated')]).ids
    #
    #     domain = {'partner_ids': [('id', 'in', partner_data)]}
    #     return {'domain': domain, 'value': {'partner_ids': []}}

    def generate_report(self):
        data = {}
        data['form'] = self.read(['partner_ids','report_type','date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        if self.report_type == 'balance': # not self.comparison_date and not self.is_month_wise:
            return self.env.ref('aged_receivable_payable.report_for_balance_sheet_pdf').report_action(self, data=data)
        else:
            data['form'].update(self.read(['partner_ids', 'report_type', 'date'])[0])
            return self.env.ref('aged_receivable_payable.report_for_aged_rece_pay_id').report_action(self, data=data)

    # get month and year
    def get_month_year(self):
        month_year = []

        start_date = self.from_date
        end_date = self.to_date

        cur_date = start = datetime.strptime(str(start_date), '%Y-%m-%d').date()
        end = datetime.strptime(str(end_date), '%Y-%m-%d').date()

        while cur_date < end:
            list = [str(cur_date.month),calendar.month_abbr[cur_date.month],str(cur_date.year)]
            month_year.append(list)
            cur_date += relativedelta(months=1)

        return month_year

    # Define XLSX Report Button Function
    def print_xlsx_report(self):
        if self.report_type == 'Both' or self.report_type == 'Receivable' or self.report_type == 'Payable':
            datas = {
                'wizard_data': self.read()
            }
            print(666666666666666666666666666666666666666, datas)
            # , data = datas
            return self.env.ref('aged_receivable_payable.action_aged_receivable_payable_xlsx_report').report_action(self)

