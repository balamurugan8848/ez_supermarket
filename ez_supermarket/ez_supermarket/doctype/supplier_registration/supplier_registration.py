# Copyright (c) 2024, Balamurugan and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document
import india_compliance.gst_india.utils
from india_compliance.gst_india.utils import guess_gst_category, is_api_enabled
from india_compliance.gst_india.utils import guess_gst_category



class SupplierRegistration(Document):
    @frappe.whitelist()
    def gstin_validation(self):
        gstin = self.gstin
        
        if gstin and len(gstin) >=2:
            state_code = gstin[:2]
            state_mapping = STATE_CODES
            
            state = state_mapping.get(state_code)
            self.state = state
            self.country = 'India'


STATE_CODES = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarkhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Orissa",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman & Diu",
    "26": "Dadra and Nagar Haveli and Daman and Diu",
    "27": "Maharashtra",
    "28": "Andhra Pradesh (Old)",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Pondicherry",
    "35": "Andaman & Nicobar Islands",
    "36": "Telengana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
    "97": "Other Territory",
    "99": "Other Territory",
}

@frappe.whitelist()
def validate_pan(pan):
    if len(pan) != 10:
        return False
    if not pan[:5].isalpha():
        return False
    if not pan[5:9].isdigit():
        return False
    if not pan[9].isalpha():
        return False
    return True

@frappe.whitelist()
def valid_state_code(code):
  if code in STATE_CODES:
    return True
  
  return False

@frappe.whitelist()  
def validate_gstin(gstin, pan):

    # GSTIN format regex check
    if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gstin):
        return {
            'valid': False,
            'message': 'Invalid GSTIN format'
        }

    # Extract PAN from GSTIN
    gstin_pan = gstin[2:12]

    # Compare PANs
    if pan != gstin_pan:
        return {
            'valid': False,
            'message': 'PAN mismatch in GSTIN'
        }

    # Validate state code
    state_code = gstin[0:2]
    if not valid_state_code(state_code):
        return {
            'valid': False,
            'message': 'Invalid state code in GSTIN'
        }
    existing_supplier = frappe.db.exists("Supplier", {"gstin": gstin})
    if existing_supplier: 
        return {
        "valid": False,
        "message": "GSTIN already linked to existing Supplier"
        }
    existing_address = frappe.db.exists("Address", {"gstin": gstin})
    if existing_address:
        return {
        "valid": False, 
        "message": "GSTIN already linked to existing Address" 
        }

    return {'valid': True}



@frappe.whitelist()
def create_supplier_from_registration(supplier_registration):
    supplier_registration = frappe.get_doc("Supplier Registration", supplier_registration)

    # Create a new Supplier document
    supplier = frappe.new_doc("Supplier")
    if supplier_registration.are_you_an_av_unit == "Yes":
        supplier.supplier_name = supplier_registration.av_unit_name
    else:
        supplier.supplier_name = supplier_registration.name_of_vendor

    supplier.supplier_group = "All Supplier Groups"
    supplier.supplier_type = "Company"
    supplier.country = supplier_registration.country
    supplier.gstin = supplier_registration.gstin
    supplier.pan = supplier_registration.pan
    supplier.revenue_growth = supplier_registration.revenue_growth_rate
    supplier.liquidity_ratio = supplier_registration.liquidity_ratio
    supplier.debt_to_equity_ratio = supplier_registration.debt_to_equity_ratio
    supplier.credit_worthiness = supplier_registration.creditworthiness
    supplier.profitability = supplier_registration.profitability_net_profit_margin 
    supplier.gst_category = guess_gst_category(supplier_registration.gstin, supplier_registration.country)
    

    # Save the Supplier document
    supplier.insert()
    
        # Create a new Address document
    address = frappe.new_doc("Address")
    if supplier_registration.are_you_an_av_unit == "Yes":
        address.address_title = supplier_registration.av_unit_name
    else:
        address.address_title = supplier_registration.name_of_vendor
    address.address_line1 = supplier_registration.address_line_1
    address.address_line2 = supplier_registration.address_line_2
    address.city = supplier_registration.city
    address.state = supplier_registration.state
    address.country = supplier_registration.country
    address.pincode = supplier_registration.postal_code
    address.gstin = supplier_registration.gstin
    address.gst_category = supplier.gst_category

    # Link the Address document to the Supplier document
    address.append("links", {
        "link_doctype": "Supplier",
        "link_name": supplier.name
    
        })

    address.insert()

    contact = frappe.new_doc("Contact")
    contact.first_name = supplier_registration.contact_name

    # Add a row to the email_ids child table
    contact.append("email_ids", {
        "email_id": supplier_registration.email_id,
        "is_primary": 1
    })

    # Add a row to the phone_nos child table
    contact.append("phone_nos", {
        "phone": supplier_registration.phone,
        "is_primary_phone": 1
    })

    # Link the Contact document to the Supplier document
    contact.append("links", {
        "link_doctype": "Supplier",
        "link_name": supplier.name
    })

    contact.insert()
    
    supplier.save()
    
    user = frappe.new_doc('User')
    user.email = supplier_registration.email_id
    user.first_name = supplier_registration.contact_name
    user.send_welcome_email = 1
    user.save()

    # Assign the Supplier role to the new user
    user.add_roles('Supplier')

    # Save the changes to the user document
    user.save()
