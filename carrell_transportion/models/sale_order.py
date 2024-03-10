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
    


    miles = fields.Integer(string='Miles')
    miles_group = fields.Integer(string='Miles Group')
    mile_rate = fields.Float("Mile Rate")
    tons = fields.Float("Tons")

    pro_number = fields.Char(string='Pro Number A')
    wo_number = fields.Char(string='Wo Number')
    po_number = fields.Char(string='Po Number')
    mp_number = fields.Char(string='MP Web Order Number')

    order_status = fields.Selection([
    ('pullfromlist', 'Pull From List'),
    ('preloaded', 'Preloaded'),
    ('return', 'Return'),
    ('delivered', 'Delivered'),
    ('need billing', 'Need Billing'),
    ('transfer', 'Transfer'),
    ('billed', 'Billed'),
    ('paid', 'Paid'),
    ('void', 'Void'),
    ], string='Order Status', default='pullfromlist')

    delivery_type = fields.Selection([
    ('delivery', 'Delivery'),
    ('splitdelivery', 'Split Delivery'),
    ('return', 'Return'),
    ('transfer', 'Transfer'),
    ('labor', 'Labor'),
    ], string='Delivery Type', default='delivery')

    load_type = fields.Selection([
    ('sack', 'Sack'),
    ('bulk', 'Bulk'),
    ('sellbulknt', 'Sell Bulk No Trucking'),
    ('sellbulkt', 'Sell Bulk Trucking'),
    ], string='Load Type', default='sack')

    fork_lift = fields.Selection([
    ('yes', 'Yes'),
    ('no', 'No'),
    ], string='Fork Lift', default='yes')

    goformz_status = fields.Selection([('ordered', 'Ordered'), ('dpending', 'Delivery Pending'), ('delivered', 'Delivered'), ('ppending', 'Pickup Pending'), ('picked', 'Picked'), ('complete', 'Complete'), ('billed', 'Billed'), ('canceled', 'Canceled'), ('void', 'Void')], required=True, default='ordered')
    trailer = fields.Integer(string='Trailer')
    weight = fields.Float(string='Weight')
    start_date = fields.Date(string='Start Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('hr.employee',string='Driver')





