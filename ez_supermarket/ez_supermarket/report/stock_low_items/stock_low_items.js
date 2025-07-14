// Copyright (c) 2023, Jagan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Low Items"] = {
  filters: [
    {
      fieldname: "group_by",
      label: __("Group By"),
      fieldtype: "Select",
      width: "80",
      reqd: 1,
      options: ["Warehouse", "Company"],
      default: "Warehouse",
    },
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      width: "80",
      options: "Company",
      reqd: 1,
      default: frappe.defaults.get_user_default("Company"),
      depends_on: "eval: doc.group_by != 'Company'",
    },
    {
      fieldname: "safety_stock_equal_to_qty",
      label: __("Safety Stock Equal to Current Qty"),
      fieldtype: "Check",
      default: 0,
    },
    {
      fieldname: "qty_less_than_safety_stock",
      label: __("Actual Qty Less Than Safety Stock"),
      fieldtype: "Check",
      default: 0,
    },
  ],
};
