from odoo import api, fields, models, _

class HrExpenseLine(models.Model):
    _name = "hr.asset"
    _description = "Assets"


    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Quantity", default=1.0)
    unit_price = fields.Float(string="Cost")
