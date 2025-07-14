# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate
from frappe import _

class StockAdjust(Document):
	pass

@frappe.whitelist()
def create_stock_reconciliation(stock_adjust):
    stock_adjust_doc = frappe.get_doc("Stock Adjust", stock_adjust)
    
    stock_reconciliation = frappe.new_doc("Stock Reconciliation")
    
    stock_reconciliation.posting_time = 1
    stock_reconciliation.posting_date = stock_adjust_doc.posting_date
    stock_reconciliation.posting_time = stock_adjust_doc.posting_time
    stock_reconciliation.custom_reason = stock_adjust_doc.reason
    # stock_reconciliation.expense_account = "Stock Adjustment - PTPS"
    stock_reconciliation.purpose = "Stock Reconciliation"
    stock_reconciliation.custom_document_type = "Stock Adjust"
    stock_reconciliation.custom_reference_document = stock_adjust_doc.name
    
    for item in stock_adjust_doc.items:
        stock_reconciliation.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "valuation_rate": item.valuation_rate,
            "warehouse": item.t_warehouse,
            # "batch_no": item.batch_no,
        })
    
    stock_reconciliation.insert()
    stock_reconciliation.submit()
    
    msg = f"Stock Reconciliation <b>{stock_reconciliation.name}</b> has been created successfully!!!"
    link = f"<b><a href='/app/stock-reconciliation/{stock_reconciliation.name}'>{stock_reconciliation.name}</a></b>"
    full_msg = _(msg + ". " + link)
    frappe.msgprint(full_msg)
    
    return stock_adjust

@frappe.whitelist()
def on_submit(doc, method):
    create_stock_reconciliation(doc.name)

  
  


@frappe.whitelist()
def get_item_details_barcode(barcode):

  # Get item from Item Barcode table
  item_barcode = frappe.get_doc("Item Barcode", {"parent": ["!=", ""], "barcode": barcode})
  if not item_barcode:
    frappe.throw("Item not found for barcode {}".format(barcode))

  # Get item details 
  item_code = item_barcode.parent
  item_doc = frappe.get_doc("Item", item_code)
  if not item_doc:
    frappe.throw("Invalid item code {}".format(item_code))

  last_purchase_rate = item_doc.last_purchase_rate
  gst_hsn_code = item_doc.gst_hsn_code
  shelf_life_in_days = item_doc.shelf_life_in_days

  # Extract rate or set default
  if not last_purchase_rate: 
      last_purchase_rate = 0

  return {
    "item_code": item_doc.name,
    "custom_article_code": item_doc.custom_article_code,
    "item_name": item_doc.item_name,
    "item_group": item_doc.item_group,  
    "Valuation_rate": item_doc.valuation_rate,
    "gst_hsn_code": gst_hsn_code,
    "shelf_life_in_days": shelf_life_in_days,
    "uom": item_doc.stock_uom,
    "has_batch_no": item_doc.has_batch_no,
    "create_new_batch": item_doc.create_new_batch,
  }
  
@frappe.whitelist()
def get_item_details(item_code):
  item = frappe.get_doc("Item", item_code)
  if item:
    return {
      "item_name": item.item_name,
      "custom_article_code": item.custom_article_code,
      "valuation_rate": item.valuation_rate,
      "uom": item.stock_uom,
      "item_group": item.item_group,
      "rate": item.valuation_rate,
      "shelf_life_in_days": item.shelf_life_in_days,
      "has_batch_no": item.has_batch_no,
      "create_new_batch": item.create_new_batch,
      "gst_hsn_code": item.gst_hsn_code,
    }
  else:
    return {}

@frappe.whitelist()
def get_item_basic_rate(item_code):

  basic_rate = 0
  
  item = frappe.get_doc("Item", item_code)

  if item.standard_rate:
    basic_rate = item.standard_rate

  else:
    price_list_rate = frappe.db.get_value("Item Price", 
      {"item_code": item_code, "buying": 1}, "price_list_rate")
    
    if price_list_rate:
      basic_rate = price_list_rate

  return {"basic_rate": basic_rate}



# @frappe.whitelist()
# def get_available_qty(item_code, warehouse):

#   batch_details = frappe.db.sql("""
#     select name, sum(actual_qty) as qty
#     from `tabBin`
#     where item_code=%s and warehouse=%s
#     group by name
#   """, (item_code, warehouse), as_dict=1)

#   available_qty = sum(batch.qty for batch in batch_details)

#   return {
#     "available_qty": available_qty, 
#     "batches": len(batch_details)
#   }
  

# @frappe.whitelist()
# def get_available_qty(item_code, warehouse, batch_no=None):
#     frappe.logger().info(f"Function get_available_qty called with item_code={item_code}, warehouse={warehouse}, batch_no={batch_no}")

#     if batch_no:
#         # Get available qty for items with a specific batch number
#         sql_query = """
#             select sum(actual_qty) as qty
#             from `tabStock Ledger Entry`
#             where item_code=%s 
#             and warehouse=%s
#             and batch_no=%s 
#         """
#         available_qty = frappe.db.sql(sql_query, (item_code, warehouse, batch_no))

#         frappe.logger().info(f"SQL Query Executed: {sql_query}")
#         frappe.logger().info(f"SQL Result: {frappe.as_json(available_qty)}")

#         if available_qty and available_qty[0][0]:
#             return {"available_qty": available_qty[0][0]}
#         else:
#             frappe.logger().error("No stock ledger entry found for the specified item, warehouse, and batch number")
#             frappe.throw("No stock ledger entry found for the specified item, warehouse, and batch number")

#     frappe.logger().error("No batch number provided")

@frappe.whitelist()
def get_available_qty(warehouse, item_code):

  item_details = frappe.db.sql("""
    SELECT item_code, warehouse, actual_qty 
    FROM tabBin
    WHERE item_code=%s AND warehouse=%s
  """, (item_code, warehouse), as_dict=1)

  if item_details: 
    return item_details[0].actual_qty
  else:
    return 0
  
@frappe.whitelist() 
def get_batch_available_qty(warehouse, item_code, batch_no):

  sle = frappe.db.sql("""
    SELECT sum(actual_qty) as qty
    FROM `tabStock Ledger Entry`
    WHERE item_code=%s AND warehouse=%s AND batch_no=%s 
  """, (item_code, warehouse, batch_no), as_dict=1)

  return sle[0].qty if sle else 0