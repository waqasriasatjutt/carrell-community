from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class HrExpense(models.Model):
    _inherit = "hr.expense"

    part_type = fields.Selection([
        ('inventory', 'Inventory'),
        ('non_inv', 'Non Inventory')
    ], string="Part Type", default="inventory")

    company_carrel = fields.Selection([
        ('ati', 'Ardmore Trailer Inc'),
        ('cti', 'Carrell Trucking Inc'),
        ('cts', 'Carrell Transportation Inc'),
        ('rjb', 'RBJ Trucking Inc'),
        ('rc', 'Rick Carrell Personal'),
        ('cr', 'Carrell Rentals LLC'),
        ('cl', 'Carrell Leasing LLC'),
        ('adw', 'Ardmore Dragway LLC'),
        ('race', 'Ardmore Dragway Motor Sports LLC'),
        ('customer', 'Customer'),
        ('other', 'Other'),
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

    # received_by = fields.Many2one('res.users', string="Received By", tracking=True)
    sub_category = fields.Many2one('product.product', string="Sub Cat", tracking=True)
    order_by = fields.Many2one('res.users', string="Order By", tracking=True)

    date_received = fields.Datetime(string="Time Received", readonly=True)
    received_by = fields.Many2one('res.users', string="Received By")
    received_by_with_date = fields.Char(
        string="Received By (Date)",
        compute="_compute_received_by_with_date",
        store=True
    )

    @api.model
    def create(self, vals):
        # Use Odoo's fields.Datetime.now() instead of datetime.now()
        if vals.get('received_by'):
            print(123)
            vals['date_received'] = fields.Datetime.now()
        return super(HrExpense, self).create(vals)

    def write(self, vals):
        # Use Odoo's fields.Datetime.now() instead of datetime.now()
        print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
        if 'received_by' in vals:
            print("=============received_by============")
            vals['date_received'] = fields.Datetime.now()
        return super(HrExpense, self).write(vals)

    @api.depends('received_by', 'date_received')
    def _compute_received_by_with_date(self):
        for record in self:
            if record.received_by and record.date_received:
                # Ensure that received_by is a Many2one field and its name is accessible
                record.received_by_with_date = "{} (Date received: {})".format(
                    record.received_by.name,  # Assuming it's a res.users record
                    fields.Datetime.to_string(record.date_received)
                )
            else:
                record.received_by_with_date = ""

            if record.received_by:
                record.date_received = fields.Datetime.now()

    # date_received = fields.Datetime(string="Time Received", readonly=True)
    #
    # @api.model
    # def create(self, vals):
    #     if vals.get('received_by'):
    #         vals['date_received'] = datetime.now()
    #     return super(HrExpense, self).create(vals)
    #
    # def write(self, vals):
    #     if 'received_by' in vals:
    #         vals['date_received'] = datetime.now()
    #     return super(HrExpense, self).write(vals)
    #
    # @api.depends('received_by', 'date_received')
    # def _compute_received_by_with_date(self):
    #     for record in self:
    #         if record.received_by and record.date_received:
    #             # Update the string of the field to include the date and time
    #             record.received_by_with_date = "{} (Date received: {})".format(
    #                 record.received_by.name,
    #                 fields.Datetime.to_string(record.date_received)
    #             )
    #         else:
    #             record.received_by_with_date = ""
    #
    # received_by_with_date = fields.Char(
    #     string="Received By (Date)",
    #     compute="_compute_received_by_with_date",
    #     store=True
    # )

    asset_id = fields.Many2one('hr.asset', string="Asset", ondelete='restrict')
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", ondelete='restrict')

    # Override the create method to ensure that when an expense is created, the default warehouse_id is propagated
    @api.model
    def create(self, vals):
        expense = super(HrExpense, self).create(vals)
        # Propagate warehouse_id to the expense lines if they exist
        if expense.warehouse_id and expense.expense_line_ids:
            for line in expense.expense_line_ids:
                line.warehouse_id = expense.warehouse_id.id
        return expense

    def write(self, vals):
        res = super(HrExpense, self).write(vals)
        # Propagate warehouse_id to the expense lines if updated
        if 'warehouse_id' in vals:
            for line in self.expense_line_ids:
                line.warehouse_id = vals.get('warehouse_id')
        return res

    order_for_who = fields.Many2one('res.users', string="Order For Who")
    paid_date = fields.Date("Paid Date")
    expense_code = fields.Char(string="Expense Code", readonly=True, copy=False, default='New')
    po_number = fields.Char(string="PO Number",)
    po_des = fields.Char(string="PO Description",)
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

    # asset_id = fields.Many2one('hr.asset', string="Asset", ondelete='restrict')

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

    sequence = fields.Char(string='Expense Reference', required=True, copy=False, readonly=True,
                           default=lambda self: 'New')

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            # Get the next sequence number
            vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.expense') or 'New'
        return super(HrExpense, self).create(vals)
