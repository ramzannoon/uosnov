from odoo import _, api, fields, models


class AdjudicationElements(models.Model):
    _name = "emp.report"
    _description = "Adjudication Elements"
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Adjudication Elements", required=True, )
    ahsan = fields.Char(string="Adjudication Elements", required=True, )


    def action_print_payslip(self):
        return {
            'name': 'Payslip',
            'type': 'ir.actions.act_url',
            'url': '/print/payslips?list_ids=%(list_ids)s' % {'list_ids': ','.join(str(x) for x in self.ids)},
        }
