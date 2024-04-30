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
    rig = fields.Char(string='RIG')
    lease = fields.Char(string='Lease')
    operator = fields.Char(string='Operator')
    pu_at =  fields.Char(string='PU AT')
    del_to = fields.Char(string='Del To')
    s_instruction = fields.Char(string='Special Instruction')
    product = fields.Many2one(
        comodel_name='product.product',
        string="Product")
    driver_pay = fields.Float(string='Driver Pay')
    pin = fields.Char(string='PIN')
    mp_number = fields.Char(string='MP Web Order Number')
    bar_price = fields.Float(string='Bar Price')
    flat_price = fields.Float(sting='Flat Price')
    fuel_s_rate = fields.Float(string='Fuel Sur Rate')
    trucking_cost = fields.Float(string='Trucking Cost')
    fuel_s_cost = fields.Float(string='Fuel Sur Cost')
    bar_cost = fields.Float(string='Bar Cost')
    other_services = fields.Float(string='Other Services')
    total_amount_carrel = fields.Float(string='Total Amount')
    fc = fields.Float(string='FC %')

    partner_contact1 = fields.Many2one(
        comodel_name='res.partner',
        string="Contact 1",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    partner_contact2 = fields.Many2one(
        comodel_name='res.partner',
        string="Contact 2",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    contact_phone1 = fields.Char(string='Contact1 Phone', related='partner_contact1.phone')
    contact_email1 = fields.Char(string='Contact1 Email', related='partner_contact1.email')
    contact_phone2 = fields.Char(string='Contact2 Phone', related='partner_contact2.phone')
    contact_email2 = fields.Char(string='Contact2 Email', related='partner_contact2.email')

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

    order_status = fields.Selection([ ('transfer', 'Transfer'), ('billed', 'Billed'), ('paid', 'Paid')], required=True, default='transfer')
    trailer = fields.Integer(string='Trailer')
    truck = fields.Char('Truck')
    notes = fields.Char('Notes')
    weight = fields.Float(string='Weight')
    start_date = fields.Date(string='Start Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('hr.employee',string='Driver')





