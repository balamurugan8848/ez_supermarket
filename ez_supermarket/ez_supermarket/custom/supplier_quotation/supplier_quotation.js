// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier Quotation Item", {
  item_code: function (frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    if (child.item_code) {
      frappe.call({
        method: "ez_supermarket.api.get_last_purchase_rate",
        args: {
          name: frm.doc.name,
          conversion_rate: frm.doc.conversion_rate,
          item_code: child.item_code,
          conversion_factor: child.conversion_factor,
        },
        callback: function (response) {
          if (response.message) {
            frappe.model.set_value(
              cdt,
              cdn,
              "last_purchase_rate",
              response.message
            );
          }
        },
      });
    }
  },
  before_save: function (frm) {
    if (!frm.doc.prompt_displayed) {
      frappe.validated = false;
      frm.doc.prompt_displayed = true;
      frappe.prompt(
        [
          {
            fieldname: "cost_is_less",
            fieldtype: "Check",
            label: "Cost is less",
          },
          { fieldname: "reliable", fieldtype: "Check", label: "Reliable" },
          {
            fieldname: "quicker_delivery",
            fieldtype: "Check",
            label: "Quicker Delivery",
          },
          {
            fieldname: "good_quality",
            fieldtype: "Check",
            label: "Good Quality",
          },
          { fieldname: "convenient", fieldtype: "Check", label: "Convenient" },
          {
            fieldname: "regular",
            fieldtype: "Check",
            label: "Regularly Purchasing",
          },
        ],
        function (values) {
          // update custom fields with selected options
          for (let key in values) {
            frm.set_value(key, values[key]);
          }
          setTimeout(function () {
            frappe.validated = true;
            frm.save();
          }, 100);
        },
        "Why did you choose this supplier?",
        "Submit"
      );
    }
  },
});
