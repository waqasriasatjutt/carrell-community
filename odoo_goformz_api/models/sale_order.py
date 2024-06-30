from odoo.fields import Command

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from datetime import datetime
import base64


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



def access_token():

    url = "https://accounts.goformz.com/connect/token"

    payload = 'scope=public_api&grant_type=client_credentials&client_id=5e701457-412d-4eda-9dc0-d69537b2cfd6&client_secret=2e525839-f366-49e2-bc68-1bde6fbfcc74'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token  = response.get("access_token")
    return token



class ResCompany(models.Model):
    _inherit = "res.company"

    template_id = fields.Char("Template ID")
    goform_username = fields.Char("GOFORM Username")
    goform_password = fields.Char("GOFORM Password")




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
                        "templateId": "b570fdfd-030c-467c-b656-f858226c7cfd",
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
                        company = self.env.user.company_id
                        username = company.goform_username
                        password = company.goform_password

                        credentials = f'{username}:{password}'
                        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                        
                        # Prepare the authorization header
                        # headers = {
                        #     'Authorization': f'Basic {encoded_credentials}'
                        # }
                        headers = {
                        'accept': 'application/json',
                        'content-type': 'application/json',
                        'Authorization': f'Basic {encoded_credentials}'
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
        company = self.env.user.company_id
        username = company.goform_username
        password = company.goform_password

        credentials = f'{username}:{password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                        
        headers = {
        'accept': 'application/json',
        'Authorization': f'Basic {encoded_credentials}',
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
                    company = self.env.user.company_id
                    username = company.goform_username
                    password = company.goform_password

                    credentials = f'{username}:{password}'
                    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                                    
                    headers = {
                    'accept': 'application/json',
                    'Authorization': f'Basic {encoded_credentials}',
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
                company = self.env.user.company_id
                username = company.goform_username
                password = company.goform_password

                credentials = f'{username}:{password}'
                encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                                
                headers = {
                'accept': 'application/json',
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'text/plain'
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
                try:
                    unit = forms_data['fields']['Status']['value']
                    if unit:
                        self.goformz_status = unit
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
                        company = self.env.user.company_id
                        username = company.goform_username
                        password = company.goform_password

                        credentials = f'{username}:{password}'
                        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                                        
                        headers = {
                        'accept': 'application/json',
                        'Authorization': f'Basic {encoded_credentials}',
                        'Content-Type': 'text/plain'
                        }

                        response = requests.request("GET", url, headers=headers, data=payload)

                        logging.info(response.text)
                        forms_data = response.json()

                        # Extract form IDs and call another API
                        unit = forms_data['fields']['Unit Number']['value']
                        if unit:
                            lot = self.env['stock.lot'].sudo().search([('name','=', unit),('product_id','=',serial.product_id.id)])
                            serial.lot_id = lot.id




    # def action_confirm(self):
    #     res = super(SaleOrderGF, self).action_confirm()
    #     formatted_date = self.date_order.strftime("%m/%d/%Y")

    #     # Convert to string
    #     formatted_date_string = str(formatted_date)

    #     # res = super(SaleOrderGF, self).action_confirm()
    #     if self.company_id.template_id:
    #         url = "https://api.goformz.com/v2/formz"
    #         # Assuming self.order_line is a list of objects with a 'product_id' attribute
    # # and 'product_uom_qty' attribute
    #         type_unit = ""
    #         # Define a mapping dictionary for product names
    #         # Define a mapping dictionary for product names
    #         name_mapping = {
    #             "Container Dry": "container_dry",
    #             "Trailer": "trailer",
    #             "Reefer Diesel": "reefer_diesel",
    #             "Reefer Electric": "reefer_electric",
    #             "Reefer Container": "container",
    #             "Office": "office",
    #             "Mud Lab": "mudlab",
    #             "Generator": "generator",
    #             "Truck": "truck",
    #             "Other": "other",
    #         }

    #         # Define a dictionary to store quantities for each product
    #         quantities = {
    #             "container_dry": 0,
    #             "trailer": 0,
    #             "reefer_diesel": 0,
    #             "reefer_electric": 0,
    #             "container": 0,
    #             "office": 0,
    #             "mudlab": 0,
    #             "generator": 0,
    #             "truck": 0,
    #             "other": 0,
    #         }

    #         # Loop through order lines and update quantities based on product names
    #         for order_line in self.order_line:
    #             product_name = order_line.product_id.name
    #             type_unit = type_unit + product_name + ", "
    #             if product_name in name_mapping:
    #                 product_key = name_mapping[product_name]
    #                 quantities[product_key] += order_line.product_uom_qty

    #         # Now 'quantities' dictionary contains the updated quantities for each product
    #         # Access the quantities like this:
    #         container_dry_quantity = quantities["container_dry"]
    #         trailer_quantity = quantities["trailer"]
    #         reefer_diesel_quantity = quantities["reefer_diesel"]
    #         reefer_electric_quantity = quantities["reefer_electric"]
    #         container_quantity = quantities["container"]
    #         office_quantity = quantities["office"]
    #         mudlab_quantity = quantities["mudlab"]
    #         generator_quantity = quantities["generator"]
    #         truck_quantity = quantities["truck"]
    #         other_quantity = quantities["other"]

    # # Use these quantities as needed in your code

    #         for order_line in self.order_line:

    #             warehouse = "Not Assigned"
    #             quant = self.env['stock.quant'].sudo().search([('product_id','=', order_line.product_id.id)], limit=1)
    #             if quant:
    #                 warehouse = str(quant.location_id.name)
    #             qty = 0
    #             form_ids = []
    #             input_string = self.name
    #             result = re.search(r'\d+', input_string)
    #             extracted_number = ""
    #             if result:
    #                 extracted_number = result.group()
    #                 print(extracted_number)
    #             else:
    #                 print("No sequence number found.")

    #             while qty < order_line.product_uom_qty:
    #                 # pickings = self.env['stock.picking'].sudo().search([('sale_id','=', rec.id)])

                    
    #                 payload = json.dumps({
    #                 "name": f"{self.name} {self.partner_id.name} {self.partner_shipping_id.street} {self.partner_shipping_id.city} {self.partner_shipping_id.state_id.name} {self.date_order} Unit -- {qty+1}",
    #                 "templateId": self.company_id.template_id,
    #                         "fields": {
    #                         "Yard": {
    #                         "value": self.warehouse_id.name,
    #                         "id": "1d165d7f-2f74-43bf-a352-c908c7799da1",
    #                         "name": "Yard",
    #                         "type": "DropDown",
    #                         },
    #                             "Or Qty Dry Con": {
    #                             "name": "Or Qty Dry Con",
    #                             "value": container_dry_quantity,
    #                             "type": "Number"
    #                             },
    #                             " Or Qty Dry Tr": {
    #                             "name": " Or Qty Dry Tr",
    #                             "value": trailer_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Or Qty Ref Dis": {
    #                             "name": "Or Qty Ref Dis",
    #                             "value": reefer_diesel_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Or Qty Ref Elc Tra": {
    #                             "name": "Or Qty Ref Elc Tra",
    #                             "value": reefer_electric_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Or Qty Ref Con": {
    #                             "name": "Or Qty Ref Con",
    #                             "value": container_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Or Qty Gen": {
    #                             "name": "Or Qty Gen",
    #                             "value": generator_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Or  Qty Mud Lab": {
    #                             "name": "Or  Qty Mud Lab",
    #                             "value": mudlab_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Or Qty Office": {
    #                             "name": "Or Qty Office",
    #                             "value": office_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Other": {
    #                             "name": "Other",
    #                             "value": other_quantity,
    #                             "type": "Number"
    #                             },
    #                             "Order Door": {
    #                                 "id": "0505aafe-d92d-4a1a-a94b-c448c714104d",
    #                                 "name": "Order Door",
    #                                 "value": self.door,
    #                                 "type": "DropDown",
    #                                 "itemCollectionId": "0b450e90-a7d5-45cd-b84e-0e9e08506ee8"
    #                             },
    #                             "Order Plug": {
    #                                 "id": "0505aafe-d92d-4a1a-a94b-c448c714104d",
    #                                 "name": "Order Plug",
    #                                 "value": self.plug,
    #                                 "type": "DropDown",
    #                                 "itemCollectionId": "0b450e90-a7d5-45cd-b84e-0e9e08506ee8"
    #                             },
    #                             "Order Number": {
    #                             "value": self.name,
    #                             "id": "d20e57e8-c6e2-4e7c-af5c-b943aba5126c",
    #                             "name": "Order Number",
    #                             "type": "Number"
    #                             },
    #                             "Contact Name": {
    #                             "value": extracted_number + "-" + str(qty) ,
    #                             "name": "Contact Name",
    #                             "type": "Text"
    #                             },
    #                         "Delivery Note": {
    #                             "value": self.delivery_note ,
    #                             "name": "Delivery Note",
    #                             "type": "Text"
    #                             },

    #                             # "Contract No": {
    #                             # "value": extracted_number + "-" + str(qty) ,
    #                             # "id": "9fd77991-4fbd-4eea-bfdb-a1b0c75f5d2b",
    #                             # "name": "Contract Number",
    #                             # "type": "AutoNumber"
    #                             # },
    #                             "Customer Name": {
    #                             "value": self.partner_id.name,
    #                             "id": "a8a19313-34ce-47bc-96cf-3a3297c04c42",
    #                             "name": "Customer Name",
    #                             "type": "Database"
    #                             },
    #                         "Customer Note": {
    #                             "value": str(self.customer_note),
    #                             "name": "Customer Note",
    #                             "type": "Text"
    #                         },
    #                         "Site Note": {
    #                             "value": str(self.site_note),
    #                             "name": "Site Note",
    #                             "type": "Text"
    #                         },
    #                         "Unit Type": {
    #                             "value": order_line.product_id.name,
    #                             "name": "Unit Type",
    #                             "type": "Text"
    #                         },
    #                         # "Delivery Note": {
    #                         #     "value": str(self.delivery_note),
    #                         #     "name": "Delivery Note",
    #                         #     "type": "Text"
    #                         # },
    #                         # "Min Rental Period": {
    #                         #     "value": str(self.initial_term),
    #                         #     "name": "Min Rental Period",
    #                         #     "type": "Text"
    #                         # },
    #                         "Order Date": {
    #                             "value": str(formatted_date_string),
    #                             "id": "654a748e-eccc-4b3c-a8fc-e337234330d6",
    #                             "name": "Order Date",
    #                             "type": "Date"
    #                         },
    #                         "Address 1": {
    #                             "text": self.partner_id.street,
    #                             "id": "7e161cdc-5319-4fdd-988b-df57bcac0e18",
    #                             "name": "Address 1",
    #                             "type": "TextBox"
    #                         },
    #                         "City State Zip": {
    #                             "text": self.partner_id.city +" "+ self.partner_id.state_id.name +" "+self.partner_id.zip ,
    #                             "id": "25c9c51d-3944-49fd-beb0-91af2296c633",
    #                             "name": "City State Zip",
    #                             "type": "TextBox"
    #                         },
    #                         "Contact Name": {
    #                             "text": self.partner_id.name,
    #                             "id": "0a943238-3cd5-4579-a4fe-2dff34faa952",
    #                             "name": "Contact Name",
    #                             "type": "TextBox"
    #                         },
    #                         "Phone Cust": {
    #                             "text": self.partner_id.phone,
    #                             # "id": "e1e41e18-071f-40e2-91ee-cdd2180350b8",
    #                             "name": "Phone Cust",
    #                             "type": "TextBox"
    #                         },
    #                         "Email Cust": {
    #                             "text": self.partner_id.email,
    #                             # "id": "99e10f42-bf19-458e-a0d2-d0b4ddec81c4",
    #                             "name": "Email Cust",
    #                             "type": "TextBox"
    #                         },
    #                         "Order Type": {
    #                             "value": type_unit,
    #                             "name": "Order Type",
    #                             "type": "DropDown",
    #                         },
    #                         "Site": {
    #                             "text": self.partner_shipping_id.name,
    #                             "name": "Site",
    #                             "type": "TextBox"
    #                         },

    #                         "Site Address": {
    #                             "text": self.partner_shipping_id.street,
    #                             "id": "fc631dcf-c180-4453-9891-81f543fa5763",
    #                             "name": "Site Address",
    #                             "type": "TextBox"
    #                         },
    #                         "Site City State Zip": {
    #                             "text": self.partner_shipping_id.city +" "+ self.partner_shipping_id.state_id.name +" "+self.partner_shipping_id.zip ,
    #                             "id": "b88bb464-6acc-43fa-8111-17be737b5f57",
    #                             "name": "Site City State Zip",
    #                             "type": "TextBox"
    #                         },
    #                         "Site Contact": {
    #                             "text": self.partner_shipping_id.name,
    #                             "id": "772b76b8-003f-4b32-9871-81f4274bd8b7",
    #                             "name": "Site Contact",
    #                             "type": "TextBox"
    #                         },
    #                         "Site Contact Phone": {
    #                             "text": self.partner_shipping_id.phone,
    #                             "id": "dffae6d2-1715-43b4-9b0a-bb834368a116",
    #                             "name": "Site Contact Phone",
    #                             "type": "TextBox"
    #                         },
    #                         "Site Contact Email": {
    #                             "text": self.partner_shipping_id.email,
    #                             "id": "86eb89d7-3534-4ca1-9a87-1d59afbb8af2",
    #                             "name": "Site Contact Email",
    #                             "type": "TextBox"
    #                         },
    #                         },
    #                     "assignment": {
    #                     "id": "4f90a5f4-0327-402b-a0e7-5fa4976001aa",
    #                     "type": "User"
    #                 }
    #                 })
    #                 headers = {
    #                 'accept': 'application/json',
    #                 'content-type': 'application/json',
    #                 'Authorization': 'Basic cmlja0BjYXJyZWxsdHJ1Y2tpbmcuY29tOlRydWNrNzgxMSQ='
    #                 }
    #                 qty = qty + 1
    #                 response = requests.request("POST", url, headers=headers, data=payload)
    #                 logging.info(response.text)
    #                 forms_data = response.json()
    #                 _logger.error(f" response  {response.text}")
    #                 _logger.error(f" tid  {self.company_id.template_id}")

    #                 form_ids.append(forms_data['id'])
    #                 print(response.text)
    #             order_line.form_id = ','.join(map(str, form_ids))

    #     return res


    def action_goformz(self):
        # res = super(SaleOrderGF, self).action_confirm()
        formatted_date = self.date_order.strftime("%m/%d/%Y")

        # Convert to string
        formatted_date_string = str(formatted_date)

        # res = super(SaleOrderGF, self).action_confirm()
        if self.company_id.template_id:
            url = "https://api.goformz.com/v2/formz"
            # Assuming self.order_line is a list of objects with a 'product_id' attribute
    # and 'product_uom_qty' attribute
            type_unit = ""
            # Define a mapping dictionary for product names
            # Define a mapping dictionary for product names
            name_mapping = {
                "Container Dry": "container_dry",
                "Trailer": "trailer",
                "Reefer Diesel": "reefer_diesel",
                "Reefer Electric": "reefer_electric",
                "Reefer Container": "container",
                "Office": "office",
                "Mud Lab": "mudlab",
                "Generator": "generator",
                "Truck": "truck",
                "Other": "other",
            }

            # Define a dictionary to store quantities for each product
            quantities = {
                "container_dry": 0,
                "trailer": 0,
                "reefer_diesel": 0,
                "reefer_electric": 0,
                "container": 0,
                "office": 0,
                "mudlab": 0,
                "generator": 0,
                "truck": 0,
                "other": 0,
            }

            # Loop through order lines and update quantities based on product names
            for order_line in self.order_line:
                product_name = order_line.product_id.name
                type_unit = type_unit + product_name + ", "
                if product_name in name_mapping:
                    product_key = name_mapping[product_name]
                    quantities[product_key] += order_line.product_uom_qty

            # Now 'quantities' dictionary contains the updated quantities for each product
            # Access the quantities like this:
            container_dry_quantity = quantities["container_dry"]
            trailer_quantity = quantities["trailer"]
            reefer_diesel_quantity = quantities["reefer_diesel"]
            reefer_electric_quantity = quantities["reefer_electric"]
            container_quantity = quantities["container"]
            office_quantity = quantities["office"]
            mudlab_quantity = quantities["mudlab"]
            generator_quantity = quantities["generator"]
            truck_quantity = quantities["truck"]
            other_quantity = quantities["other"]

    # Use these quantities as needed in your code

            for order_line in self.order_line:

                warehouse = "Not Assigned"
                quant = self.env['stock.quant'].sudo().search([('product_id','=', order_line.product_id.id)], limit=1)
                if quant:
                    warehouse = str(quant.location_id.name)
                qty = 0
                form_ids = []
                input_string = self.name
                result = re.search(r'\d+', input_string)
                extracted_number = ""
                if result:
                    extracted_number = result.group()
                    print(extracted_number)
                else:
                    print("No sequence number found.")

                while qty < order_line.product_uom_qty:
                    # pickings = self.env['stock.picking'].sudo().search([('sale_id','=', rec.id)])

                    
                    payload = json.dumps({
                    "name": f"{self.name} {self.partner_id.name} {self.partner_shipping_id.street} {self.partner_shipping_id.city} {self.partner_shipping_id.state_id.name} {self.date_order} Unit -- {qty+1}",
                    "templateId": self.company_id.template_id,
                            "fields": {
                            "Yard": {
                            "value": self.warehouse_id.name,
                            "id": "1d165d7f-2f74-43bf-a352-c908c7799da1",
                            "name": "Yard",
                            "type": "DropDown",
                            },
                                "Or Qty Dry Con": {
                                "name": "Or Qty Dry Con",
                                "value": container_dry_quantity,
                                "type": "Number"
                                },
                                " Or Qty Dry Tr": {
                                "name": " Or Qty Dry Tr",
                                "value": trailer_quantity,
                                "type": "Number"
                                },
                                "Or Qty Ref Dis": {
                                "name": "Or Qty Ref Dis",
                                "value": reefer_diesel_quantity,
                                "type": "Number"
                                },
                                "Or Qty Ref Elc Tra": {
                                "name": "Or Qty Ref Elc Tra",
                                "value": reefer_electric_quantity,
                                "type": "Number"
                                },
                                "Or Qty Ref Con": {
                                "name": "Or Qty Ref Con",
                                "value": container_quantity,
                                "type": "Number"
                                },
                                "Or Qty Gen": {
                                "name": "Or Qty Gen",
                                "value": generator_quantity,
                                "type": "Number"
                                },
                                "Or  Qty Mud Lab": {
                                "name": "Or  Qty Mud Lab",
                                "value": mudlab_quantity,
                                "type": "Number"
                                },
                                "Or Qty Office": {
                                "name": "Or Qty Office",
                                "value": office_quantity,
                                "type": "Number"
                                },
                                "Other": {
                                "name": "Other",
                                "value": other_quantity,
                                "type": "Number"
                                },
                                "Order Door": {
                                    "id": "0505aafe-d92d-4a1a-a94b-c448c714104d",
                                    "name": "Order Door",
                                    "value": self.door,
                                    "type": "DropDown",
                                    "itemCollectionId": "0b450e90-a7d5-45cd-b84e-0e9e08506ee8"
                                },
                                "Order Plug": {
                                    "id": "0505aafe-d92d-4a1a-a94b-c448c714104d",
                                    "name": "Order Plug",
                                    "value": self.plug,
                                    "type": "DropDown",
                                    "itemCollectionId": "0b450e90-a7d5-45cd-b84e-0e9e08506ee8"
                                },
                                "Order Number": {
                                "value": self.name,
                                "id": "d20e57e8-c6e2-4e7c-af5c-b943aba5126c",
                                "name": "Order Number",
                                "type": "Number"
                                },
                                "Contact Name": {
                                "value": extracted_number + "-" + str(qty) ,
                                "name": "Contact Name",
                                "type": "Text"
                                },
                            "Delivery Note": {
                                "value": self.delivery_note ,
                                "name": "Delivery Note",
                                "type": "Text"
                                },

                                # "Contract No": {
                                # "value": extracted_number + "-" + str(qty) ,
                                # "id": "9fd77991-4fbd-4eea-bfdb-a1b0c75f5d2b",
                                # "name": "Contract Number",
                                # "type": "AutoNumber"
                                # },
                                "Customer Name": {
                                "value": self.partner_id.name,
                                "id": "a8a19313-34ce-47bc-96cf-3a3297c04c42",
                                "name": "Customer Name",
                                "type": "Database"
                                },
                            "Customer Note": {
                                "value": str(self.customer_note),
                                "name": "Customer Note",
                                "type": "Text"
                            },
                            "Site Note": {
                                "value": str(self.site_note),
                                "name": "Site Note",
                                "type": "Text"
                            },
                            "Unit Type": {
                                "value": order_line.product_id.name,
                                "name": "Unit Type",
                                "type": "Text"
                            },
                            # "Delivery Note": {
                            #     "value": str(self.delivery_note),
                            #     "name": "Delivery Note",
                            #     "type": "Text"
                            # },
                            # "Min Rental Period": {
                            #     "value": str(self.initial_term),
                            #     "name": "Min Rental Period",
                            #     "type": "Text"
                            # },
                            "Order Date": {
                                "value": str(formatted_date_string),
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
                                "text": str(self.partner_id.city) +" "+ str(self.partner_id.state_id.name) +" "+str(self.partner_id.zip) ,
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
                            "Phone Cust": {
                                "text": self.partner_id.phone,
                                # "id": "e1e41e18-071f-40e2-91ee-cdd2180350b8",
                                "name": "Phone Cust",
                                "type": "TextBox"
                            },
                            "Email Cust": {
                                "text": self.partner_id.email,
                                # "id": "99e10f42-bf19-458e-a0d2-d0b4ddec81c4",
                                "name": "Email Cust",
                                "type": "TextBox"
                            },
                            "Order Type": {
                                "value": type_unit,
                                "name": "Order Type",
                                "type": "DropDown",
                            },
                            "Site": {
                                "value": self.partner_shipping_id.name,
                                "name": "Site",
                                "type": "Database"
                            },
                            "Del Number ": {
                                "text": "DEL-"+str(self.id)+"-"+str(qty+1),
                                "name": "Del Number ",
                                "type": "TextBox"
                            },

                            "Site Address": {
                                "text": self.partner_shipping_id.street,
                                "id": "fc631dcf-c180-4453-9891-81f543fa5763",
                                "name": "Site Address",
                                "type": "TextBox"
                            },
                            "Site City State Zip": {
                                "text": str(self.partner_shipping_id.city) +" "+ str(self.partner_shipping_id.state_id.name) +" "+str(self.partner_shipping_id.zip) ,
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
                            "Pics": {
                            "value": self.partner_shipping_id.number_of_pics,
                            "name": "Pics",
                            "type": "Number"
                            },
                            "Order Plug": {
                                "value": self.partner_shipping_id.plug,
                                "name": "Order Plug",
                                "type": "Drop Down"
                            },
                            "Site Contact Email": {
                                "text": self.partner_shipping_id.site_email,
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
                    company = self.env.user.company_id
                    username = company.goform_username
                    password = company.goform_password

                    credentials = f'{username}:{password}'
                    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                    
                    # Prepare the authorization header
                    # headers = {
                    #     'Authorization': f'Basic {encoded_credentials}'
                    # }
                    headers = {
                    'accept': 'application/json',
                    'content-type': 'application/json',
                    'Authorization': f'Basic {encoded_credentials}'
                    }
                    qty = qty + 1
                    response = requests.request("POST", url, headers=headers, data=payload)
                    logging.info('response.text-------------------------------')
                    logging.info(response.text)
                    forms_data = response.json()
                    _logger.error(f" response  {response.text}")
                    _logger.error(f" tid  {self.company_id.template_id}")

                    form_ids.append(forms_data['id'])
                    print(response.text)
                order_line.form_id = ','.join(map(str, form_ids))

