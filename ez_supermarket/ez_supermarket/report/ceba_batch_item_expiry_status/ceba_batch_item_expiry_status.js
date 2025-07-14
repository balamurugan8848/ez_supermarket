// Copyright (c) 2023, Jagan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ceba Batch Item Expiry Status"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      width: "80",
      default: frappe.sys_defaults.year_start_date,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      width: "80",
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: "expiring_within_0_days",
      label: __("Expiring Within 0 Days"),
      fieldtype: "Check",
      default: 0,
    },
    {
      fieldname: "expiring_within_7_days",
      label: __("Expiring Within 7 Days"),
      fieldtype: "Check",
      default: 0,
    },
    {
      fieldname: "expiring_within_15_days",
      label: __("Expiring Within 15 Days"),
      fieldtype: "Check",
      default: 0,
    },
  ],
};
