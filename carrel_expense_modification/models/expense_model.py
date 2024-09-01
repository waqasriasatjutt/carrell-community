from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    part_type = fields.Selection([
        ('inventory', 'Inventory'),
        ('non_inv', 'Non Inventory')
    ], string="Part Type", default="inventory")

    company_carrel = fields.Selection([
        ('ati', 'ATI'),
        ('cti', 'CTI'),
        ('cts', 'CTS'),
        ('rjb', 'RJB'),
        ('rc', 'RC'),
        ('cr', 'CR'),
        ('cl', 'CL'),
        ('adw', 'ADW'),
        ('race', 'RACE'),
        ('customer', 'Customer'),
    ], string='Company')

    pay_type = fields.Selection([
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('employee_paid', 'Employee Paid'),
        ('charge', 'Charge'),
        ('cod', 'COD'),
        ('employee_bill', 'Employee Use Bill Back'),
    ], string='Pay Type')

    vendor = fields.Many2one('res.partner', string="Vendors", domain="[('supplier_rank', '>', 0)]")
    received_status = fields.Selection([
        ('ordered', 'Ordered'),
        ('pickedup', 'Picked Up'),
        ('overnight', 'Over Night'),
    ], string='Received Status')

    received_by = fields.Many2one('res.users', string="Received By")
    order_for_who = fields.Many2one('res.users', string="Order For Who")
    paid_date = fields.Date("Paid Date")
    expense_code = fields.Char(string="Expense Code", readonly=True, copy=False, default='New')
    expense_line_ids = fields.One2many('hr.expense.line', 'expense_id', string="Expense Lines")
    # company_select = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_select = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='restrict',
        context={'create': True}
    )

    asset_id = fields.Many2one('hr.asset', string="Asset",  ondelete='restrict')



    def _generate_expense_code(self, company):
        sequence_code = 'hr.expense.' + company.lower()
        return self.env['ir.sequence'].next_by_code(sequence_code) or '/'

    @api.model
    def create(self, vals):
        if vals.get('expense_code', 'New') == 'New':
            if 'company_carrel' in vals:
                company = vals['company_carrel']
                vals['expense_code'] = self._generate_expense_code(company)
            else:
                raise UserError(_('Please select a company before saving the record.'))
        return super(HrExpense, self).create(vals)

    order_total = fields.Float('Total', compute='_compute_calculation_pickup', store=True)

    @api.depends('expense_line_ids.product_id', 'expense_line_ids.subtotal')
    def _compute_calculation_pickup(self):
        for rec in self:
            # Summing up the 'price_subtotal' for all order lines
            rec.order_total = sum(rec.expense_line_ids.mapped('subtotal'))
            print("Total Order Line Value ------- ", rec.order_total)


    sequence = fields.Char(string='Expense Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            # Get the next sequence number
            vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.expense') or 'New'
        return super(HrExpense, self).create(vals)