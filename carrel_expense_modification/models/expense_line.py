from odoo import api, fields, models, _

class HrExpenseLine(models.Model):
    _name = "hr.expense.line"
    _description = "Expense Line"

    expense_id = fields.Many2one('hr.expense', string="Expense", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", required=True)
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
