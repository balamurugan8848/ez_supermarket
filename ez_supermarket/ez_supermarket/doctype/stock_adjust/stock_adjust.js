// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

erpnext.stock.StockEntry = class StockEntry extends (
  erpnext.stock.StockController
) {
  scan_barcode() {
    const barcode_scanner = new erpnext.utils.BarcodeScanner({
      frm: this.frm,
    });
    barcode_scanner.process_scan();
  }
};
extend_cscript(
  cur_frm.cscript,
  new erpnext.stock.StockEntry({
    frm: cur_frm,
  })
);

frappe.ui.form.on("Stock Adjust", {
  refresh: function (frm) {
    frm.set_query("set_warehouse", function () {
      return {
        filters: {
          is_group: 0,
        },
      };
    });
  },
  onload: function (frm) {
    // Check the value of the Client Request checkbox
    frappe.model.with_doc(
      "Yb Supermarket Settings",
      "Yb Supermarket Settings",
      function () {
        var settings_doc = frappe.get_doc(
          "Yb Supermarket Settings",
          "Yb Supermarket Settings"
        );
        if (settings_doc.stock_adjust == 0) {
          // If Client Request is not checked, hide the form and throw an error
          $.each(frm.fields_dict, function (fieldname, field) {
            field.df.hidden = 1;
          });
          frm.refresh_fields();
          // Disable the Save button
          frm.disable_save();
          var settings_link = frappe.utils.get_form_link(
            "Yb Supermarket Settings",
            settings_doc.name
          );
          frappe.throw(
            "You must enable <strong>Stock Adjust</strong> feature in <a href='" +
              settings_link +
              "'><strong>Yb Supermarket Settings</a></strong> to access this page."
          );
        }
      }
    );
  },
});
frappe.ui.form.on("Stock Adjust Details", {
  item_code: function (frm, cdt, cdn) {
    updateAvailableQty(frm, cdt, cdn);
  },

  t_warehouse: function (frm, cdt, cdn) {
    updateAvailableQty(frm, cdt, cdn);
  },
  // qty: function (frm, cdt, cdn) {
  //   var value = frm.doc.qty;
  //   frm.set_value("actual_qty", value);
  // },
});

function updateAvailableQty(frm, cdt, cdn) {
  var row = locals[cdt][cdn];

  // Check if both t_warehouse and item_code are selected
  if (row.t_warehouse && row.item_code) {
    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.doctype.stock_adjust.stock_adjust.get_available_qty",
      args: {
        warehouse: row.t_warehouse,
        item_code: row.item_code,
      },
      callback: function (r) {
        if (r.message) {
          frappe.model.set_value(cdt, cdn, "available_qty", r.message);
        }
      },
    });
  }
}
