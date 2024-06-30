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
    # number_of_pics = fields.Integer("Pics")


