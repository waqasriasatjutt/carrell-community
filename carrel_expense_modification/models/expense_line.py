from odoo import api, fields, models, _

class HrExpenseLine(models.Model):
    _name = "hr.expense.line"
    _description = "Expense Line"

    expense_id = fields.Many2one('hr.expense', string="Expense", required=True, ondelete='cascade')
    part_type = fields.Selection(related='expense_id.part_type', string="Part Type", store=True, readonly=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    type = fields.Selection(related='product_id.type')
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)

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
