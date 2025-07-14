// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.accounts");

erpnext.accounts.payment_triggers.setup("Purchase Invoice");
erpnext.accounts.taxes.setup_tax_filters("Purchase Taxes and Charges");
erpnext.accounts.taxes.setup_tax_validations("Procurement Master");
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

frappe.ui.form.on("Procurement Master", {
  refresh: function (frm) {
    frm.fields_dict.items.grid.add_custom_button(
      __("Fetch Supplier Items"),
      function () {
        fetchSupplierItems(frm);
      }
    );
    frm.add_custom_button(__("Check Prices"), function () {
      checkPrices(frm);
    });
    if (frm.doc.workflow_state == "QC Pending") {
      frm.set_value("qc_posting_date", frappe.datetime.get_today());
      frm.script_manager.trigger("qc_posting_date", frm.doctype, frm.docname);
      transferToItemDetails(frm);
    }
  },
  tax_category: function (frm) {
    if (frm.doc.tax_category) {
      frm.events.set_taxes_and_charges(frm);
    }
  },
  set_taxes_and_charges: function (frm) {
    if (frm.doc.tax_category == "In-State") {
      frm.set_value("taxes_and_charges", "Input GST In-state - PTPS");
    } else if (frm.doc.tax_category == "Out-State") {
      frm.set_value("taxes_and_charges", "Input GST Out-state - PTPS");
    }

    refresh_field("taxes_and_charges");
  },
});
function transferToItemDetails(frm) {
  var items = frm.doc.items || [];
  var itemDetails = frm.doc.item_details || [];

  // Only transfer values if item_details is empty
  if (itemDetails.length === 0) {
    // Clear existing rows in item_details
    frm.clear_table("item_details");

    // Transfer values from items to item_details
    $.each(items, function (i, item) {
      var child = frm.add_child("item_details");
      child.item_code = item.item_code;
      child.uom = item.uom;
      child.rate = item.rate;
      child.total_qty = item.qty;
      // Add other fields as needed
    });

    frm.refresh_field("item_details");
  }
}

function checkPrices(frm) {
  var items = frm.doc.items || [];
  var rows = [];

  function getNextItem(index) {
    if (index < items.length) {
      getPreviousPurchaseDetails(items[index], rows, function () {
        getNextItem(index + 1);
      });
    } else {
      showPurchaseDetailsDialog(rows);
    }
  }

  getNextItem(0);
}

function getPreviousPurchaseDetails(item, rows, callback) {
  frappe.call({
    method:
      "ez_supermarket.ez_supermarket.custom.purchase_order.purchase_order.get_previous_purchase_details",
    args: {
      item_code: item.item_code,
      rate: item.rate,
      base_rate: item.base_rate,
    },
    callback: function (response) {
      if (response.message && response.message.rate < item.rate) {
        rows.push({
          item_code: item.item_code,
          supplier: response.message.supplier,
          date: response.message.date,
          rate: response.message.rate,
        });
      }
      callback();
    },
  });
}

function showPurchaseDetailsDialog(rows) {
  frappe.prompt(
    [
      {
        label: __("Previous Purchase Details"),
        fieldname: "table",
        fieldtype: "Table",
        options: "Purchase Order Item",
        fields: [
          {
            label: __("Item Code"),
            fieldname: "item_code",
            fieldtype: "Data",
            in_list_view: 1,
          },
          {
            label: __("Supplier"),
            fieldname: "supplier",
            fieldtype: "Data",
            in_list_view: 1,
          },
          {
            label: __("Transaction Date"),
            fieldname: "date",
            fieldtype: "Data",
            in_list_view: 1,
          },
          {
            label: __("Rate"),
            fieldname: "rate",
            fieldtype: "Currency",
            in_list_view: 1,
          },
        ],
        data: rows,
      },
    ],
    function (values) {},
    __("Are you sure? Because i found these Suppliers with Low Price.!"),
    "Submit"
  );
}
// Function to fetch supplier items
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
          var alpha = 0.2; // Define the smoothing factor
          child.custom_forecasted_sales_quantity =
            calculate_exponential_smoothing(
              item.custom_current_month_sales_2,
              item.custom_last_month_sales,
              alpha // Pass the smoothing factor to the function
            );

          child.custom_forecasted_purchase_quantity =
            calculate_exponential_smoothing(
              item.custom_current_month_purchase,
              item.custom_last_month_purchase,
              alpha // Pass the smoothing factor to the function
            );
        });

        // frm.refresh_field("buying_price_list");
        frm.refresh_field("items");
      } else {
        frappe.msgprint("No items found for supplier.");
      }
    },
  });
}

