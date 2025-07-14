# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.utils import flt
from frappe import _

# OG Code
# def get_qty_sold_and_purchased_last_two_months(item_code):
#     # Get the first and last day of the current month
#     today = datetime.today()
#     first_day_of_current_month = datetime(today.year, today.month, 1)
#     last_day_of_current_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

#     # Make sure the dates cover the entire day
#     first_day_of_current_month = first_day_of_current_month.replace(hour=0, minute=0, second=0, microsecond=0)
#     last_day_of_current_month = last_day_of_current_month.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Get the first and last day of the last month
#     last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
#     first_day_of_last_month = last_day_of_last_month.replace(day=1)

#     # Get the first and last day of the month before the last month
#     last_day_of_month_before_last = first_day_of_last_month - timedelta(days=1)
#     first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)

#     # Query Sales Invoices for the given item within the last two months
#     qty_sold_last_month = frappe.db.sql("""
#         SELECT SUM(sii.qty) as total_qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_last_month, last_day_of_last_month), as_dict=True)[0].get('total_qty') or 0

#     qty_sold_previous_month = frappe.db.sql("""
#         SELECT SUM(sii.qty) as total_qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_month_before_last, last_day_of_month_before_last), as_dict=True)[0].get('total_qty') or 0

#     # Query Sales Invoices for the given item within the current month
#     qty_sold_current_month = frappe.db.sql("""
#         SELECT SUM(sii.qty) as total_qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_current_month, last_day_of_current_month), as_dict=True)[0].get('total_qty') or 0

#     # Query Purchase Invoices for the given item within the last two months
#     qty_purchased_last_month = frappe.db.sql("""
#         SELECT SUM(pii.qty) as total_qty
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_last_month, last_day_of_last_month), as_dict=True)[0].get('total_qty') or 0

#     qty_purchased_previous_month = frappe.db.sql("""
#         SELECT SUM(pii.qty) as total_qty
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_month_before_last, last_day_of_month_before_last), as_dict=True)[0].get('total_qty') or 0

#     # Query Purchase Invoices for the given item within the current month
#     qty_purchased_current_month = frappe.db.sql("""
#         SELECT SUM(pii.qty) as total_qty
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_current_month, last_day_of_current_month), as_dict=True)[0].get('total_qty') or 0

#     return qty_sold_last_month, qty_sold_previous_month, qty_sold_current_month, qty_purchased_last_month, qty_purchased_previous_month, qty_purchased_current_month


# OG Code
# @frappe.whitelist()
# def fetch_supplier_items(supplier):
#     items = []
    
#     item_defaults = frappe.get_all("Item Default", 
#         filters={
#             "default_supplier": supplier
#         },
#         fields=["parent"]
#     )
    
#     for row in item_defaults:
#         item_code = row.parent
#         item = frappe.get_doc("Item", item_code)
        
#         # Fetch current balance of the item
#         # available_qty = get_item_current_balance(item_code)
        
#         stall_qty, store_rooms_qty = get_item_current_balance(item_code)
        
#         last_month_sales, previous_last_month_sales, current_month_sales, last_month_purchase, previous_last_month_purchase, current_month_purchase = get_qty_sold_and_purchased_last_two_months(item_code)
        
#         # if item.last_purchase_rate == 0:
#         #     last_purchase_rate = get_last_purchase_rate_from_item_price(item_code)
#         # else:
#         #     last_purchase_rate = item.last_purchase_rate
                                                            
#         items.append({
#             "item_code": item_code,
#             "item_name": item.item_name,
#             # "description": item.description,
#             "uom": item.stock_uom,
#             # "last_purchase_rate": last_purchase_rate,
#             # "item_tax_template": get_item_tax_template(item),
#             # "buying_price_list": "Standard Buying",
#             # "custom_available_qty": available_qty,
#             "custom_available_qty": f"{stall_qty} / {store_rooms_qty}",
#             "custom_last_month_sales": last_month_sales,
#             "custom_previous_last_month_sales": previous_last_month_sales,
#             "custom_current_month_sales_2": current_month_sales,
#             "custom_last_month_purchase": last_month_purchase,
#             "custom_previous_last_month_purchase": previous_last_month_purchase,
#             "custom_current_month_purchase": current_month_purchase,
#             "custom_tax": item.custom_tax_rate,
#             "custom_mrp": item.custom_mrp,
#         })
        
