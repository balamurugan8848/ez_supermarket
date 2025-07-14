# Copyright (c) 2024, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class YbSupermarketSettings(Document):
	pass


@frappe.whitelist()
def create_inventory_dimension(dimension_name, reference_document):
    inventory_dimension = frappe.new_doc('Inventory Dimension')
    inventory_dimension.dimension_name = dimension_name
    inventory_dimension.reference_document = reference_document
    inventory_dimension.save()
    return {"message": "success"}
