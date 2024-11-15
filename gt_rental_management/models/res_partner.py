from datetime import datetime, date, time, timedelta
import datetime
from datetime import date
from functools import partial
from itertools import groupby
from odoo.fields import Command

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class PartnerTemplate(models.Model):
    _inherit = "res.partner"

    customer_id = fields.Char('Customer ID')
    site_email = fields.Char('Site Email')
    contact2_name = fields.Char('Contact 2 Name')
    contact2_phone = fields.Char('Contact 2 Phone')
    contact2_email = fields.Char('Contact 2 Email')

    contact3_name = fields.Char("Contact 3 Name")
    contact3_phone = fields.Char("Contact 3 Phone")
    contact3_email = fields.Char('Contact 3 Email')


    active_address = fields.Boolean(string="Active", default=True)

    notes = fields.Char('Notes')
    plug = fields.Char('Plug')
    number_of_pics = fields.Integer(string="Pics")

    contact1_name = fields.Char('Contact 1 Name')
    contact1_phone = fields.Char('Contact 1 Phone')
    contact1_email = fields.Char('Contact 1 Email')
    # contact_name_02 = fields.Char('Contact 2 Name')
    # contact_phone_02 = fields.Char('Contact 2 Phone')
    # contact_email_02 = fields.Char('Contact 2 Email')
    #
    # contact_name_03 = fields.Char("Contact 3 Name")
    # contact_phone_03 = fields.Char("Contact 3 Phone")
    # contact_email_03 = fields.Char('Contact 3 Email')

    # notes = fields.Char('Notes')
    # plug = fields.Char('Plug')
    # number_of_pics = fields.Integer("Pics")

    # Store Uses
    dry_cont = fields.Char(string="Dry cont Ct(N)")
    dry_trl = fields.Char(string="Dry Trl Ct")
    reefer_ct = fields.Char(string="Reefer Ct")
    doors_dry = fields.Char(string="Doors Dry")
    doors_ref = fields.Char(string="Doors Ref")
    cord = fields.Char(string="Cord Lgth")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Cost Info
    miles = fields.Char(string="Miles ($)")
    gallons = fields.Monetary('Gallons')
    fuel = fields.Monetary('Fuel Cost', currency_field='currency_id')
    driver = fields.Monetary('Driver Pay', currency_field='currency_id')
    expense = fields.Monetary('Expenses', currency_field='currency_id')
    net = fields.Monetary('Net', currency_field='currency_id')
    fuel_cost = fields.Monetary('Fuel Cost pG ($)', currency_field='currency_id')

    # Rental Charges
    
    dry_con_rent = fields.Monetary('Dry Con Rental', currency_field='currency_id')
    dry_trl_rent = fields.Monetary('Dry Trailer Rental', currency_field='currency_id')
    reefer_rent = fields.Monetary('Reefer Rental', currency_field='currency_id')
    del_fee = fields.Monetary('Del Fee', currency_field='currency_id')
    pickup_fee = fields.Monetary('Pickup Fee', currency_field='currency_id')
    fuel_amount = fields.Monetary('Fuel sur amount(number)', currency_field='currency_id')


    reefer_type = fields.Selection(
        string="Reefer Type",
        selection=[('dr', 'Dr'), ('er', 'Er'), ('rc', 'Rc')],
        required=False,
        default='dr'
    )
    fuel_sur = fields.Selection(
        string="Fuel Sur",
        selection=[('yes', 'Y'), ('no', 'N')],
        required=False,
        default='no'
    )
    fuel_sc = fields.Selection(
        string="Fuel SC Charge Type",
        selection=[('mil', 'Mileage'), ('pc', 'Percent Choice')],
        required=False,
        default='mil'
    )
