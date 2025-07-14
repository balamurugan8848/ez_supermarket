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
    // Settings check: hides form if disabled
    frappe.model.with_doc("Yb Supermarket Settings", "Yb Supermarket Settings", function () {
      var settings_doc = frappe.get_doc("Yb Supermarket Settings", "Yb Supermarket Settings");
      if (settings_doc.purchase_master == 0) {
        $.each(frm.fields_dict, function (fieldname, field) {
          field.df.hidden = 1;
        });
        frm.refresh_fields();
        frm.disable_save();
        var settings_link = frappe.utils.get_form_link("Yb Supermarket Settings", settings_doc.name);
        frappe.throw("You must enable <strong>Purchase Master</strong> feature in <a href='" + settings_link + "'><strong>Yb Supermarket Settings</a></strong> to access this page.");
      }
    });

    // Fetch Supplier Items button
    frm.fields_dict.items.grid.add_custom_button(__("Fetch Supplier Items"), function () {
      fetchSupplierItems(frm);
    });

    // Calculate Purchase Qty button
    frm.add_custom_button("Calculate Purchase Qty", function () {
      const itemData = frm.doc.items.map((item) => ({
        item_code: item.item_code,
        qty: item.qty,
        pur_qty: 0,
        suggested_qty: 0
      }));

      const dialog = new frappe.ui.Dialog({
        title: "Enter details",
        fields: [
          {
            label: "Number of Months",
            fieldname: "months",
            fieldtype: "Int",
            reqd: 1
          },
          {
            label: "Items",
            fieldname: "items",
            fieldtype: "Table",
            fields: [
              { label: "Item Code", fieldname: "item_code", fieldtype: "Data", read_only: 1, in_list_view: 1 },
              { label: "Qty", fieldname: "qty", fieldtype: "Float", read_only: 1, in_list_view: 1 },
              { label: "Total Purchase Qty", fieldname: "pur_qty", fieldtype: "Float", read_only: 1, in_list_view: 1 },
              { label: "Suggested Qty", fieldname: "suggested_qty", fieldtype: "Float", read_only: 1, in_list_view: 1 }
            ],
            in_place_edit: true,
            data: itemData
          }
        ],
        primary_action_label: "Calculate",
        primary_action(values) {
          const months = values.months;
          const rows = dialog.fields_dict.items.df.data;

          // Loop through each item and fetch server data
          rows.forEach((row, index) => {
            frappe.call({
              method: "ez_supermarket.ez_supermarket.doctype.purchase_master.purchase_master.get_total_purchase_qty",
              args: {
                item_code: row.item_code,
                number_of_months: months
              },
              callback: function (r) {
                if (r.message) {
                  row.pur_qty = r.message.total_qty;
                  row.suggested_qty = Math.ceil(r.message.total_qty / months);
                  dialog.fields_dict.items.refresh();
                }
              }
            });
          });
        }
      });

      dialog.show();
    });
  },

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
  const supplier = frm.doc.supplier;

  frappe.call({
    method: "ez_supermarket.ez_supermarket.custom.purchase_order.purchase_order.fetch_supplier_items",
    args: { supplier },
    callback: function (r) {
      if (!r.message || r.message.length === 0) {
        frappe.msgprint("No items found for supplier.");
        frm.fields_dict.supplier_item_table.$wrapper.html("<p>No data available.</p>");
        return;
      }

      frm.doc.items = [];

      // Extract quantity from "qty UOM / Rs rate"
      function parseQty(text) {
        if (!text || typeof text !== "string") return 0;
        const match = text.trim().match(/^([\d.]+)/);
        return match ? parseFloat(match[1]) : 0;
      }

      let html = `
        <div style="overflow-x:auto; max-height:400px; overflow-y:auto;">
          <table class="table table-bordered table-sm table-hover table-striped text-nowrap">
            <thead class="bg-light sticky-top">
              <tr class="text-center align-middle" style="background:#e9ecef;">
                <th rowspan="2">Item Code</th>
                <th colspan="2" style="background:#f7fafc;">Stock Qty</th>
                <th colspan="2" style="background:#f8f9fa;">Item Info</th>
                <th colspan="3" style="background:#e2f0d9;">Sales</th>
                <th colspan="3" style="background:#fde9ea;">Purchases</th>
                <th colspan="2" style="background:#fef9ec;">Avg (3M)</th>
              </tr>
              <tr class="text-center align-middle small text-muted">
                <th>Stall</th><th>Store</th>
                <th>MRP</th><th>Tax %</th>
                <th>CM</th><th>LM</th><th>PLM</th>
                <th>CM</th><th>LM</th><th>PLM</th>
                <th>Sales</th><th>Purchase</th>
              </tr>
            </thead>
            <tbody>`;

      $.each(r.message, function (i, item) {
        const s1 = parseQty(item.custom_current_month_sales_2);
        const s2 = parseQty(item.custom_last_month_sales);
        const s3 = parseQty(item.custom_previous_last_month_sales);
        const p1 = parseQty(item.custom_current_month_purchase);
        const p2 = parseQty(item.custom_last_month_purchase);
        const p3 = parseQty(item.custom_previous_last_month_purchase);

        const avg_sales = (s1 + s2 + s3) / 3;
        const avg_purchase = (p1 + p2 + p3) / 3;

        const child = frm.add_child("items");
        child.item_code = item.item_code;
        frm.script_manager.trigger("item_code", child.doctype, child.name);

        Object.assign(child, {
          custom_available_qty: item.custom_available_qty,
          custom_last_month_sales: item.custom_last_month_sales,
          custom_previous_last_month_sales: item.custom_previous_last_month_sales,
          custom_current_month_sales_2: item.custom_current_month_sales_2,
          custom_tax: item.custom_tax,
          custom_mrp: item.custom_mrp,
          custom_last_month_purchase: item.custom_last_month_purchase,
          custom_previous_last_month_purchase: item.custom_previous_last_month_purchase,
          custom_current_month_purchase: item.custom_current_month_purchase,
          custom_average_sales_last_3_months: avg_sales,
          custom_average_purchase_last_3_months: avg_purchase
        });

        html += `<tr class="text-center align-middle">
          <td><strong>${item.item_code}</strong></td>
          <td>${item.custom_available_qty?.split(" / ")[0] ?? "-"}</td>
          <td>${item.custom_available_qty?.split(" / ")[1] ?? "-"}</td>
          <td>${item.custom_mrp ?? "-"}</td>
          <td>${item.custom_tax ?? "-"}</td>
          <td>${item.custom_current_month_sales_2 ?? "-"}</td>
          <td>${item.custom_last_month_sales ?? "-"}</td>
          <td>${item.custom_previous_last_month_sales ?? "-"}</td>
          <td>${item.custom_current_month_purchase ?? "-"}</td>
          <td>${item.custom_last_month_purchase ?? "-"}</td>
          <td>${item.custom_previous_last_month_purchase ?? "-"}</td>
          <td><span class="badge bg-success fs-6">${avg_sales.toFixed(2)}</span></td>
          <td><span class="badge bg-warning text-dark fs-6">${avg_purchase.toFixed(2)}</span></td>
        </tr>`;
      });

      html += "</tbody></table></div>";
      frm.refresh_field("items");
      frm.fields_dict.supplier_item_table.$wrapper.html(html);
    }
  });
}
function purchaseqtycal(frm) {}
