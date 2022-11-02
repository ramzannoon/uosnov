from odoo.osv import expression
from odoo import models, fields, api, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char('Code')
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual/AOP'), ('company', 'Company')],
                                    compute='_compute_company_type', inverse='_write_company_type')

    tax_payer_state_income = fields.Selection(string='Tax Payer State',
                                              selection=[('reg', 'Registered'), ('non_reg', 'Non Registered')],
                                              default=None)
    wth_for_goods = fields.Many2one('account.tax', string='WithHeld Tax for Goods',
                                    domain=[('withholding_tax', '=', True)])
    wth_for_service = fields.Many2one('account.tax', string='WithHeld Tax for Service',
                                      domain=[('withholding_tax', '=', True)])

    tax_payer_state_sales = fields.Selection(string='Tax Payer State',
                                             selection=[('reg', 'Registered'), ('non_reg', 'Non Registered')],
                                             default=None)
    sales_tax_for_goods = fields.Many2one('account.tax', string='Sales Tax for Goods',
                                          domain=[('withholding_tax', '=', True)])
    sales_tax_for_service = fields.Many2one('account.tax', string='Sales Tax for Service',
                                            domain=[('withholding_tax', '=', True)])

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for partner in self:
            name = partner.name
            if partner.code:
                name = partner.code + '-' + name
            result.append((partner.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', '%' + name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