#     return items

# def get_purchase_price_last_two_months(item_code):
#     # Get the first and last day of the current month
#     today = datetime.today()
#     first_day_of_current_month = datetime(today.year, today.month, 1)
#     last_day_of_current_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

#     # Make sure the dates cover the entire day
#     first_day_of_current_month = first_day_of_current_month.replace(hour=0, minute=0, second=0, microsecond=0)
#     last_day_of_current_month = last_day_of_current_month.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Get the first and last day of the last month
#     last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
#     first_day_of_last_month = last_day_of_last_month.replace(day=1)

#     # Get the first and last day of the month before the last month
#     last_day_of_month_before_last = first_day_of_last_month - timedelta(days=1)
#     first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)

#     # Query Purchase Invoices for the given item within the last two months
#     purchase_price_last_month = frappe.db.sql("""
#         SELECT AVG(pii.rate) as avg_rate
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_last_month, last_day_of_last_month), as_dict=True)[0].get('avg_rate') or 0

#     purchase_price_previous_month = frappe.db.sql("""
#         SELECT AVG(pii.rate) as avg_rate
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_month_before_last, last_day_of_month_before_last), as_dict=True)[0].get('avg_rate') or 0

#     # Query Purchase Invoices for the given item within the current month
#     purchase_price_current_month = frappe.db.sql("""
#         SELECT AVG(pii.rate) as avg_rate
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_current_month, last_day_of_current_month), as_dict=True)[0].get('avg_rate') or 0

#     return purchase_price_last_month, purchase_price_previous_month, purchase_price_current_month

# def get_sales_price_last_two_months(item_code):
#     # Get the first and last day of the current month
#     today = datetime.today()
#     first_day_of_current_month = datetime(today.year, today.month, 1)
#     last_day_of_current_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

#     # Make sure the dates cover the entire day
#     first_day_of_current_month = first_day_of_current_month.replace(hour=0, minute=0, second=0, microsecond=0)
#     last_day_of_current_month = last_day_of_current_month.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Get the first and last day of the last month
#     last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
#     first_day_of_last_month = last_day_of_last_month.replace(day=1)

#     # Get the first and last day of the month before the last month
#     last_day_of_month_before_last = first_day_of_last_month - timedelta(days=1)
#     first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)

#     # Query Sales Invoices for the given item within the last two months
#     sales_price_last_month = frappe.db.sql("""
#         SELECT AVG(sii.rate) as avg_rate
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_last_month, last_day_of_last_month), as_dict=True)[0].get('avg_rate') or 0

#     sales_price_previous_month = frappe.db.sql("""
#         SELECT AVG(sii.rate) as avg_rate
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_month_before_last, last_day_of_month_before_last), as_dict=True)[0].get('avg_rate') or 0

#     # Query Sales Invoices for the given item within the current month
#     sales_price_current_month = frappe.db.sql("""
#         SELECT AVG(sii.rate) as avg_rate
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_current_month, last_day_of_current_month), as_dict=True)[0].get('avg_rate') or 0

#     return sales_price_last_month, sales_price_previous_month, sales_price_current_month


# # Trial
# def get_qty_sold_and_purchased_last_two_months(item_code):
#     # Get the first and last day of the current month
#     today = datetime.today()
#     first_day_of_current_month = datetime(today.year, today.month, 1)
#     last_day_of_current_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

#     # Make sure the dates cover the entire day
#     first_day_of_current_month = first_day_of_current_month.replace(hour=0, minute=0, second=0, microsecond=0)
#     last_day_of_current_month = last_day_of_current_month.replace(hour=23, minute=59, second=59, microsecond=999999)

#     # Get the first and last day of the last month
#     last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
#     first_day_of_last_month = last_day_of_last_month.replace(day=1)

#     # Get the first and last day of the month before the last month
#     last_day_of_month_before_last = first_day_of_last_month - timedelta(days=1)
#     first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)

