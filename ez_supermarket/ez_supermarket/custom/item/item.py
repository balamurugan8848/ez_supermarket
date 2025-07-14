# Copyright (c) 2023, Balamurugan and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.utils import add_months, today
from datetime import datetime
from datetime import datetime, timedelta

# Server method
@frappe.whitelist()
def apply_tax_template(doc_json):
    doc = json.loads(doc_json)

    # Clear existing tax rows
    doc["taxes"] = []

    tax_rate = doc.get("custom_tax_rate")
    if tax_rate:
        # Fetch the company name from the 'item_defaults' table
        company = doc.get("item_defaults")[0].get("company") if doc.get("item_defaults") else None

        if company:
            # Fetch the company abbreviation
            company_abbr = frappe.db.get_value("Company", company, "abbr")

            if not company_abbr:
                frappe.throw(_("Could not find abbreviation for company: {0}").format(company))

                    # Create a new row in the taxes child table for In-State tax category
            tax_row_in_state = {
                "item_tax_template": "GST {}% - {}".format(tax_rate, company_abbr),
                "tax_category": "In-State"
            }
            doc["taxes"].append(tax_row_in_state)

            # Create another row in the taxes child table for Out-State tax category
            tax_row_out_state = {
                "item_tax_template": "GST {}% - {}".format(tax_rate, company_abbr),
                "tax_category": "Out-State"
            }
            doc["taxes"].append(tax_row_out_state)

    return doc