function calculate_exponential_smoothing(yt, st_minus_1, alpha) {
  console.log("yt:", yt);
  console.log("st_minus_1:", st_minus_1);
  console.log("alpha:", alpha);
  // Calculate the forecast using exponential smoothing
  const forecast = alpha * yt + (1 - alpha) * st_minus_1;

  return forecast;
}

frappe.ui.form.on("PM Accepted Items", {
  manufacturing_date: (frm, cdt, cdn) => {
    const doc = locals[cdt][cdn];

    frappe.call({
      method:
        "ceba_utilities.ceba_utilities.doctype.qc_template.qc_template.update_batch_expiry_date",
      args: {
        item_code: doc.item_code,
        manufacturing_date: doc.manufacturing_date,
      },
      callback: (r) => {
        frappe.model.set_value(cdt, cdn, "expiry_date", r.message);
      },
    });
  },
  shelf_batch_no: (frm, cdt, cdn) => {
    const doc = locals[cdt][cdn];

    if (doc.shelf_batch_no) {
      frappe.model.set_value(cdt, cdn, "supplier_batch_no", null);
    }
  },
  supplier_batch_no: (frm, cdt, cdn) => {
    const doc = locals[cdt][cdn];

    if (doc.supplier_batch_no) {
      frappe.model.set_value(cdt, cdn, "shelf_batch_no", null);
    }
  },
  accepted_qty: (frm, cdt, cdn) => {
    const doc = locals[cdt][cdn];

    if (doc.accepted_qty < 0 || doc.accepted_qty > doc.received_qty) {
      const new_accepted_qty = doc.received_qty - doc.rejected_qty;
      frappe.model.set_value(cdt, cdn, "accepted_qty", new_accepted_qty);
    }
    const new_rejected_qty = doc.received_qty - doc.accepted_qty;
    if (new_rejected_qty || new_rejected_qty == 0) {
      frappe.model.set_value(cdt, cdn, "rejected_qty", new_rejected_qty);
    }
    setStatusVal(frm);
  },
  rejected_qty: (frm, cdt, cdn) => {
    const doc = locals[cdt][cdn];

    if (doc.rejected_qty < 0 || doc.rejected_qty > doc.received_qty) {
      const new_rejected_qty = doc.received_qty - doc.accepted_qty;
      frappe.model.set_value(cdt, cdn, "rejected_qty", new_rejected_qty);
    }
    const new_accepted_qty = doc.received_qty - doc.rejected_qty;
    if (new_accepted_qty || new_accepted_qty == 0) {
      frappe.model.set_value(cdt, cdn, "accepted_qty", new_accepted_qty);
    }
    setStatusVal(frm);
  },
  received_qty: (frm, cdt, cdn) => {
    const doc = locals[cdt][cdn];

    if (doc.received_qty < 0 || doc.received_qty > doc.total_qty) {
      const new_received_qty = doc.accepted_qty + doc.rejected_qty;
      frappe.model.set_value(cdt, cdn, "received_qty", new_received_qty);
    } else {
      frappe.model.set_value(cdt, cdn, "accepted_qty", doc.received_qty);
      frappe.model.set_value(cdt, cdn, "rejected_qty", 0);
    }
    setStatusVal(frm);
  },
});

function setStatusVal(frm) {
  let accepted = 0;
  let rejected = 0;

  frm.doc.item_details.forEach((row) => {
    accepted += row.accepted_qty;
    rejected += row.rejected_qty;
  });

  if (accepted == 0) {
    frm.set_value("qc_status", "Rejected");
    frm.toggle_reqd("rejected_warehouse", true);
  } else if (rejected == 0) {
    frm.set_value("qc_status", "Accepted");
    frm.toggle_reqd("rejected_warehouse", false);
  } else {
    frm.set_value("qc_status", "Partially Accepted");
    frm.toggle_reqd("rejected_warehouse", true);
  }

  refresh_field("qc_status");
}
