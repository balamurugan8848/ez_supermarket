// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item", {
  setup: function (frm) {
    const warehouseFilters = {
      is_group: "0",
    };

    frm.set_query("custom_default_store_warehouse", function () {
      return { filters: warehouseFilters };
    });

    frm.set_query("custom_default_stall_warehouse", function () {
      return { filters: warehouseFilters };
    });

    frm.set_query("custom_default_store_location", function (doc) {
      return { filters: { warehouse: doc.custom_default_store_warehouse } };
    });

    frm.set_query("custom_default_stall_location", function (doc) {
      return { filters: { warehouse: doc.custom_default_stall_warehouse } };
    });
  },
  validate: function (frm) {
    console.log("Validation of Item Form");

    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.custom.item.item.apply_tax_template",
      args: {
        doc_json: JSON.stringify(frm.doc),
      },
      callback: function (r) {
        console.log("Server response:", r);
        // Update the form with the response
        frm.doc = r.message;
      },
    });
  },
  custom_mrp: function (frm) {
    var value = frm.doc.custom_mrp;
    frm.set_value("standard_rate", value);
    frm.set_value("valuation_rate", value);
  },
});
