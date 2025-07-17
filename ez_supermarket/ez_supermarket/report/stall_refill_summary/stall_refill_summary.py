# Copyright (c) 2025, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    if not filters:
        filters = {}

    conditions = []
    values = {}

    # Apply date filter
    if filters.get("from_date"):
        conditions.append("srr.posting_date >= %(from_date)s")
        values["from_date"] = getdate(filters.get("from_date"))

    if filters.get("to_date"):
        conditions.append("srr.posting_date <= %(to_date)s")
        values["to_date"] = getdate(filters.get("to_date"))

    if filters.get("item_code"):
        conditions.append("srd.item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")

    if filters.get("stall_location"):
        conditions.append("srd.stall_location = %(stall_location)s")
        values["stall_location"] = filters.get("stall_location")

    condition_str = " AND ".join(conditions)
    if condition_str:
        condition_str = "WHERE " + condition_str

    data = frappe.db.sql(f"""
        SELECT
            srr.posting_date,
            srd.stall_location,
            srd.store_location,
            srd.item_code,
            srd.item_name,
            srd.refill_qty
        FROM
            `tabStall Refill Request` srr
        JOIN
            `tabStall Request Details` srd ON srr.name = srd.parent
        {condition_str}
        ORDER BY srr.posting_date DESC
    """, values, as_dict=1)

    columns = [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Stall Location", "fieldname": "stall_location", "fieldtype": "Data", "width": 180},
        {"label": "Store Location", "fieldname": "store_location", "fieldtype": "Data", "width": 180},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Refill Qty", "fieldname": "refill_qty", "fieldtype": "Float", "width": 120},
    ]

    return columns, data
