from odoo.fields import Command

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
import requests
import json
import logging

# class SaleOrderGF(models.Model):
#     _inherit = "stock.picking"


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        url = "https://api.goformz.com/v2/formz"
        for picking in self:
            order = self.env['sale.order'].sudo().search([('name','=', picking.origin)])
            if picking.state != 'cancel':
                for serial in picking.move_line_ids_without_package:
                    if serial.lot_id and ( serial.reserved_uom_qty == 1 or serial.qty_done == 1):
                        payload = json.dumps({
                        "name": f"{order.name} {order.partner_id.name} {order.partner_shipping_id.street} {order.partner_shipping_id.city} {order.partner_shipping_id.state_id.name} {order.date_order} {serial.lot_id.name}",
                        # "name":' {self.name} Creating new one from epi',
                        "templateId": "105e3109-ad03-42e3-8444-c4cdcd060b23",
                        "fields": {
                            "Order Number": {
                            "value": order.name,
                            "id": "d20e57e8-c6e2-4e7c-af5c-b943aba5126c",
                            "name": "Order Number",
                            "type": "Number"
                            },
                            "Customer Name": {
                            "value": order.partner_id.name,
                            "id": "a8a19313-34ce-47bc-96cf-3a3297c04c42",
                            "name": "Customer Name",
                            "type": "Database"
                            },
                        "Order Date": {
                            "value": str(order.date_order),
                            "displayValue": str(order.date_order),
                            "id": "654a748e-eccc-4b3c-a8fc-e337234330d6",
                            "name": "Order Date",
                            "type": "Date"
                        },
                        },
                        "assignment": {
                            "id": "4f90a5f4-0327-402b-a0e7-5fa4976001aa",
                            "type": "User"
                        }
                        })
                        headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'Authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                        }

                        response = requests.request("POST", url, headers=headers, data=payload)

                        print(response.text)
                        print('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')
        return res

    


class SaleOrderLineCarrel(models.Model):
    _inherit = "sale.order.line"

    form_id = fields.Char("Goformz ID")
    


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    form_id = fields.Char("Goformz ID")
    


