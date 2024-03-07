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

# class SaleOrderGF(models.Model):
#     _inherit = "stock.picking"



class SaleOrderGF(models.Model):
    _inherit = "sale.order"
    



    pro_number = fields.Char(string='Pro Number A')
    mp_number = fields.Char(string='MP Web Order Number')

    goformz_status = fields.Selection([('ordered', 'Ordered'), ('dpending', 'Delivery Pending'), ('delivered', 'Delivered'), ('ppending', 'Pickup Pending'), ('picked', 'Picked'), ('complete', 'Complete'), ('billed', 'Billed'), ('canceled', 'Canceled'), ('void', 'Void')], required=True, default='ordered')
    trailer = fields.Integer(string='Trailer')
    weight = fields.Float(string='Weight')
    start_date = fields.Date(string='Start Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('hr.employee',string='Driver')