#     # Query Sales Invoices for the given item within the last two months
#     qty_sold_last_month = frappe.db.sql("""
#         SELECT SUM(sii.qty) as total_qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_last_month, last_day_of_last_month), as_dict=True)[0].get('total_qty') or 0

#     qty_sold_previous_month = frappe.db.sql("""
#         SELECT SUM(sii.qty) as total_qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_month_before_last, last_day_of_month_before_last), as_dict=True)[0].get('total_qty') or 0

#     # Query Sales Invoices for the given item within the current month
#     qty_sold_current_month = frappe.db.sql("""
#         SELECT SUM(sii.qty) as total_qty
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
#         WHERE sii.item_code = %s
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.docstatus = 1
#     """, (item_code, first_day_of_current_month, last_day_of_current_month), as_dict=True)[0].get('total_qty') or 0

#     # Query Purchase Invoices for the given item within the last two months
#     qty_purchased_last_month = frappe.db.sql("""
#         SELECT SUM(pii.qty) as total_qty
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_last_month, last_day_of_last_month), as_dict=True)[0].get('total_qty') or 0

#     qty_purchased_previous_month = frappe.db.sql("""
#         SELECT SUM(pii.qty) as total_qty
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_month_before_last, last_day_of_month_before_last), as_dict=True)[0].get('total_qty') or 0

#     # Query Purchase Invoices for the given item within the current month
#     qty_purchased_current_month = frappe.db.sql("""
#         SELECT SUM(pii.qty) as total_qty
#         FROM `tabPurchase Invoice` pi
#         JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
#         WHERE pii.item_code = %s
#             AND pi.posting_date BETWEEN %s AND %s
#             AND pi.docstatus = 1
#     """, (item_code, first_day_of_current_month, last_day_of_current_month), as_dict=True)[0].get('total_qty') or 0

#     return qty_sold_last_month, qty_sold_previous_month, qty_sold_current_month, qty_purchased_last_month, qty_purchased_previous_month, qty_purchased_current_month


# Trial
# @frappe.whitelist()
# def fetch_supplier_items(supplier):
#     items = []
    
#     item_defaults = frappe.get_all("Item Default", 
#         filters={
#             "default_supplier": supplier
#         },
#         fields=["parent"]
#     )
    
#     for row in item_defaults:
#         item_code = row.parent
#         item = frappe.get_doc("Item", item_code)
        
#         # Fetch current balance of the item
#         stall_qty, store_rooms_qty = get_item_current_balance(item_code)
        
#         # Fetch sales and purchases for the last two months
#         last_month_sales, previous_last_month_sales, current_month_sales, last_month_purchase, previous_last_month_purchase, current_month_purchase = get_qty_sold_and_purchased_last_two_months(item_code)
        
#         # Fetch sales prices for the last two months
#         last_month_sales_price, previous_last_month_sales_price, current_month_sales_price = get_sales_price_last_two_months(item_code)
        
#         # Fetch purchase prices for the last two months
#         last_month_purchase_price, previous_last_month_purchase_price, current_month_purchase_price = get_purchase_price_last_two_months(item_code)
        
#         items.append({
#             "item_code": item_code,
#             "item_name": item.item_name,
#             "uom": item.stock_uom,
#             "custom_available_qty": f"{stall_qty} / {store_rooms_qty}",
#             "custom_last_month_sales": f"{last_month_sales} {item.stock_uom} / Rs {last_month_sales_price}",
#             "custom_previous_last_month_sales": f"{previous_last_month_sales} {item.stock_uom} / Rs {previous_last_month_sales_price}",
#             "custom_current_month_sales_2": f"{current_month_sales} {item.stock_uom} / Rs {current_month_sales_price}",
#             "custom_last_month_purchase": f"{last_month_purchase} {item.stock_uom} / Rs {last_month_purchase_price}",
#             "custom_previous_last_month_purchase": f"{previous_last_month_purchase} {item.stock_uom} / Rs {previous_last_month_purchase_price}",
#             "custom_current_month_purchase": f"{current_month_purchase} {item.stock_uom} / Rs {current_month_purchase_price}",
#             "custom_tax": item.custom_tax_rate,
#             "custom_mrp": item.custom_mrp,
#         })
        
