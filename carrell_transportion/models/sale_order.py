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



    street = fields.Char(related='partner_invoice_id.street')
    city = fields.Char(related='partner_invoice_id.city')
    zip = fields.Char(related='partner_invoice_id.zip')
    phone = fields.Char(related='partner_invoice_id.phone')
    email = fields.Char(related='partner_invoice_id.email')


    pu = fields.Many2one(
        comodel_name='res.partner',
        string='Pickup Address',
        help="Select an active delivery address related to the selected customer."
    )


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
        help="Select an active delivery address related to the selected customer."
    )



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

    bill_type = fields.Selection(string="Bill Type", selection=[('flat', 'Flat'), ('miles', 'Miles'), ('lb', '100 LB'), ], required=False, )
    fc_type = fields.Selection(string="FC Type SEL", selection=[('none', 'None'), ('miles', 'Miles'), ('percent', 'Percent'), ], required=False, )
    product_type = fields.Selection(string="Product Type", selection=[('all', 'All'), ('bar', '3.9 BAR'), ('bar_2', '4.1 Bar'), ('sack','SACK'), ('rental', 'Rental Only'), ], required=False, )
    bar_type = fields.Selection(string="BAR Type", selection=[('secl', 'SECL 3.9'), ('owner', 'OWNER 4.1'), ('own_1', 'OWNED 3.9'), ('sell_4', 'SELL 4.1'), ('sell', 'SELL'), ('all', 'ALL') ], required=False, )


    warehouse = fields.Float(string='Warehouse')


    bar_price = fields.Monetary(string='Bar Price', currency_field='currency_id')
    flat_price = fields.Monetary(sting='Flat Price', currency_field='currency_id')
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


    miles = fields.Float(string='Miles')
    mpg = fields.Float(sting='MPG', default=5)
    gall_used = fields.Float(string='Gall Used', compute='_compute_gall_used', store=True)

    @api.depends('miles', 'mpg')
    def _compute_gall_used(self):
        for record in self:
            record.gall_used = record.miles / record.mpg if record.mpg else 0

    driver_over = fields.Float(string='Driver Overhead Percentage')
    driver_pay = fields.Monetary(sting='Driver Pay', currency_field='currency_id', digits=(16, 2))
    driver_total = fields.Float(string='Driver Total', compute='_compute_driver_total',  store=True )

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


