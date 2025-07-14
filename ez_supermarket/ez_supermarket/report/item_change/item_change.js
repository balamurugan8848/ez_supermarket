// // Copyright (c) 2023, Balamurugan and contributors
// // For license information, please see license.txt

frappe.query_reports["Item Change"] = {
  filters: [
    {
      fieldname: "date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
      reqd: 1,
    },
  ],

  get_query: function (report) {
    return {
      filters: {
        date: frappe.datetime.get_today() + " 00:00:00",
        // Add more filters as needed
      },
    };
  },
};
// //   onload: function (report) {
// //     report.page.add_inner_button(__("Item Transfer Request"), function () {
// //       createMaterialRequest(report.data);
// //     });
// //   },
// // };

// // function createMaterialRequest(data) {
// //   frappe.call({
// //     method:
// //       "ez_supermarket.ez_supermarket.report.item_change.item_change.create_material_requests",
// //     args: {
// //       items: data,
// //     },
// //     callback: function (response) {
// //       if (response.message && response.message.status === "success") {
// //         frappe.msgprint(__("Material Requests created successfully."));
// //       } else {
// //         frappe.msgprint({
// //           title: __("Error"),
// //           indicator: "red",
// //           message: __(
// //             "Failed to create Material Requests. Please check the server logs for details."
// //           ),
// //         });
// //       }
// //     },
// //   });
// // }
