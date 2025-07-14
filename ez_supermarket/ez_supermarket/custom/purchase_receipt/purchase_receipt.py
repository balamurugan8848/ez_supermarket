# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe import get_doc
from frappe.model.document import Document
from frappe.utils import nowdate
import json
from datetime import datetime


class PurchaseReceipt(Document):
	pass

def update_item_prices(doc, method):
    for item in doc.items:
        # Get the batch_id from Batch with reference to Purchase Receipt and name
        batch_id = frappe.get_value("Batch", {"reference_doctype": doc.doctype, "reference_name": doc.name}, "batch_id")

        # If batch_id is not empty, proceed to create a new Item Price
        if batch_id:
            # Create a new Item Price entry
            new_item_price = frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item.item_code,
                "price_list": "Standard Selling",  # Use the selling price list
                "price_list_rate": item.custom_selling_price,  # You may adjust this based on your requirements
                "batch_no": batch_id
            })

            new_item_price.insert()

def update_batch_expiry_after_submit(doc, method):
  if doc.doctype == "Purchase Receipt" and doc.docstatus == 1:
    # Get all items 
    items = doc.items
    
    for item in items:
      # Get custom_expiry_date for this item
      expiry_date = item.custom_expiry_date
      
      # Find batches for this item
      batches = frappe.get_list("Batch", {"item": item.item_code, "reference_name": doc.name})
      
      for batch in batches:
        # Update expiry date
        frappe.db.set_value("Batch", batch.name, "expiry_date", expiry_date)
        

@frappe.whitelist()
def update_item_lead_time(pr_name):
    pr = frappe.get_doc("Purchase Receipt", pr_name)
    if not pr:
        return "Purchase Receipt not found"

    for item in pr.items:
        po_date = None
        if item.purchase_order:
            po = frappe.get_doc("Purchase Order", item.purchase_order)
            if po:
                po_date = po.transaction_date

        if not po_date:
            # Fetch custom purchase order date from the Purchase Receipt main doctype
            po_date = pr.custom_purchase_order_date

        if not po_date: 
            continue

        lead_time_days = (pr.posting_date - po_date).days

        if lead_time_days > 0:
            frappe.db.set_value('Item', item.item_code, 'lead_time_days', lead_time_days)

    return "Lead Times Updated"


def on_submit(doc, method):
    update_batch_expiry_after_submit(doc, method)
    update_item_prices(doc, method)
    # update_item_lead_time(doc, method)
    

@frappe.whitelist()
def fetch_item_details(item_code, set_warehouse=None, warehouse=None):
    warehouse = set_warehouse or warehouse  # Use set_warehouse from parent if provided, otherwise use warehouse from child table

    if warehouse:
        item = frappe.get_doc("Item", item_code)
        if not item:
            return {}

        if item.custom_default_store_warehouse == warehouse:
            return {
                "warehouse": warehouse,
                "item_location": item.custom_default_store_location,
                # "custom_mrp": item.custom_mrp
            }
        elif item.custom_default_stall_warehouse == warehouse:
            return {
                "warehouse": warehouse,
                "item_location": item.custom_default_stall_location,
                # "custom_mrp": item.custom_mrp
            }

    return {}


def update_item_fields(doc, method):
    if doc.items:
        for item in doc.items:
            if item.custom_mrp:
                frappe.db.set_value('Item', item.item_code, 'custom_mrp', item.custom_mrp)
            if item.rate:
                frappe.db.set_value('Item', item.item_code, 'valuation_rate', item.custom_mrp)

                

