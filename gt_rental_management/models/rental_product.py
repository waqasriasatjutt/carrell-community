    #
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, date, time, timedelta
import datetime
from datetime import date
from functools import partial
from itertools import groupby
from odoo.fields import Command
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    replacement_value = fields.Float('Replacement Value')
    rental = fields.Boolean('Can be Rented')
    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    part_type = fields.Selection([
        ('inventory', 'Inventory'),
        ('non_inv', 'Non Inventory')
    ], string="Part Type", default="inventory")

    goformz_status = fields.Selection([('ordered', 'Ordered'), ('dpending', 'Delivery Pending'), ('delivered', 'Delivered'), ('ppending', 'Pickup Pending'), ('picked', 'Picked Up'), ('complete', 'Complete'), ('billed', 'Billed'), ('canceled', 'Canceled'), ('void', 'Void'), ('sold', 'Sold'), ('move', 'Move'), ('purchased', 'Purchased')], required=True, default='ordered')
    trailer = fields.Integer(string='Trailer')
    weight = fields.Float(string='Weight')
    invoice_notes = fields.Char("Invoice Notes")
    po_number = fields.Char("PO Number")
    # driver = fields.Many2one('hr.employee',string='Driver')

    
    #@api.multi

    order_line_sequence = fields.Text(string="Order Line Sequence", compute="_compute_order_line_sequence")
    order_line_quantities = fields.Text(string="Order Line Quantities", compute="_compute_order_line_quantities")


    @api.depends('order_line')
    def _compute_order_line_quantities(self):
        for order in self:
            quantities = []
            product_quantities = {}
            for line in order.order_line:
                if line.product_id.detailed_type == 'product':
                    product_name = line.product_id.name
                    product_quantities[product_name] = product_quantities.get(product_name, 0) + line.product_uom_qty
            
            for product, qty in product_quantities.items():
                quantities.append(f"{int(qty)} {product}")
            
            order.order_line_quantities = "\n".join(quantities)

    @api.depends('order_line')
    def _compute_order_line_sequence(self):
        for order in self:
            sequences = []
            base_sequence = order.name.replace('RENTAL', '')  # Assuming 'RENTAL' is the prefix in order name
            sequence_number = 1
            for line in order.order_line:
                if line.product_id.detailed_type == 'product':
                    for qty in range(int(line.product_uom_qty)):  # Loop through each quantity
                        line_name = f"{base_sequence}-{sequence_number:02d} {line.product_id.name}"
                        sequences.append(line_name)
                        sequence_number += 1
            order.order_line_sequence = "\n".join(sequences)

    def _compute_del_numbers(self):
        for rec in self:
            qty = 0
            order_number = ""
            match = re.match(r'RENTAL(\d+)', rec.name)
            del_number = None
            if match:
                order_number = match.group(1)
                for order_line in rec.order_line:
                    if order_line.product_id.detailed_type == 'product':
                        del_number = f"DEL{order_number}"
                        # del_number_list.append(del_number)

                        qty = qty + order_line.product_uom_qty
                qty = int(qty)
                if del_number:
                    all_del_number = f"{del_number}-1 TO {del_number}-{qty}"
                    rec.del_numbers = all_del_number
                else:
                    rec.del_numbers = ""

            else:
                order_number = ""
            # Loop through order lines and update quantities based on product names
            # for order_line in rec.order_line:
            #     if order_line.product_id.detailed_type == 'product':
            #         del_number = f"DEL{order_number}"
            #         # del_number_list.append(del_number)

            #         qty = qty + order_line.product_uom_qty
            # qty = int(qty)
            # all_del_number = f"{del_number}-1 TO {del_number}-{qty}"
            # rec.del_numbers = all_del_number

    def _compute_state_new(self):
        for rec in self:
            rec.state_new = rec.state 
            
    def _compute_all_delivery(self):
        self.quantity_total = 0
        for rec in self.order_line:
            self.quantity_total = self.quantity_total +  rec.product_uom_qty

    contact_email = fields.Char(related='partner_id.email',string='Contact Email')
    contact_phone = fields.Char(related='partner_id.phone',string='Contact Phone')

    partner_invoice_id_email = fields.Char(related='partner_invoice_id.email',string='Contact Email')
    partner_invoice_id_phone = fields.Char(related='partner_invoice_id.phone',string='Contact Phone')

    partner_shipping_id_email = fields.Char(related='partner_shipping_id.email',string='Contact Email')
    partner_shipping_id_phone = fields.Char(related='partner_shipping_id.phone',string='Contact Phone')


    address_type = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Bill To'),
        ('delivery', 'Delivery'),
        ('private', 'Private'),
        ('other', 'Other'),
    ], string='Address Type', default='contact')


    door = fields.Selection([
        ('cab', 'Cab'),
        ('rear', 'Rear'),
        ('swing', 'Swing'),
        ('roll', 'Roll'),
    ], string='Doors')

    plug = fields.Selection([
        ('plug', 'Plug'),
        ('hardwire', 'Hardwire'),
        ('have cord', 'Have Cord'),
        ('special', 'Special'),
    ], string='Plug')


    address_type_invoice = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Bill To'),
        ('delivery', 'Delivery'),
        ('private', 'Private'),
        ('other', 'Other'),
    ], string='Address Type', default='invoice')

    manual_order_number = fields.Char(default="SET TO AUTO")

    address_type_delivery = fields.Selection([
        ('contact', 'Contact'),
        ('invoice', 'Bill To'),
        ('delivery', 'Delivery'),
        ('private', 'Private'),
        ('other', 'Other'),
    ], string='Address Type', default='delivery')
    sage_inv = fields.Char("Sage Invoice Number")
    bill_amount = fields.Float("Bill")
    min_rental_period = fields.Integer("Minimum Rental Period (MONTH)")
    date_paid = fields.Date(string='Date Paid', copy=False)
    miles = fields.Float(string='Miles')
    fuel = fields.Float(string='Fuel')
    driver_pay = fields.Float(string='Driver Pay')
    expenses = fields.Float(string='Expenses')
    net = fields.Float(string='Net')
    fuel_cost = fields.Float(string='Fuel Cost')
    fuel_surcharge = fields.Float(string='Fuel Surcharge')
    fuel_sc_amount = fields.Float(string='Fuel SC Amount')

    customer_id = fields.Char(related='partner_id.customer_id')
    quantity_total = fields.Integer('Total Delivery', compute='_compute_all_delivery', store=False)            
    customer_note = fields.Char('Customer Note')
    delivery_note = fields.Char('Delivery Note')
    site_note = fields.Char('Site Note')
    start_date = fields.Date(string='Start Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='Pu Date', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    agreement_received = fields.Boolean('Agreement Received?')
    initial_term = fields.Integer('Initial Terms (Months)')
    purchase_price = fields.Float('Purchase Price')
    del_numbers = fields.Char("Del Numbers", compute='_compute_del_numbers', store= False)
    # l10n_in_journal_id = fields.Many2one('account.journal', string="Journal", store=True, readonly=True)

    state_new = fields.Selection([
    ('draft', 'Quotation'),
    ('sent', 'Sent'),
    ('sale', 'Confirmed Rental'),
    ('done', 'Locked'),
    ('cancel', 'Closed Rental'),
    ], string='Status', default='draft', compute='_compute_state_new')
    
    
    
    @api.model
    def cron_product_rental(self):
        sale_obj = self.search([('agreement_received', '=', True)])
        res_obj = self.env['res.company'].search([])
        for sale in sale_obj:
            for res in res_obj:
                if res.reminder_days <= 5:
                    template = self.env.ref('gt_rental_management.rental_stock_notification_email_template1')
                    mail_id = template.send_mail(sale.id)
                    mail_now = self.env['mail.mail'].browse(mail_id)
                    mail_now.send()
                if res.reminder_days == 0:
                   template = self.env.ref('gt_rental_management.rental_stock_notification_email_template2')
                   mail_id = template.send_mail(sale.id)
                   mail_now = self.env['mail.mail'].browse(mail_id)
                   mail_now.send()
                   
    
    #@api.multi
    def action_confirm(self):
        print('action_confirm++++++++_____-',self.action_confirm)
        today = date.today()
        for line in self.order_line:
            print('self.order_line++++++++_____-', self.order_line)
            sale_line = self.env['sale.order.line'].search([('product_id','=', line.product_id.id)])
            print('sale_line++++++++_____-', sale_line)
            # if line.product_uom_qty > line.product_id.qty_available:
            #     print('line.product_uom_qty++++++++_____-', line.product_uom_qty)
            #     print('line.product_id.qty_available++++++++_____-', line.product_id.qty_available)
            #     for order_line in sale_line:
            #         if order_line.order_id.start_date and order_line.order_id.end_date:
            #             if order_line.order_id.start_date <= today and order_line.order_id.end_date >= today:
            #                 raise UserError(_("This product has already been rented.\nYou cannot rent already rented product.\nChange the start date and end date."
            #                              ))

        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
            
        ids =[]
        inv_line_obj = self.env['account.move.line']
        inv_obj = self.env['account.move']
        l_vals = {}
        #hp_line = self.env['helpdesk.ticket'].browse(self._context.get('active_ids', []))
        invoice_ids = []
        invoice_vals_list = []
        for order in self:
            invoice_vals = self._prepare_invoice()
            for sline in order.order_line:
                invoice_vals['invoice_line_ids'].append((0, 0, self._prepare_invoice_line_single(sline)))
            invoice_vals_list.append(invoice_vals)
            moves = self.env['account.move'].sudo().with_context(move_type='out_invoice').create(invoice_vals_list)
        return True


#     def _prepare_invoice(self):
#         """
#         Prepare the dict of values to create the new invoice for a sales order. This method may be
#         overridden to implement custom invoice generation (making sure to call super() to establish
#         a clean extension chain).
#         """
#         self.ensure_one()
#         # ensure a correct context for the _get_default_journal method and company-dependent fields
#         self = self.with_context(default_company_id=self.company_id.id, force_company=self.company_id.id)
#         #journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
# #        if not journal:
# #            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (invoice.company.name, invoice.company.id))
#         domain = [
#             ('type', '=', 'sale'),
#             ('company_id', '=', self.env.user.company_id.id),
#         ]
#         journal = self.env['account.journal'].search(domain, limit=1)
#
#         invoice_vals = {
#             'ref': self.name or '',
#             'move_type': 'out_invoice',
#             'narration': self.name,
#             'currency_id': self.company_id.currency_id.id,
#             #'campaign_id': self.campaign_id.id,
#             #'medium_id': self.medium_id.id,
#             #'source_id': self.source_id.id,
#             #'invoice_user_id': invoice.assi_to and invoice.assi_to.id,
            #'team_id': self.team_id.id,
        #     'partner_id': self.partner_id.id,
        #     'partner_shipping_id': self.partner_id.id,
        #     'partner_bank_id': self.partner_id.company_id.partner_id.bank_ids[:1].id,
        #     #'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
        #     'journal_id': self.journal_id.id,  # company comes from the journal
        #     'invoice_origin': self.name,
        #     'invoice_payment_term_id': self.partner_id.property_payment_term_id.id,
        #     'payment_reference': self.name,
        #     #'transaction_ids': [(6, 0, self.transaction_ids.ids)],
        #     'invoice_line_ids': [],
        #     'company_id': self.company_id.id,
        # }
        # return invoice_vals

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()

        return {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(
                self.partner_invoice_id)).id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_user_id': self.user_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [Command.set(self.transaction_ids.ids)],
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
        }

    def _prepare_invoice_line_single(self, invline):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {
            'display_type': 'product',
            #'sequence': self.sequence,
            'name': invline.name,
            'product_id': invline.product_id.id,
            'product_uom_id': invline.product_uom.id,
            'quantity': invline.product_uom_qty,
            #'discount': self.discount,
            'price_unit': invline.price_unit,
            'tax_ids': [(6, 0, invline.tax_id.ids)],
            #'analytic_account_id': invline.ac_analytic_id.id,
            #'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, invline.id)],
        }
        #if self.display_type:
        #res['account_id'] = False
        return res
    
    def create_invoice(self):
        ids =[]
        inv_line_obj = self.env['account.move.line']
        inv_obj = self.env['account.move']
        l_vals = {}
        ir_property_obj = self.env['ir.property']
        for order in self:
            for line in order.order_line:
                account_id = False
                if line.product_id.id:
                    account_id = line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id
                if not account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                    account_id = order.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
                if not account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (line.product_id.name,))
                
                taxes = line.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes, line.product_id, order.partner_shipping_id).ids
                else:
                    tax_ids = taxes.ids
                l_vals = {
                'name':  _('Down Payment'),
                'origin': order.name,
                'account_id': account_id,
                'price_unit': line.price_unit,
                'quantity': 1.0,
                'discount': 0.0,
                'uom_id': line.product_id.uom_id.id,
                'product_id': line.product_id.id,
                'sale_line_ids': [(6, 0, [line.id])],
                'invoice_line_tax_ids': [(6, 0, line.tax_id.ids)],
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'account_analytic_id': order.analytic_account_id.id or False,
                }
                inv_line_rec = inv_line_obj.create(l_vals)
                ids.append(inv_line_rec.id)
            invoice = inv_obj.create({
                'name': order.client_order_ref or order.name,
                'origin': order.name,
                'move_type': 'out_invoice',
                'reference': False,
                'account_id': order.partner_id.property_account_receivable_id.id,
                'partner_id': order.partner_invoice_id.id,
                'partner_shipping_id': order.partner_shipping_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                'payment_term_id': order.payment_term_id.id,
                'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
                'team_id': order.team_id.id,
                'user_id': order.user_id.id,
                'comment': order.note,
                'start_date' : order.start_date,
                'end_date' : order.end_date,
            })
            invoice.invoice_line_ids = ids
            record = invoice.compute_taxes()
            res = invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice
        
        
    #@api.multi
    def action_product_replace(self):
        rental_obj = self.env['rental.wizard']
        ids = []
        for lines in self.order_line:
            lines_dic = {
                        'quantity' : lines.product_uom_qty,
                        'product_id' : lines.product_id.id,
                        'serial_no' : lines.serial_no,
                        }
            ids.append(lines.id)
            ctx = ids
        return {
            'res_model': 'rental.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('gt_rental_management.wizard_view_rental_wizard').id,
            'type': 'ir.actions.act_window',
            'context':  {'default_rental_wizard_line': ids},
            'target': 'new',
        }
