// Copyright (c) 2024, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Yb Supermarket Settings", {
  create_inventory_dimension: function (frm) {
    createInventoryDimension(frm);
    // Hide the button after it's pressed
    frm.set_df_property("create_inventory_dimension", "hidden", 1);
  },
});

function createInventoryDimension(frm) {
  frappe.call({
    method:
      "ez_supermarket.ez_supermarket.doctype.yb_supermarket_settings.yb_supermarket_settings.create_inventory_dimension",
    args: {
      dimension_name: frm.doc.dimension_name,
      reference_document: frm.doc.reference_document,
    },
    callback: function (r) {
      if (r.message) {
        frm.refresh();
        frappe.msgprint(__("Inventory Dimension created successfully."));
      }
    },
  });
}
