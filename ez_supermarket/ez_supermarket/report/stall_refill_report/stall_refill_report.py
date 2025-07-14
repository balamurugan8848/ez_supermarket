# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {'fieldname': 'posting_date', 'label': _('Posting Date'), 'fieldtype': 'Data'},
        {'fieldname': 'item_code', 'label': _('Item Code'), 'fieldtype': 'Data'},
        {'fieldname': 'warehouse', 'label': _('Warehouse'), 'fieldtype': 'Link', 'options': 'Warehouse'},     
        {'fieldname': 'custom_default_stall_location', 'label': _('Location'), 'fieldtype': 'Data'},
        {'fieldname': 'qty_sold', 'label': _('Quantity Sold'), 'fieldtype': 'Float'},
        {'fieldname': 'custom_max_qty', 'label': _('Max Qty'), 'fieldtype': 'Float'},
        {'fieldname': 'qty_after_transaction', 'label': _('Current Qty'), 'fieldtype': 'Float'},
        {'fieldname': 'qty_to_be_refilled', 'label': _('Refill Qty'), 'fieldtype': 'Float'},
    ]

    data = get_data(filters)

    return columns, data

def get_data(filters):
    query = """
        SELECT
            sle.posting_date,
            sle.item_code,
            sle.warehouse,
            SUM(IF(sle.actual_qty < 0, -sle.actual_qty, 0)) AS qty_sold,
            i.custom_default_stall_location,
            i.custom_max_qty,
            (SELECT sle2.qty_after_transaction FROM `tabStock Ledger Entry` sle2 
             WHERE sle2.item_code = sle.item_code AND DATE(sle2.posting_date) = DATE(sle.posting_date) 
             ORDER BY sle2.posting_date DESC, sle2.posting_time DESC LIMIT 1) AS qty_after_transaction,
            (i.custom_max_qty - (SELECT sle2.qty_after_transaction FROM `tabStock Ledger Entry` sle2 
             WHERE sle2.item_code = sle.item_code AND DATE(sle2.posting_date) = DATE(sle.posting_date) 
             ORDER BY sle2.posting_date DESC, sle2.posting_time DESC LIMIT 1)) AS qty_to_be_refilled
        FROM
            `tabStock Ledger Entry` sle
        JOIN
            `tabItem` i ON sle.item_code = i.item_code
        WHERE
            sle.docstatus = 1 AND
            sle.voucher_type = 'Sales Invoice'
            AND DATE(sle.posting_date) = %(date)s
        GROUP BY
            DATE(sle.posting_date), sle.item_code, sle.warehouse, i.custom_default_stall_location, i.custom_max_qty
        ORDER BY
            sle.posting_date DESC
    """
    return frappe.db.sql(query, filters, as_dict=True)