#     return items

# Trial 2
# from datetime import datetime, timedelta

@frappe.whitelist()
def fetch_supplier_items(supplier):
    items = []
    
    item_defaults = frappe.get_all("Item Default", 
        filters={
            "default_supplier": supplier
        },
        fields=["parent"]
    )
    
    for row in item_defaults:
        item_code = row.parent
        item = frappe.get_doc("Item", item_code)
        
        # Fetch current balance of the item
        stall_qty, store_rooms_qty = get_item_current_balance(item_code)
        
        # Get the first and last day of the current month
        today = datetime.today()
        first_day_of_current_month = datetime(today.year, today.month, 1)
        last_day_of_current_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Make sure the dates cover the entire day
        first_day_of_current_month = first_day_of_current_month.replace(hour=0, minute=0, second=0, microsecond=0)
        last_day_of_current_month = last_day_of_current_month.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get the first and last day of the last month
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        # Get the first and last day of the month before the last month
        last_day_of_month_before_last = first_day_of_last_month - timedelta(days=1)
        first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)
        
        # Fetch sales and purchases for the last two months
        last_month_sales, last_month_purchase = get_qty_and_price(item_code, first_day_of_last_month, last_day_of_last_month)
        previous_last_month_sales, previous_last_month_purchase = get_qty_and_price(item_code, first_day_of_month_before_last, last_day_of_month_before_last)
        current_month_sales, current_month_purchase = get_qty_and_price(item_code, first_day_of_current_month, last_day_of_current_month)
        
        items.append({
                    "item_code": item_code,
                    "item_name": item.item_name,
                    "uom": item.stock_uom,
                    "custom_available_qty": f"{stall_qty if stall_qty is not None else 0} / {store_rooms_qty if store_rooms_qty is not None else 0}",
                    "custom_last_month_sales": f"{last_month_sales['total_qty'] if last_month_sales['total_qty'] is not None else 0} {item.stock_uom} / Rs {last_month_sales['avg_rate'] if last_month_sales['avg_rate'] is not None else 0}",
                    "custom_previous_last_month_sales": f"{previous_last_month_sales['total_qty'] if previous_last_month_sales['total_qty'] is not None else 0} {item.stock_uom} / Rs {previous_last_month_sales['avg_rate'] if previous_last_month_sales['avg_rate'] is not None else 0}",
                    "custom_current_month_sales_2": f"{current_month_sales['total_qty'] if current_month_sales['total_qty'] is not None else 0} {item.stock_uom} / Rs {current_month_sales['avg_rate'] if current_month_sales['avg_rate'] is not None else 0}",
                    "custom_last_month_purchase": f"{last_month_purchase['total_qty'] if last_month_purchase['total_qty'] is not None else 0} {item.stock_uom} / Rs {last_month_purchase['avg_rate'] if last_month_purchase['avg_rate'] is not None else 0}",
                    "custom_previous_last_month_purchase": f"{previous_last_month_purchase['total_qty'] if previous_last_month_purchase['total_qty'] is not None else 0} {item.stock_uom} / Rs {previous_last_month_purchase['avg_rate'] if previous_last_month_purchase['avg_rate'] is not None else 0}",
                    "custom_current_month_purchase": f"{current_month_purchase['total_qty'] if current_month_purchase['total_qty'] is not None else 0} {item.stock_uom} / Rs {current_month_purchase['avg_rate'] if current_month_purchase['avg_rate'] is not None else 0}",
                    "custom_tax": item.custom_tax_rate if item.custom_tax_rate is not None else 0,
                    "custom_mrp": item.custom_mrp if item.custom_mrp is not None else 0,
                })

        
    return items

