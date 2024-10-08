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

    # Cost Info
    miles = fields.Char(string="Miles ($)")
    gallons = fields.Float('Gallons')
    fuel = fields.Float('Fuel Cost')
    driver = fields.Float('Driver Pay')
    expense = fields.Float('Expenses')
    net = fields.Float('Net')
    fuel_cost = fields.Float('Fuel Cost pG ($)')

    # Rental Charges
    dry_con_rent = fields.Float('Dry Con Rental')
    dry_trl_rent = fields.Float('Dry Trailer Rental')
    reefer_rent = fields.Float('Reefer Rental')
    del_fee = fields.Float('Del Fee')
    pickup_fee = fields.Float('Pickup Fee')
    fuel_amount = fields.Float('Fuel sur amount(number)')  # Fixed typo here

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
