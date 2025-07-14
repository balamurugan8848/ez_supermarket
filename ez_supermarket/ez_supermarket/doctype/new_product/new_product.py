# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NewProduct(Document):
	pass

@frappe.whitelist()
def create_item_from_product(product):
    # Check if the Item already exists
    if frappe.db.exists("Item", product):
        frappe.msgprint(f"Item {product} already exists.")
        return

    # Get data from the "New Product" document
    new_product = frappe.get_doc("New Product", product)

    # Create a new Item
    item = frappe.new_doc("Item")
    item.item_code = frappe.scrub(product)
    item.item_name = product
    item.custom_article_code = new_product.article_code
    # item.description = new_product.description
    item.item_group = new_product.item_group
    item.custom_tax_rate = new_product.tax_rate
    item.gst_hsn_code = new_product.hsn_code
    item.maintain_stock = 1
    # Set other properties as needed

    # Save the Item
    item.insert(ignore_permissions=True)

    frappe.msgprint(f"Item {item.item_code} created successfully.")

    return item.name

