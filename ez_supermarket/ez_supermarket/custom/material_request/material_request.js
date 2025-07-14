// Copyright (c) 2024, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Request", "refresh", function (frm) {
  if (frappe.user.has_role("PTPS_FIN_M")) {
    frm.add_custom_button(__("Budget Status"), function () {
      // Fetch the total budget value from the AV Budget DocType
      frappe.call({
        method: "frappe.client.get_value",
        args: {
          doctype: "AV Budget",
          fieldname: "total_budget",
          filters: {
            // You can specify filters based on your logic
            fiscal_year: frm.doc.fiscal_year,
          },
        },
        callback: function (r1) {
          // Fetch the total expenses value from the Profit and Loss Report
          frappe.call({
            method: "frappe.desk.query_report.run",
            args: {
              report_name: "AV Budget Info",
              filters: {
                // You can specify filters based on your logic
                company: frm.doc.company,
                from_fiscal_year: frm.doc.fiscal_year,
                to_fiscal_year: frm.doc.fiscal_year,
              },
            },
            callback: function (r2) {
              // Calculate the balance amount as the difference between the total budget and the total expenses
              var total_budget = r1.message.total_budget;
              var total_expenses = r2.message.result[0].total_expenses;
              var balance_amount = total_budget - total_expenses;
              // Show all values in a popup
              frappe.msgprint(
                __(
                  "The total budget for this fiscal year is {0}, the total expenses so far is {1}, and the balance amount is {2}",
                  [total_budget, total_expenses, balance_amount]
                )
              );
            },
          });
        },
      });
    });
  }
});
