import frappe
import json

# @frappe.whitelist()
# def get_data(filters):
    
#     filters = frappe.parse_json(filters)

#     query = """
#         SELECT
#             sle.posting_date,
#             sle.item_code,
#             sle.warehouse,
#             SUM(IF(sle.actual_qty < 0, -sle.actual_qty, 0)) AS qty_sold,
#             i.custom_location,
#             i.custom_max_qty,
#             SUM(sle.actual_qty) AS current_qty,
#             ABS(SUM(sle.actual_qty)) AS qty_to_be_refilled
#         FROM
#             `tabStock Ledger Entry` sle
#         JOIN
#             `tabItem` i ON sle.item_code = i.item_code
#         WHERE
#             sle.docstatus = 1
#             AND DATE(sle.posting_date) = %(date)s
#         GROUP BY
#             DATE(sle.posting_date), sle.item_code, sle.warehouse, i.custom_location, i.custom_max_qty
#     """
#     return frappe.db.sql(query, filters, as_dict=True)