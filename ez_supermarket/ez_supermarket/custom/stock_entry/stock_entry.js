// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt
frappe.ui.form.on("Stock Entry", {
  refresh: function (frm) {
    frm.fields_dict["items"].grid.get_field("item_location").get_query =
      function (doc, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (doc.purpose === "Material Transfer") {
          return {
            filters: { warehouse: child.s_warehouse },
          };
        } else {
          return {};
        }
      };

    frm.fields_dict["items"].grid.get_field("to_item_location").get_query =
      function (doc, cdt, cdn) {
        var child = locals[cdt][cdn];
        if (doc.purpose === "Material Transfer") {
          return {
            filters: { warehouse: child.t_warehouse },
          };
        } else {
          return {};
        }
      };
  },
  onload: function (frm) {
    if (frm.doc.custom_document_type === "Stall Refill Request") {
      $.each(frm.doc.items || [], function (i, d) {
        if (d.item_code) {
          frm.script_manager.trigger("item_code", d.doctype, d.name);
        }
        // Check if valuation rate is 0, blank, or null
        if (!d.basic_rate || d.basic_rate === 0) {
          // Set allow_zero_valuation_rate to 1
          frappe.model.set_value(
            d.doctype,
            d.name,
            "allow_zero_valuation_rate",
            1
          );
        }
      });
    }
  },
});

frappe.ui.form.on("Stock Entry Detail", {
  item_code: function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    frappe.call({
      method: "frappe.client.get",
      args: {
        doctype: "Item",
        name: row.item_code,
      },
      callback: function (response) {
        var item = response.message;
        frappe.model.set_value(
          cdt,
          cdn,
          "s_warehouse",
          item.custom_default_store_warehouse
        );
        frappe.model.set_value(
          cdt,
          cdn,
          "t_warehouse",
          item.custom_default_stall_warehouse
        );
        frappe.model.set_value(
          cdt,
          cdn,
          "item_location",
          item.custom_default_store_location
        );
        frappe.model.set_value(
          cdt,
          cdn,
          "to_item_location",
          item.custom_default_stall_location
        );
      },
    });
  },
});