class SaleOrderGF(models.Model):
    _inherit = "sale.order"
    

    def action_update_from_goformz1(self):
        url = "https://api.goformz.com/v2/formz?name="+self.name

        payload = ""
        headers = {
        'accept': 'application/json',
        'authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ==',
        'Content-Type': 'text/plain'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        logging.info(response.text)

        if response.status_code == 200:
            forms_data = response.json()

            # Extract form IDs and call another API
            for form in forms_data:
                form_id = form.get("formId")
                if form_id:
                    # Call another API with the form ID

                    url = "https://api.goformz.com/v2/formz/"+form_id

                    payload = {}
                    headers = {
                    'accept': 'application/json',
                    'authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                    }

                    response = requests.request("GET", url, headers=headers, data=payload)

                    logging.info(response.text)



    def action_update_from_goformz(self):
        for order_line in self.order_line:
            form_ids = order_line.form_id.split(',')
            pickings = self.env['stock.picking'].sudo().search([('sale_id','=', self.id)])
            serial_ids =[]
            for form_id in form_ids:
                # Call another API with each form ID
                url = f"https://api.goformz.com/v2/formz/{form_id}"

                payload = {}
                headers = {
                    'accept': 'application/json',
                    'authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                logging.info(response.text)
                forms_data = response.json()

                # Extract form IDs and call another API
                try:
                    unit = forms_data['fields']['Unit Number']['value']
                    if unit:
                        serial_ids.append(unit)
                        print(response.text)
                        order_line.serial_no = ','.join(map(str, serial_ids))
                except:
                    print('failed')



    def action_update_from_goformz3(self):
        for rec in self:
            pickings = self.env['stock.picking'].sudo().search([('sale_id','=', rec.id)])
        for picking in pickings:
            if picking.state != 'cancel':
                for serial in picking.move_line_ids_without_package:
                    if serial.form_id:
                        url = f"https://api.goformz.com/v2/formz/{serial.form_id}"

                        payload = {}
                        headers = {
                            'accept': 'application/json',
                            'authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)

                        logging.info(response.text)
                        forms_data = response.json()

                        # Extract form IDs and call another API
                        unit = forms_data['fields']['Unit Number']['value']
                        if unit:
                            lot = self.env['stock.lot'].sudo().search([('name','=', unit),('product_id','=',serial.product_id.id)])
                            serial.lot_id = lot.id




    def action_confirm(self):
        res = super(SaleOrderGF, self).action_confirm()

        url = "https://api.goformz.com/v2/formz"
        

        for order_line in self.order_line:
            qty = 0
            form_ids = []
            while qty < order_line.product_uom_qty:
                
                payload = json.dumps({
                "name": f"{self.name} {self.partner_id.name} {self.partner_shipping_id.street} {self.partner_shipping_id.city} {self.partner_shipping_id.state_id.name} {self.date_order} Unit -- {qty}",
                "templateId": "5a5ecf1f-67f6-4af7-8d0f-47011d4220b6",
                        "fields": {
                            "Order Number": {
                            "value": self.name,
                            "id": "d20e57e8-c6e2-4e7c-af5c-b943aba5126c",
                            "name": "Order Number",
                            "type": "Number"
                            },
                            "Customer Name": {
                            "value": self.partner_id.name,
                            "id": "a8a19313-34ce-47bc-96cf-3a3297c04c42",
                            "name": "Customer Name",
                            "type": "Database"
                            },
                        "Order Date": {
                            "value": str(self.date_order),
                            "displayValue": str(self.date_order),
                            "id": "654a748e-eccc-4b3c-a8fc-e337234330d6",
                            "name": "Order Date",
                            "type": "Date"
                        },
                        "Address 1": {
                            "text": self.partner_id.street,
                            "id": "7e161cdc-5319-4fdd-988b-df57bcac0e18",
                            "name": "Address 1",
                            "type": "TextBox"
                        },
                        "City State Zip": {
                            "text": self.partner_id.city +" "+ self.partner_id.state_id.name +" "+self.partner_id.zip ,
                            "id": "25c9c51d-3944-49fd-beb0-91af2296c633",
                            "name": "City State Zip",
                            "type": "TextBox"
                        },
                        "Contact Name": {
                            "text": self.partner_id.name,
                            "id": "0a943238-3cd5-4579-a4fe-2dff34faa952",
                            "name": "Contact Name",
                            "type": "TextBox"
                        },
                        "Phone": {
                            "text": self.partner_id.phone,
                            "id": "e1e41e18-071f-40e2-91ee-cdd2180350b8",
                            "name": "Phone",
                            "type": "TextBox"
                        },
                        "Email": {
                            "text": self.partner_id.email,
                            "id": "99e10f42-bf19-458e-a0d2-d0b4ddec81c4",
                            "name": "Email",
                            "type": "TextBox"
                        },
                        "Unit Type": {
                            "text": order_line.product_id.name,
                            "id": "5384c560-aa58-4882-a1b9-eed7b005839a",
                            "name": "Unit Type",
                            "type": "TextBox"
                        },
                        "Site Address": {
                            "text": self.partner_shipping_id.street,
                            "id": "fc631dcf-c180-4453-9891-81f543fa5763",
                            "name": "Site Address",
                            "type": "TextBox"
                        },
                        "Site City State Zip": {
                            "text": self.partner_shipping_id.city +" "+ self.partner_shipping_id.state_id.name +" "+self.partner_shipping_id.zip ,
                            "id": "b88bb464-6acc-43fa-8111-17be737b5f57",
                            "name": "Site City State Zip",
                            "type": "TextBox"
                        },
                        "Site Contact": {
                            "text": self.partner_shipping_id.name,
                            "id": "772b76b8-003f-4b32-9871-81f4274bd8b7",
                            "name": "Site Contact",
                            "type": "TextBox"
                        },
                        "Site Contact Phone": {
                            "text": self.partner_shipping_id.phone,
                            "id": "dffae6d2-1715-43b4-9b0a-bb834368a116",
                            "name": "Site Contact Phone",
                            "type": "TextBox"
                        },
                        "Site Contact Email": {
                            "text": self.partner_shipping_id.email,
                            "id": "86eb89d7-3534-4ca1-9a87-1d59afbb8af2",
                            "name": "Site Contact Email",
                            "type": "TextBox"
                        },
                        },
                    "assignment": {
                    "id": "4f90a5f4-0327-402b-a0e7-5fa4976001aa",
                    "type": "User"
                }
                })
                headers = {
                'accept': 'application/json',
                'content-type': 'application/json',
                'Authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                }
                qty = qty + 1
                response = requests.request("POST", url, headers=headers, data=payload)
                forms_data = response.json()
                form_ids.append(forms_data['id'])
                print(response.text)
            order_line.form_id = ','.join(map(str, form_ids))

        return res


    def action_goformz(self):
        # res = super(SaleOrderGF, self).action_confirm()

        for rec in self:
            pickings = self.env['stock.picking'].sudo().search([('sale_id','=', rec.id)])
        url = "https://api.goformz.com/v2/formz"
        for order_line in self.order_line:
            qty = 0
            form_ids = []
            while qty < order_line.product_uom_qty:
                        payload = json.dumps({
                        "name": f"{self.name} {self.partner_id.name} {self.partner_shipping_id.street} {self.partner_shipping_id.city} {self.partner_shipping_id.state_id.name} {self.date_order} {serial.lot_id.name}",
                        # "name":' {self.name} Creating new one from epi',
                        "templateId": "5a5ecf1f-67f6-4af7-8d0f-47011d4220b6",
                        "fields": {
                            "Order Number": {
                            "value": self.name,
                            "id": "d20e57e8-c6e2-4e7c-af5c-b943aba5126c",
                            "name": "Order Number",
                            "type": "Number"
                            },
                            "Customer Name": {
                            "value": self.partner_id.name,
                            "id": "a8a19313-34ce-47bc-96cf-3a3297c04c42",
                            "name": "Customer Name",
                            "type": "Database"
                            },
                        "Order Date": {
                            "value": str(self.date_order),
                            "displayValue": str(self.date_order),
                            "id": "654a748e-eccc-4b3c-a8fc-e337234330d6",
                            "name": "Order Date",
                            "type": "Date"
                        },
                        "Address 1": {
                            "text": self.partner_id.street,
                            "id": "7e161cdc-5319-4fdd-988b-df57bcac0e18",
                            "name": "Address 1",
                            "type": "TextBox"
                        },
                        "City State Zip": {
                            "text": self.partner_id.city +" "+ self.partner_id.state_id.name +" "+self.partner_id.zip ,
                            "id": "25c9c51d-3944-49fd-beb0-91af2296c633",
                            "name": "City State Zip",
                            "type": "TextBox"
                        },
                        "Contact Name": {
                            "text": self.partner_id.name,
                            "id": "0a943238-3cd5-4579-a4fe-2dff34faa952",
                            "name": "Contact Name",
                            "type": "TextBox"
                        },
                        "Phone": {
                            "text": self.partner_id.phone,
                            "id": "e1e41e18-071f-40e2-91ee-cdd2180350b8",
                            "name": "Phone",
                            "type": "TextBox"
                        },
                        "Email": {
                            "text": self.partner_id.email,
                            "id": "99e10f42-bf19-458e-a0d2-d0b4ddec81c4",
                            "name": "Email",
                            "type": "TextBox"
                        },
                        "Unit Type": {
                            "text": order_line.product_id.name,
                            "id": "5384c560-aa58-4882-a1b9-eed7b005839a",
                            "name": "Unit Type",
                            "type": "TextBox"
                        },
                        "Site Address": {
                            "text": self.partner_shipping_id.street,
                            "id": "fc631dcf-c180-4453-9891-81f543fa5763",
                            "name": "Site Address",
                            "type": "TextBox"
                        },
                        "Site City State Zip": {
                            "text": self.partner_shipping_id.city +" "+ self.partner_shipping_id.state_id.name +" "+self.partner_shipping_id.zip ,
                            "id": "b88bb464-6acc-43fa-8111-17be737b5f57",
                            "name": "Site City State Zip",
                            "type": "TextBox"
                        },
                        "Site Contact": {
                            "text": self.partner_shipping_id.name,
                            "id": "772b76b8-003f-4b32-9871-81f4274bd8b7",
                            "name": "Site Contact",
                            "type": "TextBox"
                        },
                        "Site Contact Phone": {
                            "text": self.partner_shipping_id.phone,
                            "id": "dffae6d2-1715-43b4-9b0a-bb834368a116",
                            "name": "Site Contact Phone",
                            "type": "TextBox"
                        },
                        "Site Contact Email": {
                            "text": self.partner_shipping_id.email,
                            "id": "86eb89d7-3534-4ca1-9a87-1d59afbb8af2",
                            "name": "Site Contact Email",
                            "type": "TextBox"
                        },
                        },
                        "assignment": {
                            "id": "4f90a5f4-0327-402b-a0e7-5fa4976001aa",
                            "type": "User"
                        }
                        })
                        headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'Authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                        }

                        response = requests.request("POST", url, headers=headers, data=payload)
                        forms_data = response.json()
                        # serial.form_id = forms_data['id']

                        print(response.text)
                        print('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')        
        for picking in pickings:
            if picking.state != 'cancel':
                for serial in picking.move_line_ids_without_package:
                    if serial.lot_id:
                        payload = json.dumps({
                        "name": f"{self.name} {self.partner_id.name} {self.partner_shipping_id.street} {self.partner_shipping_id.city} {self.partner_shipping_id.state_id.name} {self.date_order} {serial.lot_id.name}",
                        # "name":' {self.name} Creating new one from epi',
                        "templateId": "5a5ecf1f-67f6-4af7-8d0f-47011d4220b6",
                        "fields": {
                            "Order Number": {
                            "value": self.name,
                            "id": "d20e57e8-c6e2-4e7c-af5c-b943aba5126c",
                            "name": "Order Number",
                            "type": "Number"
                            },
                            "Customer Name": {
                            "value": self.partner_id.name,
                            "id": "a8a19313-34ce-47bc-96cf-3a3297c04c42",
                            "name": "Customer Name",
                            "type": "Database"
                            },
                        "Order Date": {
                            "value": str(self.date_order),
                            "displayValue": str(self.date_order),
                            "id": "654a748e-eccc-4b3c-a8fc-e337234330d6",
                            "name": "Order Date",
                            "type": "Date"
                        },
                        "Address 1": {
                            "text": self.partner_id.street,
                            "id": "7e161cdc-5319-4fdd-988b-df57bcac0e18",
                            "name": "Address 1",
                            "type": "TextBox"
                        },
                        "City State Zip": {
                            "text": self.partner_id.city +" "+ self.partner_id.state_id.name +" "+self.partner_id.zip ,
                            "id": "25c9c51d-3944-49fd-beb0-91af2296c633",
                            "name": "City State Zip",
                            "type": "TextBox"
                        },
                        "Contact Name": {
                            "text": self.partner_id.name,
                            "id": "0a943238-3cd5-4579-a4fe-2dff34faa952",
                            "name": "Contact Name",
                            "type": "TextBox"
                        },
                        "Phone": {
                            "text": self.partner_id.phone,
                            "id": "e1e41e18-071f-40e2-91ee-cdd2180350b8",
                            "name": "Phone",
                            "type": "TextBox"
                        },
                        "Email": {
                            "text": self.partner_id.email,
                            "id": "99e10f42-bf19-458e-a0d2-d0b4ddec81c4",
                            "name": "Email",
                            "type": "TextBox"
                        },
                        "Unit Type": {
                            "text": serial.product_id.name,
                            "id": "5384c560-aa58-4882-a1b9-eed7b005839a",
                            "name": "Unit Type",
                            "type": "TextBox"
                        },
                        "Site Address": {
                            "text": self.partner_shipping_id.street,
                            "id": "fc631dcf-c180-4453-9891-81f543fa5763",
                            "name": "Site Address",
                            "type": "TextBox"
                        },
                        "Site City State Zip": {
                            "text": self.partner_shipping_id.city +" "+ self.partner_shipping_id.state_id.name +" "+self.partner_shipping_id.zip ,
                            "id": "b88bb464-6acc-43fa-8111-17be737b5f57",
                            "name": "Site City State Zip",
                            "type": "TextBox"
                        },
                        "Site Contact": {
                            "text": self.partner_shipping_id.name,
                            "id": "772b76b8-003f-4b32-9871-81f4274bd8b7",
                            "name": "Site Contact",
                            "type": "TextBox"
                        },
                        "Site Contact Phone": {
                            "text": self.partner_shipping_id.phone,
                            "id": "dffae6d2-1715-43b4-9b0a-bb834368a116",
                            "name": "Site Contact Phone",
                            "type": "TextBox"
                        },
                        "Site Contact Email": {
                            "text": self.partner_shipping_id.email,
                            "id": "86eb89d7-3534-4ca1-9a87-1d59afbb8af2",
                            "name": "Site Contact Email",
                            "type": "TextBox"
                        },
                        },
                        "assignment": {
                            "id": "4f90a5f4-0327-402b-a0e7-5fa4976001aa",
                            "type": "User"
                        }
                        })
                        headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'Authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOnRSVUNLNzghIQ=='
                        }

                        response = requests.request("POST", url, headers=headers, data=payload)
                        forms_data = response.json()
                        serial.form_id = forms_data['id']

                        print(response.text)
                        print('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')