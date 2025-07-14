// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Order", {
  custom_suppliers_bill_no: function (frm) {
    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.custom.purchase_order.purchase_order.check_supplier_bill_no",
      args: {
        supplier: frm.doc.supplier,
        custom_suppliers_bill_no: frm.doc.custom_suppliers_bill_no,
      },
      callback: function (r) {
        if (r.message && r.message.existing_po) {
          let poLink = frappe.utils.get_form_link(
            "Purchase Order",
            r.message.existing_po
          );
          let errorMessage = `Supplier Bill Number '<b>${frm.doc.custom_suppliers_bill_no}</b>' already exists in a previous Purchase Order. <a href="${poLink}" target="_blank"><b>${r.message.existing_po}<b></a>`;

          frappe.msgprint({
            title: __("Duplicate Supplier Bill Number"),
            indicator: "red",
            message: errorMessage,
          });

          frappe.validated = false;
        }
      },
    });
  },
  refresh: function (frm) {
    if (frm.doc.docstatus == 1) {
      frm.page.add_inner_button(
        __("Intiate Quality Check"),

        () => {
          const doc_name = frm.docname;
          const doc_type = frm.doctype;

          frappe.call({
            method:
              "ez_supermarket.ez_supermarket.doctype.quality_check.quality_check.generate_quality_check",
            args: {
              doc_name: doc_name,
              doc_type: doc_type,
            },
            callback: (r) => {
              frappe.set_route("Form", "Quality Check", r.message);
            },
          });
        },
        __("Create")
      );
    }
    frm.fields_dict.items.grid.add_custom_button(
      __("Fetch Supplier Items"),
      function () {
        fetchSupplierItems(frm);
      }
    );
    frm.add_custom_button(__("Check Prices"), function () {
      checkPrices(frm);
    });
  },
});
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
  var schedule_date = frappe.datetime.add_days(frm.doc.schedule_date, 12);
  frm.set_value("schedule_date", schedule_date);

  // Call the server-side function to fetch supplier items
  frappe.call({
    method:
      "ez_supermarket.ez_supermarket.custom.purchase_order.purchase_order.fetch_supplier_items",
    args: {
      supplier: frm.doc.supplier,
    },
    callback: function (r) {
      if (r.message && r.message.length > 0) {
        // Clear existing rows
        frm.doc.items = [];

        // Add fetched items
        $.each(r.message, function (i, item) {
          var child = frm.add_child("items");
          child.item_code = item.item_code;

          // Trigger the item_code event asynchronously
          triggerItemCode(child).catch((error) => {});
          // Assuming `item` is the object you're working with
          var last_month_sales_qty = item.custom_last_month_sales
            ? parseFloat(item.custom_last_month_sales.split(" / ")[0])
            : 0;
          var previous_last_month_sales_qty =
            item.custom_previous_last_month_sales
              ? parseFloat(
                  item.custom_previous_last_month_sales.split(" / ")[0]
                )
              : 0;
          var current_month_sales_qty = item.custom_current_month_sales_2
            ? parseFloat(item.custom_current_month_sales_2.split(" / ")[0])
            : 0;

          var last_month_purchase_qty = item.custom_last_month_purchase
            ? parseFloat(item.custom_last_month_purchase.split(" / ")[0])
            : 0;
          var previous_last_month_purchase_qty =
            item.custom_previous_last_month_purchase
              ? parseFloat(
                  item.custom_previous_last_month_purchase.split(" / ")[0]
                )
              : 0;
          var current_month_purchase_qty = item.custom_current_month_purchase
            ? parseFloat(item.custom_current_month_purchase.split(" / ")[0])
            : 0;

          child.buying_price_list = frm.doc.buying_price_list;
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
            (last_month_sales_qty +
              previous_last_month_sales_qty +
              current_month_sales_qty) /
            3;

          child.custom_average_purchase_last_3_months =
            (current_month_purchase_qty +
              last_month_purchase_qty +
              previous_last_month_purchase_qty) /
            3;

          // Calculate and set custom_forecasted_sales and custom_forecasted_purchase using exponential smoothing
          var alpha = 0.2; // Define the smoothing factor
          child.custom_forecasted_sales_quantity =
            calculate_exponential_smoothing(
              current_month_sales_qty,
              last_month_sales_qty,
              alpha // Pass the smoothing factor to the function
            );

          child.custom_forecasted_purchase_quantity =
            calculate_exponential_smoothing(
              current_month_purchase_qty,
              last_month_purchase_qty,
              alpha // Pass the smoothing factor to the function
            );
        });

        frm.refresh_field("buying_price_list");
        frm.refresh_field("items");
      } else {
        frappe.msgprint("No items found for supplier.");
      }
    },
  });
}
function triggerItemCode(child) {
  return new Promise((resolve, reject) => {
    try {
      cur_frm.script_manager.trigger("item_code", child.doctype, child.name);
      resolve();
    } catch (error) {
      reject(error);
    }
  });
}

function calculate_exponential_smoothing(yt, st_minus_1, alpha) {
  // Calculate the forecast using exponential smoothing
  const forecast = alpha * yt + (1 - alpha) * st_minus_1;

  return forecast;
}
