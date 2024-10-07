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
