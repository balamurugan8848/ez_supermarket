// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("New Product", {
  on_submit: function (frm) {
    // Create a new Item when the Product is saved
    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.doctype.new_product.new_product.create_item_from_product",
      args: {
        product: frm.doc.name,
      },
      callback: function (response) {
        // Handle the response if needed
      },
    });
  },
});
