// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.accounts");

// erpnext.accounts.payment_triggers.setup("Purchase Master");
erpnext.accounts.taxes.setup_tax_filters("Purchase Taxes and Charges");
erpnext.accounts.taxes.setup_tax_validations("Purchase Master");
erpnext.buying.setup_buying_controller();

erpnext.accounts.PurchaseInvoice = class PurchaseInvoice extends (
  erpnext.buying.BuyingController
) {
  // setup(doc) {
  //   this.setup_posting_date_time_check();
  //   super.setup(doc);
  // }

  onload() {
    if (this.frm.doc.supplier && this.frm.doc.__islocal) {
      this.frm.trigger("supplier");
    }
  }
};

cur_frm.script_manager.make(erpnext.accounts.PurchaseInvoice);

cur_frm.fields_dict["items"].grid.get_field("item_code").get_query = function (
  doc,
  cdt,
  cdn
) {
  return {
    query: "erpnext.controllers.queries.item_query",
    filters: { is_purchase_item: 1 },
  };
};

frappe.ui.form.on("Purchase Master", {
  refresh: function (frm) {
    // Check the value of the Client Request checkbox
    frappe.model.with_doc(
      "Yb Supermarket Settings",
      "Yb Supermarket Settings",
      function () {
        var settings_doc = frappe.get_doc(
          "Yb Supermarket Settings",
          "Yb Supermarket Settings"
        );
        if (settings_doc.purchase_master == 0) {
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
            "You must enable <strong>Purchase Master</strong> feature in <a href='" +
              settings_link +
              "'><strong>Yb Supermarket Settings</a></strong> to access this page."
          );
        }
      }
    );
    frm.fields_dict.items.grid.add_custom_button(
      __("Fetch Supplier Items"),
      function () {
        fetchSupplierItems(frm);
      }
    );
    frm.add_custom_button("Calculate Purchase Qty", function () {
      // Create a new dialog
      var d = new frappe.ui.Dialog({
        title: "Enter details",
        fields: [
          {
            label: "Number of Months",
            fieldname: "months",
            fieldtype: "Int",
            reqd: 1,
            change: function () {
              // Perform action when the number of months changes
              var numberOfMonths = this.value;
              // Calculate total purchase quantity for each item
              var items = frm.doc.items;
              for (var i = 0; i < items.length; i++) {
                var item = items[i];
                var totalPurchaseQty = calculateTotalPurchaseQty(
                  item.item_code,
                  numberOfMonths
                );
                // Update the pur_qty field for the item
                d.fields_dict.items.df.data[i].pur_qty = totalPurchaseQty;
              }
              d.refresh_field("items");
            },
          },

          {
            label: "Items",
            fieldname: "items",
            fieldtype: "Table",
            fields: [
              {
                label: "Item Code",
                fieldname: "item_code",
                fieldtype: "Data",
                read_only: 1,
                in_list_view: 1,
              },
              {
                label: "Qty",
                fieldname: "qty",
                fieldtype: "Float",
                read_only: 1,
                in_list_view: 1,
              },
              {
                label: "Total Purchase Qty",
                fieldname: "pur_qty",
                fieldtype: "Float",
                read_only: 1,
                in_list_view: 1,
              },
              {
                label: "Suggested Qty",
                fieldname: "suggested_qty",
                fieldtype: "Float",
                read_only: 1,
                in_list_view: 1,
              },
            ],
            in_place_edit: true,
            data: frm.doc.items.map((item) => ({
              item_code: item.item_code,
              qty: item.qty,
              pur_qty: 0, // Initialize pur_qty to 0
              suggested_qty: 0,
            })),
          },
        ],
        primary_action_label: "Calculate",
        primary_action: function () {},
      });

      d.show();
    });
  },
  //   frm.add_custom_button("Calculate Purchase Qty", function () {
  //     const months = prompt("Based on how many months?");
  //     if (months !== null && !isNaN(months)) {
  //       frappe.call({
  //         method:
  //           "ez_supermarket.ez_supermarket.doctype.purchase_master.purchase_master.calculate_purchase_quantity",
  //         doc: frm.doc,
  //         args: { months: parseInt(months) },
  //         callback: function (r) {
  //           const data = r.message;
  //           frm.clear_table("items");
  //           data.forEach((item) => {
  //             const child = frm.add_child("items");
  //             frappe.model.set_value(
  //               child.doctype,
  //               child.name,
  //               "item_code",
  //               item.item_code
  //             );
  //             frappe.model.set_value(
  //               child.doctype,
  //               child.name,
  //               "qty",
  //               item.suggested_qty
  //             );
  //           });
  //           frm.refresh_field("items");
  //           frappe.msgprint(
  //             __("Suggested purchase quantities have been calculated.")
  //           );
  //         },
  //       });
  //     }
  //   });
  // },

  mode_of_payment: function (frm) {
    // Call the server-side function to get the Cash or Bank account
    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.doctype.purchase_master.purchase_master.get_bank_cash_account",
      args: {
        mode_of_payment: frm.doc.mode_of_payment,
        company: frm.doc.company,
      },
      callback: function (response) {
        // Set the Cash or Bank Account field with the fetched account
        if (response.message && response.message.account) {
          frm.set_value("cashbank_account", response.message.account);
        }
      },
    });
  },
  tax_category: function (frm) {
    if (frm.doc.tax_category) {
      frm.events.set_taxes_and_charges(frm);
    }
  },
  set_taxes_and_charges: function (frm) {
    if (frm.doc.tax_category) {
      frappe.call({
        method: "frappe.client.get_list",
        args: {
          doctype: "Purchase Taxes and Charges Template",
          filters: {
            company: frm.doc.company,
            tax_category: frm.doc.tax_category,
          },
          fields: ["name"],
        },
        callback: function (response) {
          if (response && response.message && response.message.length > 0) {
            // Set taxes and charges based on the retrieved tax template
            frm.set_value("taxes_and_charges", response.message[0].name);
          } else {
            // Handle case where no matching tax template is found
            frm.set_value("taxes_and_charges", "");
            frappe.msgprint(
              "No matching tax template found for the selected tax category."
            );
          }
          refresh_field("taxes_and_charges");
        },
      });
    }
  },
});
function calculateTotalPurchaseQty(item_code, numberOfMonths) {
  frappe.call({
    method:
      "ez_supermarket.ez_supermarket.doctype.purchase_master.purchase_master.get_total_purchase_qty",
    args: {
      item_code: item_code,
      number_of_months: numberOfMonths,
    },
    callback: function (r) {
      if (r.message) {
        var totalQty = r.message.total_qty;
        var suggestedQty = totalQty / numberOfMonths;

        // Update the pur_qty and suggested_qty fields
        var itemIndex = frm.doc.items.findIndex(
          (item) => item.item_code === item_code
        );
        if (itemIndex !== -1) {
          d.fields_dict.items.df.data[itemIndex].pur_qty = totalQty;
          d.fields_dict.items.df.data[itemIndex].suggested_qty = suggestedQty;
        }
      }
    },
  });
}
function fetchSupplierItems(frm) {
  // Get supplier
  var supplier = frm.doc.supplier;
  frappe.call({
    method:
      "ez_supermarket.ez_supermarket.custom.purchase_order.purchase_order.fetch_supplier_items",
    args: {
      supplier: supplier,
    },
    callback: function (r) {
      // console.log("Response from server:", r);

      if (r.message && r.message.length > 0) {
        // Clear existing rows
        frm.doc.items = [];

        // Add fetched items
        $.each(r.message, function (i, item) {
          // console.log("Processing item:", item);

          var child = frm.add_child("items");
          child.item_code = item.item_code;
          frm.script_manager.trigger("item_code", child.doctype, child.name);
          child.custom_available_qty = item.custom_available_qty;
          child.custom_last_month_sales = item.custom_last_month_sales;
          child.custom_tax = item.custom_tax;
          child.custom_mrp = item.custom_mrp;
          child.custom_previous_last_month_sales =
            item.custom_previous_last_month_sales;
          child.custom_current_month_sales_2 =
            item.custom_current_month_sales_2;
          child.custom_current_month_purchase =
            item.custom_current_month_purchase;
          child.custom_last_month_purchase = item.custom_last_month_purchase;
          child.custom_previous_last_month_purchase =
            item.custom_previous_last_month_purchase;
          child.custom_average_sales_last_3_months =
            (item.custom_last_month_sales +
              item.custom_previous_last_month_sales +
              item.custom_current_month_sales_2) /
            3;
          child.custom_average_purchase_last_3_months =
            (item.custom_current_month_purchase +
              item.custom_last_month_purchase +
              item.custom_previous_last_month_purchase) /
            3;
          // Calculate and set custom_forecasted_sales and custom_forecasted_purchase using exponential smoothing
        });

        // frm.refresh_field("buying_price_list");
        frm.refresh_field("items");
      } else {
        frappe.msgprint("No items found for supplier.");
      }
    },
  });
}
function purchaseqtycal(frm) {}
