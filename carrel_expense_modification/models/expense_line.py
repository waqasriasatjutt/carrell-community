from odoo import api, fields, models, _

class HrExpenseLine(models.Model):
    _name = "hr.expense.line"
    _description = "Expense Line"

    expense_id = fields.Many2one('hr.expense', string="Expense", required=True, ondelete='cascade')
    part_type = fields.Selection(related='expense_id.part_type', string="Part Type", store=True, readonly=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    # type = fields.Selection(related='product_id.type')
    type = fields.Char(string="Type", compute="_compute_type", store=True)  # Updated type field to Char
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Cost")
    subtotal = fields.Float(string="Todatl Cost", compute="_compute_subtotal", store=True)
    received_by = fields.Many2one('res.users', string="Received By")
    order_for_who = fields.Many2one('res.users', string="Order For Who")

    warrinity = fields.Boolean("Warrinity")
    core = fields.Boolean("Core")
    is_return =  fields.Boolean("Return")
    mp_web = fields.Boolean("MP Web")
    asset_id = fields.Many2one('hr.asset', string="Asset", ondelete='restrict')
    # Editable field, set default from the parent expense's warehouse_id
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", ondelete='restrict')

    @api.model
    def create(self, vals):
        # If 'warehouse_id' is not provided, take it from the parent expense_id
        if 'warehouse_id' not in vals and 'expense_id' in vals:
            expense = self.env['hr.expense'].browse(vals['expense_id'])
            if expense.warehouse_id:
                vals['warehouse_id'] = expense.warehouse_id.id
        return super(HrExpenseLine, self).create(vals)

    def write(self, vals):
        if 'warehouse_id' not in vals and 'expense_id' in vals:
            expense = self.env['hr.expense'].browse(vals['expense_id'])
            if expense.warehouse_id:
                vals['warehouse_id'] = expense.warehouse_id.id
        return super(HrExpenseLine, self).write(vals)


    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.onchange('part_type')
    def _onchange_part_type(self):
        if self.part_type == 'inventory':
            return {'domain': {'product_id': [('type', '=', 'product')]}}
        elif self.part_type == 'non_inv':
            return {'domain': {'product_id': [('type', '=', 'service')]}}

    @api.depends('product_id')
    def _compute_type(self):
        for line in self:
            if line.product_id.type == 'product':
                line.type = 'Yes'  # Storable product
            elif line.product_id.type in ['service', 'consu']:
                line.type = 'No'  # Consumable product
            else:
                line.type = ''  # Default empty string if type doesn't match