def get_qty_and_price(item_code, start_date, end_date):
    # Query Sales Invoices for the given item within the given date range
    sales_qty = frappe.db.sql("""
        SELECT SUM(sii.qty) as total_qty, AVG(sii.rate) as avg_rate
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE sii.item_code = %s
            AND si.posting_date BETWEEN %s AND %s
            AND si.docstatus = 1
    """, (item_code, start_date, end_date), as_dict=True)[0]

    # Query Purchase Invoices for the given item within the given date range
    purchase_qty = frappe.db.sql("""
        SELECT SUM(pii.qty) as total_qty, AVG(pii.rate) as avg_rate
        FROM `tabPurchase Invoice` pi
        JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
        WHERE pii.item_code = %s
            AND pi.posting_date BETWEEN %s AND %s
            AND pi.docstatus = 1
    """, (item_code, start_date, end_date), as_dict=True)[0]

    return sales_qty, purchase_qty





def get_last_purchase_rate_from_item_price(item_code):
    item_price = frappe.get_all("Item Price",
                                 filters={"item_code": item_code, "price_list": "Standard Buying"},
                                 fields=["price_list_rate"],
                                 order_by="valid_from DESC",
                                 limit=1)

    if item_price:
        return item_price[0].price_list_rate
    else:
        return 0  # Return 0 if no item price is found

def get_item_tax_template(item):
    # Fetch the item's tax template (you may need to adjust the field name)
    return item.get("taxes")[0].get("item_tax_template", "") if item.get("taxes") else ""


def get_item_current_balance(item_code):
    # Fetch all warehouses
    all_warehouses = frappe.get_all("Warehouse", fields=["name", "custom_selling_warehouse"])

    # Separate the selling warehouse from the other warehouses
    selling_warehouse = next((wh['name'] for wh in all_warehouses if wh['custom_selling_warehouse']), None)
    other_warehouses = [wh['name'] for wh in all_warehouses if not wh['custom_selling_warehouse']]

    bin_docs = frappe.get_all("Bin",
                              filters={"item_code": item_code, "warehouse": ["in", [selling_warehouse] + other_warehouses]},
                              fields=["warehouse", "actual_qty"])

    quantity_by_warehouse = {warehouse: 0 for warehouse in [selling_warehouse] + other_warehouses}

    for bin_doc in bin_docs:
        warehouse = bin_doc.get("warehouse")
        actual_qty = bin_doc.get("actual_qty")
        quantity_by_warehouse[warehouse] += actual_qty

    # Sum up the quantities from all the other warehouses
    other_qty = sum(qty for warehouse, qty in quantity_by_warehouse.items() if warehouse in other_warehouses)

    return quantity_by_warehouse[selling_warehouse], other_qty




@frappe.whitelist()
def get_previous_purchase_details(item_code, rate):
    try:
        # Find the previous purchase details
        sql_query = """
            SELECT
                pi.supplier,
                pi.posting_date as date,
                MIN(pi_item.rate) as rate
            FROM
                `tabPurchase Invoice` pi
            JOIN
                `tabPurchase Invoice Item` pi_item ON pi.name = pi_item.parent
            WHERE
                pi_item.item_code = %(item_code)s
                AND pi_item.rate < %(rate)s
            GROUP BY
                pi.supplier,
                pi.posting_date
            ORDER BY
                rate ASC
            LIMIT 1
        """

        result = frappe.db.sql(sql_query, {'item_code': item_code, 'rate': rate}, as_dict=True)

        if result:
            return {
                'supplier': result[0].supplier,
                'date': result[0].date,
                'rate': result[0].rate
            }
        else:
            return _("No previous purchase invoice found for the given criteria.")

    except Exception as e:
        frappe.log_error(f"Error in get_previous_purchase_details: {e}")
        return _("Error occurred while fetching previous purchase details.")


@frappe.whitelist()
def get_tax_rate(item_tax_template):
    tax_rate = frappe.db.get_value('Item Tax Template Detail', {'parent': item_tax_template}, ['tax_rate'])
    print(tax_rate)
    return tax_rate

@frappe.whitelist()
def check_supplier_bill_no(supplier, custom_suppliers_bill_no):
    existing_po = frappe.get_value("Purchase Order", {
        'supplier': supplier,
        'custom_suppliers_bill_no': custom_suppliers_bill_no,
        'docstatus': 1  # Include only submitted Purchase Orders
    }, 'name')

    return {'existing_po': existing_po}