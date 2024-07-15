from odoo.fields import Command

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from datetime import datetime


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import requests
import json
import logging
import re
_logger = logging.getLogger(__name__)



class HrExpense(models.Model):
    _inherit = "hr.expense"

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
