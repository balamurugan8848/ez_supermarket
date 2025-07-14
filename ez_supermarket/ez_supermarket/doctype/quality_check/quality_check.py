# Copyright (c) 2024, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today
from datetime import timedelta, datetime
import json

class QualityCheck(Document):
    pass

def validate_purchase_order(doc_details):
	if doc_details.docstatus != 1: return { "status": False, "msg": "Invalid docstatus for QC Process" }
	if doc_details.status == "On Hold" or doc_details.status == "Completed": return { "status": False,"msg": "Invalid status for QC Process" }
	return { "status": True, "msg": "" }

@frappe.whitelist()
def generate_quality_check(doc_type, doc_name):
	doc = frappe.get_doc(doc_type, doc_name)
	doc_details = doc.as_dict()

	validation = validate_purchase_order(doc_details)

	if not validation.get("status", False):
		frappe.throw(
			title="Error",
			msg=validation.get("msg", "Internal Server Error")
		)
	
	inspection_type = {
		"Purchase Order": "Incoming"
	}

	outerJson = {
		"doctype": "Quality Check",
		# "accepted_warehouse": doc_details.set_warehouse,
		"document_type": doc_type,
		"ref_document": doc_name,
		"supplier": doc_details.supplier,
		"status": "Accepted",
		"date": today(),
		"inspection_type": inspection_type.get(doc_type, "Incoming"),
		"accepted_item": []
	}

	for i in doc_details.get("items", []):
		innerJson = {
			"item_code": i.get("item_code"),
			"accepted_qty": i.get("qty"),
			"uom": i.get("uom"),
			"received_qty": i.get("qty"),
			"total_qty": i.get("qty"),
			"warehouse": i.get("warehouse")
		}

		outerJson["accepted_item"].append(innerJson)
	
	new_doc = frappe.new_doc("Quality Check")
	new_doc.update(outerJson)
	new_doc.save()
	# generate_batch_number(new_doc.name)

	return new_doc.name

def get_item_map(ref_doc):
	i_map = {}
	i_price = {}

	for i in ref_doc.items:
		i_map[i.item_code] = i.name
		i_price[i.item_code] = i.rate
	
	return i_map, i_price

@frappe.whitelist()
def generate_purchase_receipt(doc_type, doc_name):
	doc = frappe.get_doc(doc_type, doc_name)
	doc_details = doc.as_dict()
	doc_purchase = frappe.get_doc("Purchase Order", doc.get("ref_document"))

	ref_doc = frappe.get_doc(doc_details.get("document_type"), doc_details.get("ref_document"))
	item_map, item_price = get_item_map(ref_doc)

	if doc_details.get("document_type") != "Purchase Order":
		frappe.throw(
			title="Error",
			msg="Cannot generate Purchase Receipt"
		)

	outerJson = {
		"doctype": "Purchase Receipt",
		"supplier": doc_details.supplier,
		"qc_ref": doc_name,
		# "set_warehouse": doc_details.get("accepted_warehouse"),
		"rejected_warehouse": doc_details.get("rejected_warehouse"),
		"items": [],
		"tax_category": ref_doc.tax_category,
		"taxes_and_charges": ref_doc.taxes_and_charges,
		"taxes":[]
	}

	for i in doc_details.get("accepted_item", []):
		if not (i.get("accepted_qty") > 0): continue
		innerJson = {
			"item_code": i.get("item_code"),
			"uom": i.get("uom"),
			"received_qty": i.get("received_qty"),
			"qty": i.get("accepted_qty"),
			"rejected_qty": i.get("rejected_qty"),
			"purchase_order": ref_doc.name,
			"purchase_order_item": item_map.get(i.get("item_code")),
			"rate": item_price.get(i.get("item_code")),
			"warehouse": i.get("warehouse"),
			# "batch_no": i.get("batch_no"),
			"custom_expiry_date":i.get("expiry_date"),
			
		}

		outerJson["items"].append(innerJson)
	
	for i in doc_purchase.taxes:
		inJson = {
					"charge_type":i.get("charge_type"),
					"account_head": i.get("account_head"),
					"rate": i.get("rate"),
					"tax_amount": i.get("tax_amount"),
					"total": i.get("total"),
					"description": i.get("description")
		}
		outerJson["taxes"].append(inJson)
	print(outerJson)

	new_doc = frappe.new_doc("Purchase Receipt")
	new_doc.update(outerJson)
	new_doc.save()

	return new_doc.name
