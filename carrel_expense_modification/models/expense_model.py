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

    check = fields.Char("Check")
    credit_card = fields.Char("Credit Card")
    cash = fields.Char("Cash")
    employee_paid = fields.Char("Employee Paid")
    charge = fields.Float("Charge")
    cod = fields.Char("COD")
    vendor = fields.Many2one('res.partner', string="Vendors", domain="[('supplier_rank', '>', 0)]")
