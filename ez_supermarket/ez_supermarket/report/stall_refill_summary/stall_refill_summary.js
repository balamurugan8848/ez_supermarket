// Copyright (c) 2025, Balamurugan and contributors
// For license information, please see license.txt

frappe.query_reports["Stall Refill Summary"] = {
	"filters": [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "item_code",
            label: "Item Code",
            fieldtype: "Link",
            options: "Item",
            reqd: 0
        },
        {
            fieldname: "stall_location",
            label: "Stall Location",
            fieldtype: "Data",
            reqd: 0
        }
    ]
};
