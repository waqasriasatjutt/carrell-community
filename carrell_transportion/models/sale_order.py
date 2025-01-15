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


class ResPartner(models.Model):
    _inherit = "res.partner"

    active_address = fields.Boolean("Active", default=True)

    pu_pin = fields.Char(string='PU PIN')
    del_pin = fields.Char(string='DEL PIN')

    p_street = fields.Char('PU Street')
    p_city = fields.Char('PU City')
    p_phone = fields.Char('PU Phone')
    p_state_id = fields.Many2one('res.country.state', string="PU State")
    p_country = fields.Many2one('res.country', string="PU Country")
    pu_directions = fields.Char("Pu Directions")
    del_directions = fields.Char("Del Directions")


class SaleOrderGF(models.Model):
    _inherit = "sale.order"



    pu = fields.Many2one(
        comodel_name='res.partner',
        string='PU',
        help="Select an active delivery address related to the selected customer."
    )
    lease_address = fields.Many2one(
        comodel_name='res.partner',
        string='Lease Key',
        help="Select an active delivery address related to the selected customer."
    )



    del_street = fields.Char(related='lease_address.street')
    del_city = fields.Char(related='lease_address.city')
    del_zip = fields.Char(related='lease_address.zip')
    del_phone = fields.Char(related='lease_address.phone')
    del_email = fields.Char(related='lease_address.email')
    del_state = fields.Many2one(related='lease_address.state_id')
    del_country = fields.Many2one(related='lease_address.country_id')
    del_directions = fields.Char("Del Directions")

    
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"



    street = fields.Char(related='partner_id.street')
    city = fields.Char(related='partner_id.city')
    zip = fields.Char(related='partner_id.zip')
    phone = fields.Char(related='partner_id.phone')
    email = fields.Char(related='partner_id.email')


    pu = fields.Many2one(
        comodel_name='res.partner',
        string='Pickup Address',
        compute='_compute_pu',
        store=True,
        help="Automatically filled from the invoice address of the customer. If no invoice address exists, it defaults to the customer."
    )

    @api.depends('partner_id')
    def _compute_pu(self):
        for record in self:
            if record.partner_id:
                # Search for an "invoice" type address
                invoice_address = record.partner_id.child_ids.filtered(
                    lambda c: c.type == 'invoice'
                )
                # Set the first matching invoice address or default to the partner
                record.pu = invoice_address[0] if invoice_address else record.partner_id

    pu_street = fields.Char(related='pu.street')
    pu_city = fields.Char(related='pu.city')
    pu_zip = fields.Char(related='pu.zip')
    pu_phone = fields.Char(related='pu.phone')
    pu_email = fields.Char(related='pu.email')
    pu_state = fields.Many2one(related='pu.state_id')
    pu_country = fields.Many2one(related='pu.country_id')
    pu_directions = fields.Char("Pu Directions")


    lease_address = fields.Many2one(
        comodel_name='res.partner',
        string='Lease Address',
        compute='_compute_lease_address',
        store=True,
        help="Automatically filled from the delivery address of the customer. If no delivery address exists, it defaults to the customer."
    )

    @api.depends('partner_id')
    def _compute_lease_address(self):
        for record in self:
            if record.partner_id:
                # Search for a "delivery" type address
                delivery_address = record.partner_id.child_ids.filtered(
                    lambda c: c.type == 'delivery'
                )
                # Set the first matching delivery address or default to the partner
                record.lease_address = delivery_address[0] if delivery_address else record.partner_id


    # pu = fields.Many2one(
    #     comodel_name='res.partner',
    #     string='PU',
    #     readonly=False,
    #     check_company=True,
    #     help="The delivery address will be used in the computation of the fiscal position.",
    # )
    #
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
        Dynamically update the domain for shipping, invoicing, and PU addresses
        based on the selected customer.
        """
        for record in self:
            if record.partner_id:
                return {
                    'domain': {
                        'lease_address': [
                            ('parent_id', '=', record.partner_id.id),
                            ('active_address', '=', True),
                            ('type', '=', 'delivery'),
                        ],
                        'pu': [
                            ('parent_id', '=', record.partner_id.id),
                            ('active_address', '=', True),
                            ('type', '=', 'invoice'),
                        ],
                    }
                }
            else:
                # Reset domains if no customer is selected
                return {
                    'domain': {
                        'lease_address': [('id', '=', False)],
                        'pu': [('id', '=', False)],
                    }
                }

    mile_rate = fields.Float("Mile Rate")
    rate_type = fields.Selection(string="Rate Type", selection=[('per 100 watt', 'Per 100 Watt'), ('flat', 'Flat'), ('miles', 'Miles')], required=False, )


    price_list = fields.Selection(
        string="Price List",
        selection=[
            ('none', 'None'),
            ('basic', 'Basic'),
            ('handling_inc', 'Handling inc'),
        ],
        required=True,
    )

    bill_miles = fields.Selection(
        string="Bill Miles",
        selection=[
            ('none', 'None'),
            ('0-50', '0-50'),
            ('51-60', '51-60'),
            ('61-70', '61-70'),
            ('71-80', '71-80'),
            ('81-90', '81-90'),
            ('91-100', '91-100'),
            ('101-110', '101-110'),
            ('111-120', '111-120'),
            ('121-130', '121-130'),
            ('131-140', '131-140'),
            ('141-150', '141-150'),
            ('151-160', '151-160'),
            ('161-170', '161-170'),
            ('171-180', '171-180'),
            ('181-190', '181-190'),
            ('191-200', '191-200'),
            ('201-210', '201-210'),
            ('211-220', '211-220'),
            ('221-230', '221-230'),
            ('231-240', '231-240'),
            ('241-250', '241-250'),
            ('251-260', '251-260'),
            ('261-270', '261-270'),
            ('271-280', '271-280'),
            ('281-290', '281-290'),
            ('291-300', '291-300'),
        ],
        required=True,
    )

    bill_rate = fields.Float(string="Bill Rate", compute="_compute_bill_rate", store=True)


    @api.onchange('price_list')
    def _onchange_price_list(self):
        if self.price_list:
            # Clear or reset the fields
            self.bill_rate = 0.0
            self.flat_price = 0.0
            self.bill_miles = None


    @api.depends('price_list', 'bill_miles')
    def _compute_bill_rate(self):
        rate_chart = {
            'basic': {
                'None': 0,'0-50': 1.36, '51-60': 1.46, '61-70': 1.56, '71-80': 1.68, '81-90': 1.83,
                '91-100': 1.95, '101-110': 2.05, '111-120': 2.17, '121-130': 2.27, '131-140': 2.38,
                '141-150': 2.50, '151-160': 2.56, '161-170': 2.66, '171-180': 2.75, '181-190': 2.86,
                '191-200': 2.94, '201-210': 3.04, '211-220': 3.06, '221-230': 3.13, '231-240': 3.21,
                '241-250': 3.28, '251-260': 3.40, '261-270': 3.52, '271-280': 3.63, '281-290': 3.75,
                '291-300': 3.87,
            },
            'handling_inc': {
                'None': 0,'0-50': 1.60, '51-60': 1.70, '61-70': 1.80, '71-80': 1.92, '81-90': 2.07,
                '91-100': 2.19, '101-110': 2.29, '111-120': 2.41, '121-130': 2.51, '131-140': 2.62,
                '141-150': 2.74, '151-160': 2.80, '161-170': 2.90, '171-180': 2.99, '181-190': 3.10,
                '191-200': 3.18, '201-210': 3.28, '211-220': 3.30, '221-230': 3.37, '231-240': 3.45,
                '241-250': 3.52, '251-260': 3.64, '261-270': 3.76, '271-280': 3.87, '281-290': 3.99,
                '291-300': 4.11,
            },
            'none': {
                'None': 0,'0-50': 0, '51-60': 0, '61-70': 0, '71-80': 0, '81-90': 0,
                '91-100': 0, '101-110': 0, '111-120': 0, '121-130': 0, '131-140': 0,
                '141-150': 0, '151-160': 0, '161-170': 0, '171-180': 0, '181-190': 0,
                '191-200': 0, '201-210': 0, '211-220': 0, '221-230': 0, '231-240': 0,
                '241-250': 0, '251-260': 0, '261-270': 0, '271-280': 0, '281-290': 0,
                '291-300': 0,
            },
        }
        for record in self:
            if record.price_list and record.bill_miles:
                price_list = record.price_list or 'none'
                bill_miles = record.bill_miles or '0-50'
                record.bill_rate = rate_chart.get(price_list, {}).get(bill_miles, 0)
            else:
                record.bill_rate = 0.0


    tons = fields.Float("Tons")

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    pro_number = fields.Char(
        string="Pro Number A", 
        readonly=True, 
        copy=False, 
        default=lambda self: 'NEW'
    )

    @api.model
    def create(self, vals):
        if vals.get('pro_number', 'NEW') == 'NEW':
            vals['pro_number'] = self.env['ir.sequence'].next_by_code('sale.order.pro.number') or 'NEW'
        return super(SaleOrder, self).create(vals)    
    
    wo_number = fields.Char(string='Wo Number')
    po_number = fields.Char(string='Po Number')
    rig = fields.Selection(string="RIG", selection=[('rig_2', 'RIG 2'), ('dan', 'DAN D'), ], required=False, )
    lease = fields.Char(string='Lease')
    operator = fields.Char(string='Operator')
    pu_at =  fields.Char(string='PU AT')
    del_to = fields.Char(string='Del To')
    s_instruction = fields.Char(string='Special Instruction')
    product = fields.Many2one(
        comodel_name='product.product',
        string="Product")

    pu_pin = fields.Char(string='PU PIN')
    del_pin = fields.Char(string='DEL PIN')

    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one('res.country.state', string="State")


    mp_number = fields.Char(string='MP Web Order Number')

    fuel_s_rate = fields.Float(string='Fuel Sur Rate')
    trucking_cost = fields.Float(string="Trucking Cost", compute="_compute_trucking_cost", store=True)
    fuel_s_cost = fields.Float(string='Fuel Sur Cost')
    other_services = fields.Float(string='Other Services')
    total_charge = fields.Float(string='Total Charge', compute="_compute_total_charge")
    fc = fields.Float(string='FC %', compute="_compute_FC")


    @api.depends('trucking_cost', 'fc_price')
    def _compute_FC(self):
        for record in self:
            record.fc = record.trucking_cost * record.fc_price


    @api.depends('trucking_cost', 'fc')
    def _compute_total_charge(self):
        for record in self:
            record.total_charge = record.trucking_cost + record.fc

    @api.depends('tons', 'bill_rate', 'flat_price')
    def _compute_trucking_cost(self):
        for record in self:
            record.trucking_cost = (record.tons * 2000 / 100 * record.bill_rate) + record.flat_price

    partner_contact1 = fields.Many2one(
        comodel_name='res.partner',
        string="Contact 1",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    partner_contact2 = fields.Many2one(
        comodel_name='res.partner',
        string="Contact 2",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


    invoice_manual = fields.Char(string='Invoice #')

    contact_phone1 = fields.Char(string='Contact1 Phone', related='partner_contact1.phone')
    contact_email1 = fields.Char(string='Contact1 Email', related='partner_contact1.email')
    contact_phone2 = fields.Char(string='Contact2 Phone', related='partner_contact2.phone')
    contact_email2 = fields.Char(string='Contact2 Email', related='partner_contact2.email')

    date_order_changed_by = fields.Many2one(
        'res.users', 
        string="Date Changed By", 
        readonly=True, 
        help="User who last modified the Order Date"
    )

    @api.onchange('date_order')
    def _onchange_date_order(self):
        """Track the user who changes the date_order."""
        if self.date_order:
            self.date_order_changed_by = self.env.user


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

    # order_status = fields.Selection([ ('transfer', 'Transfer'), ('billed', 'Billed'), ('paid', 'Paid')], required=True, default='transfer')
    trailer = fields.Integer(string='Trailer')
    truck = fields.Char('Truck')
    notes = fields.Char('Notes')
    weight = fields.Float(string='Weight')
    start_date = fields.Date(string='Start Date',  default=fields.Date.context_today,
        readonly=True, copy=False, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='End Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    driver = fields.Many2one('hr.employee', string='Driver', context={'create': False}, )

    bill_type = fields.Selection(string="Bill Type", selection=[('flat', 'Flat'), ('miles', 'Miles'), ('lb', '100 LB'),('ton', 'Ton'), ], required=False, )
    fc_type = fields.Selection(string="FC Type SEL", selection=[('none', 'None'), ('miles', 'Miles'), ('percent', 'Percent'), ], required=False, )
    product_type = fields.Selection(string="Product Type", selection=[('all', 'All'), ('bar', '3.9 BAR'), ('bar_2', '4.1 Bar'), ('sack','SACK'), ('rental', 'Rental Only'), ], required=False, )
    bar_type = fields.Selection(string="BAR Type", selection=[('secl', 'SECL 3.9'), ('owner', 'OWNER 4.1'), ('own_1', 'OWNED 3.9'), ('sell_4', 'SELL 4.1'), ('sell', 'SELL'), ('all', 'ALL') ], required=False, )


    warehouse = fields.Float(string='Warehouse')


    bar_price = fields.Monetary(string='Bar Price',compute="_compute_bar_price", currency_field='currency_id')
    bar_per_ton = fields.Monetary(string='Bar Per Tons', currency_field='currency_id')

    @api.depends('bar_per_ton', 'tons')
    def _compute_bar_price(self):
        for record in self:
            record.bar_price = record.bar_per_ton * record.tons 


    flat_price = fields.Monetary(sting='Flat Price', currency_field='currency_id')
    fc_price = fields.Monetary(sting='FC Rate', currency_field='currency_id')
    fork_lift_price = fields.Monetary(sting='Fork Lift Charge', currency_field='currency_id')
    labour_charge = fields.Monetary(sting='Stacking/Labour Charge', currency_field='currency_id')
    rental_tank = fields.Monetary(sting='Rentals Tank', currency_field='currency_id')
    rental_stand = fields.Monetary(sting='Rentals Stand', currency_field='currency_id')
    rental_mat = fields.Monetary(sting='Rentals Matt', currency_field='currency_id')
    rental_comp = fields.Monetary(sting='Rentals Comp', currency_field='currency_id')
    miles_group = fields.Monetary(sting='Miles Group', currency_field='currency_id', digits=(16, 2))

    rev_fixed_cost = fields.Monetary(sting='Rev Fixed Cost', currency_field='currency_id')
    cpg = fields.Monetary(sting='CPG', currency_field='currency_id')
    fuel_cost = fields.Monetary(sting='Fuel Cost(GL Used CPG)', currency_field='currency_id')


    miles = fields.Float(string='Act Miles')
    mpg = fields.Float(sting='MPG', default=5)
    gall_used = fields.Float(string='Gall Used', compute='_compute_gall_used', store=True)

    @api.depends('miles', 'mpg')
    def _compute_gall_used(self):
        for record in self:
            record.gall_used = record.miles / record.mpg if record.mpg else 0

    driver_over = fields.Float(string='Driver Overhead Percentage')
    driver_pay = fields.Monetary(sting='Driver Pay', currency_field='currency_id', digits=(16, 2))
    driver_total = fields.Float(string='Driver Total', compute='_compute_driver_total',  store=True )
    per_cent = fields.Monetary(sting='Per Cent', default=1.25,currency_field='currency_id', digits=(16, 2))
    other_total = fields.Monetary(sting='Other Total',currency_field='currency_id', digits=(16, 2))

    @api.depends('driver_over', 'driver_pay')
    def _compute_driver_total(self):
        for record in self:
            record.driver_total = record.driver_over * record.driver_pay

    gross_expence = fields.Float(string='TOTS Of Expense', compute='_compute_gross_expence', store=True)

    @api.depends('driver_total', 'fuel_cost')
    def _compute_gross_expence(self):
        for record in self:
            record.gross_expence = record.driver_total + record.fuel_cost

    gross_total = fields.Monetary(sting='Gross Total', currency_field='currency_id', digits=(16, 2))
    net_total = fields.Monetary(string='Net Total', currency_field='currency_id', compute='_compute_net_total',
                                store=True,)

    @api.depends('gross_total', 'gross_expence')
    def _compute_net_total(self):
        for record in self:
            # Calculate net_total as gross_total minus gross_expence
            record.net_total = record.gross_total - record.gross_expence


