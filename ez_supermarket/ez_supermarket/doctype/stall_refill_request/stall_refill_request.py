# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate, get_time, get_datetime, today

class StallRefillRequest(Document):
	pass

@frappe.whitelist()
def set_timestamps(doc_str):
    # Parse the input JSON string into a dict
    doc = frappe.parse_json(doc_str)
    now = frappe.utils.now_datetime()

    # Check for the most recent submitted doc (docstatus = 1)
    existing_doc = frappe.get_all(
        "Stall Refill Request",
        filters={
            "docstatus": 1,
        },
        fields=["name", "timestamp"],
        order_by="creation desc",
        limit=1,
        as_list=False
    )

    if existing_doc:
        # If previous doc exists: use its timestamp as the new doc's last_fetch_timestamp
        updated_doc = frappe.get_doc(doc)
        updated_doc.last_fetch_timestamp = existing_doc[0].timestamp
        updated_doc.timestamp = now
        return updated_doc
    else:
        # First doc: set last_fetch_timestamp as posting_date + 00:00:00
        updated_doc = frappe.get_doc(doc)
        updated_doc.timestamp = now
        updated_doc.last_fetch_timestamp = f"{updated_doc.posting_date} 00:00:00"
        return updated_doc

@frappe.whitelist()
def fetch_items_sold(timestamp, last_fetch_ts=None):
    data = [] # Define as list

    if last_fetch_ts:
        invoices = frappe.db.sql("""
            SELECT sii.item_code, sii.qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE CONCAT(si.posting_date, ' ', si.posting_time) BETWEEN %s AND %s
            AND si.docstatus = 1
        """, (last_fetch_ts, timestamp), as_dict=1)
    else:
        start_time = frappe.utils.nowdate() + " 00:00:00"
        invoices = frappe.db.sql("""
            SELECT sii.item_code, sii.qty
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE CONCAT(si.posting_date, ' ', si.posting_time) BETWEEN %s AND %s
            AND si.docstatus = 1
        """, (start_time, timestamp), as_dict=1)

    items_sold = {}

    for d in invoices:
        item_code = d.item_code
        if item_code not in items_sold:
            items_sold[item_code] = {"qty": 0}
        items_sold[item_code]["qty"] += d.qty

    for item_code, item_data in items_sold.items():
        item = frappe.get_doc("Item", item_code)
        item_data["item_code"] = item_code
        item_data["stock_uom"] = item.stock_uom
        item_data["item_name"] = item.item_name
        item_data["qty_sold"] = items_sold[item_code]["qty"]
        item_data["stall_location"] = item.custom_default_stall_location
        item_data["store_location"] = item.custom_default_store_location
        item_data["max_qty"] = item.custom_max_qty
        item_data["store_warehouse"] = item.custom_default_store_warehouse
        item_data["stall_warehouse"] = item.custom_default_stall_warehouse

        data.append(item_data)  # Append to list

    return data


# @frappe.whitelist()
# def create_item_transfer_to_stall(stall_request):
#     stall_request = frappe.get_doc("Stall Refill Request", stall_request)
#     if stall_request.docstatus != 1:
#         raise Exception("Document is not saved")

#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.stock_entry_type = "Item Transfer to Stall"
#     stock_entry.posting_date = stall_request.posting_date
#     stock_entry.posting_time = stall_request.posting_time
#     # stock_entry.company = stall_request.company
#     # stock_entry.from_warehouse = stall_request.store_warehouse
#     # stock_entry.to_warehouse = stall_request.custom_default_stall_warehouse

#     for item in stall_request.stall_request_details:
#         item_doc = frappe.get_doc("Item", item.item_code)
#         valuation_rate = item_doc.valuation_rate if item_doc.valuation_rate is not None and item_doc.valuation_rate != 0 else 1
        
#         # Adjust the quantity in the Serial and Batch Bundle
#         # bundle = frappe.get_doc("Serial and Batch Bundle", item.serial_and_batch_bundle)
#         # bundle.qty -= item.qty_sold
#         # bundle.save()
        
#         stock_entry.append("items", {
#             "item_code": item.item_code,
#             "qty": item.qty_sold,
#             "s_warehouse": item_doc.custom_default_store_warehouse,
#             "t_warehouse": item_doc.custom_default_stall_warehouse,
#             "valuation rate": valuation_rate,
#             "allow_zero_valuation_rate" : "1"
#         })

#     stock_entry.insert()
#     # stock_entry.submit()

#     return stock_entry.name


# @frappe.whitelist()
# def create_item_transfer_to_stall(stall_request):
#     stall_request = frappe.get_doc("Stall Refill Request", stall_request)
#     if stall_request.docstatus != 1:
#         raise Exception("Document is not saved")

#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.stock_entry_type = "Material Transfer"
#     stock_entry.posting_date = stall_request.posting_date
#     stock_entry.posting_time = stall_request.posting_time

#     for item in stall_request.stall_request_details:
#         item_doc = frappe.get_doc("Item", item.item_code)
#         valuation_rate = item_doc.valuation_rate if item_doc.valuation_rate is not None and item_doc.valuation_rate != 0 else 1

#         stock_entry.append("items", {
#             "item_code": item.item_code,
#             "qty": item.qty_sold,
#             "s_warehouse": item.store_warehouse,
#             "t_warehouse": "Stall - PTPS",
#             "valuation rate": valuation_rate
#         })

#     stock_entry.insert()

#     # Get the URL of the newly created Stock Entry page
#     stock_entry_url = frappe.utils.get_url_to_form("Stock Entry", stock_entry.name)

#     return stock_entry_url