#     

    #@api.multi
    def action_renew_rental(self):
        print ("=============renew_rental============", self)
        
        
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if 'start_date' in vals and 'end_date' in vals:
            name = self.env['ir.sequence'].next_by_code('RENTAL') or '/'
            res.update({'name' :name})
        return res
        
    #@api.multi
    def action_view_delivery(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action
    
    @api.onchange('start_date', 'end_date','initial_term')
    def calculate_date(self):
        if self.start_date and self.end_date:
            d1=datetime.datetime.strptime(str(self.start_date),'%Y-%m-%d') 
            d2=datetime.datetime.strptime(str(self.end_date),'%Y-%m-%d')
            d3=d2-d1
            self.initial_term=int(d3.days)/30
    
    @api.model
    def cron_invoice_recurring_method(self):
        today = date.today()
        sale_order_obj = self.env['sale.order'].search([('agreement_received', '=', True)])
        for order in sale_order_obj:
            st_date = order.start_date + timedelta(days=order.payment_term_id.line_ids.days - 3)
            if st_date == today:
                rec = order.create_invoice()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    part_type = fields.Selection(related='order_id.part_type', string="Part Type", store=True, readonly=True)
    serial_no = fields.Char('Serial Number')
    rental_wizard_id = fields.Many2one('rental.wizard', string='Rental Wizard')
    monthly_rent = fields.Float('Monthly Rent', default=0.0)
    replace = fields.Boolean('Replace')

    @api.onchange('part_type')
    def _onchange_part_type(self):
        if self.part_type == 'inventory':
            return {'domain': {'product_id': [('type', '=', 'product')]}}
        elif self.part_type == 'non_inv':
            return {'domain': {'product_id': [('type', '=', 'service')]}}

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(SaleOrderLine, self).create(vals_list)
        lines.filtered(lambda line: line.state == 'sale')._action_launch_stock_rule()
        return lines  
    
    
    #@api.multi
#    def _prepare_invoice_line(self, qty):
#        """
#        Prepare the dict of values to create the new invoice line for a sales order line.

#        :param qty: float quantity to invoice
#        """
#        self.ensure_one()
#        res = {}
#        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id

#        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
#        if fpos and account:
#            account = fpos.map_account(account)

#        res = {
#            'name': self.name,
#            'sequence': self.sequence,
#            'origin': self.order_id.name,
#            'account_id': account.id,
#            'price_unit': self.price_unit,
#            'quantity': qty,
#            'discount': self.discount,
#            'uom_id': self.product_uom.id,
#            'product_id': self.product_id.id or False,
#            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
#            'account_analytic_id': self.order_id.analytic_account_id.id,
#            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
#            'display_type': self.display_type,
#        }
#        return res

#    #@api.multi
#    def invoice_line_create(self, invoice_id, qty):
#        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative (refund).
#            :param invoice_id: integer
#            :param qty: float quantity to invoice
#            :returns recordset of account.invoice.line created
#        """
#        invoice_lines = self.env['account.move.line']
#        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#        for line in self:
#            if not float_is_zero(qty, precision_digits=precision) or not line.product_id:
#                vals = line._prepare_invoice_line(qty=qty)
#                vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
#                invoice_lines |= self.env['account.move.line'].create(vals)
#        return invoice_lines
    

class AccountInvoice(models.Model):
    _inherit = "account.move"

    start_date = fields.Date(string='Rental Start Date')
    end_date = fields.Date(string='Rental End Date')

    
class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"    

    # name = fields.Text(string='Description')
    name = fields.Char(
        string='Label',
        compute='_compute_name', store=True, readonly=False, precompute=True,
        tracking=True,
    )
    serial_no = fields.Char('Serial Number')
    
    
class StockMoveLine(models.Model):
    _inherit = "stock.move"
    
    serial_no = fields.Char('Serial Number')
        
       


    
    
