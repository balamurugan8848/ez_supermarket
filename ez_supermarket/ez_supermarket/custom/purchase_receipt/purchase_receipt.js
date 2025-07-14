// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Receipt", {
  refresh: function (frm) {
    frm.fields_dict["items"].grid.get_field("item_location").get_query =
      function (doc, cdt, cdn) {
        var child = locals[cdt][cdn];
        return {
          filters: { warehouse: child.warehouse || frm.doc.set_warehouse },
        };
      };
    if (
      frappe.user.has_role("PTPS_EXECUTIVE_1") ||
      frappe.user.has_role("PTPS_EXECUTIVE_2")
    ) {
      // if (frm.doc.docstatus === 0 && frm.doc.workflow_state == "Update Price") {
      frm.fields_dict.items.grid.add_custom_button(
        __("Update Price"),
        function () {
          showItemDialog(frm);
        }
      );
    }
  },
  before_submit: function (frm) {
    const pr_name = frm.doc.name;

    if (!pr_name) {
      console.log("No Purchase Receipt name found");
      return;
    }

    console.log("PR Name:", pr_name);

    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.custom.purchase_receipt.purchase_receipt.update_item_lead_time",
      args: { pr_name: pr_name },
      callback: function (r) {
        console.log("Function response:", r);
        if (r.message) {
          frappe.show_alert(
            {
              message: __(r.message),
              indicator: "blue",
            },
            3
          );
        } else {
          console.log("No message in response");
        }
      },
    });
  },
  validate: function (frm) {
    $.each(frm.doc.items || [], function (i, d) {
      if (d.custom_mrp > 0 && d.custom_selling_price > d.custom_mrp) {
        frappe.validated = false;
        frappe.msgprint(
          "Row " +
            (i + 1) +
            ": Selling price cannot exceed MRP for item " +
            d.item_code
        );
      }
    });
  },
});

function showItemDialog(frm) {
  // Fetch items from the Purchase Order
  var items = frm.doc.items || [];

  // Index to keep track of the current item being displayed
  var currentIndex = 0;

  function updateDialogContent() {
    var dialog = new frappe.ui.Dialog({
      title: __("Update Prices"),
      size: "large",
      fields: [
        {
          fieldname: "item_code",
          label: "Item Code",
          fieldtype: "Data",
          reqd: 1,
          default: frm.doc.items[currentIndex].item_code,
          read_only: 1,
        },
        {
          fieldname: "received_qty",
          label: "Received",
          fieldtype: "Float",
          reqd: 1,
          default: frm.doc.items[currentIndex].qty,
        },
        {
          fieldname: "date_received",
          label: "Date Received",
          fieldtype: "Date",
          default: "Today",
        },
        {
          fieldname: "margin",
          label: "Margin",
          fieldtype: "Currency",
          onchange: function () {
            calculateSellingPrice(dialog);
          },
        },
        {
          fieldname: "column_break234",
          fieldtype: "Column Break",
        },
        {
          fieldname: "buying_price",
          label: "Buying Rate",
          fieldtype: "Currency",
          reqd: 1,
          default: frm.doc.items[currentIndex].rate,
          onchange: function () {
            calculateSellingPrice(dialog);
          },
        },
        {
          fieldtype: "Check",
          fieldname: "update_mrp",
          label: "Update MRP",
          onchange: function () {
            dialog.set_df_property(
              "mrp",
              "read_only",
              !dialog.get_value("update_mrp")
            );
          },
        },
        {
          fieldname: "mrp",
          label: "MRP",
          fieldtype: "Currency",
          default: frm.doc.items[currentIndex].custom_mrp,
          description: "MRP will be updated if you change it here",
          read_only: function () {
            return !dialog.get_value("update_mrp");
          },
        },
        {
          fieldname: "calculate_mrp",
          label: "Calculate MRP",
          fieldtype: "Button",
          click: function () {
            var buying_price = dialog.get_value("buying_price");
            var tax_rate = dialog.get_value("tax_rate");
            var margin = 0.35; // 35%

            // Calculate MRP
            var mrp =
              buying_price +
              buying_price * margin +
              (buying_price * tax_rate) / 100;

            // Update the MRP field
            dialog.set_value("mrp", mrp);
          },
        },
        {
          fieldname: "selling_price_wo_taxes",
          label: "Selling Price without Taxes",
          fieldtype: "Currency",
          read_only: 1,
        },
        {
          fieldname: "selling_price_with_taxes",
          label: "Selling Price with Taxes",
          fieldtype: "Currency",
          read_only: 1,
        },
        {
          fieldname: "tax_rate",
          label: "Tax %",
          fieldtype: "Data",
          read_only: 1,
          default: frm.doc.items[currentIndex].custom_tax,
        },

        {
          fieldname: "original_rate",
          label: "Original Rate",
          fieldtype: "Currency",
          default: frm.doc.items[currentIndex].rate,
          read_only: 1,
          hidden: 1,
        },
        {
          fieldname: "discount_amount",
          label: "Discount Rate",
          fieldtype: "Currency",
          hidden: 1,
        },
        {
          fieldname: "discount_percentage",
          label: "Discount Percentage",
          fieldtype: "Currency",
          hidden: 1,
        },
      ],
      primary_action: function () {
        var values = dialog.get_values();

        if (values.update_mrp) {
          // Update the custom_mrp field in the current item
          frm.doc.items[currentIndex].custom_mrp = values.mrp;
        }
        // Update the current item with the new values
        frm.doc.items[currentIndex].item_code = values.item_code;
        frm.doc.items[currentIndex].qty = values.received_qty;
        frm.doc.items[currentIndex].rate = values.buying_price;
        frm.doc.items[currentIndex].amount =
          values.buying_price * frm.doc.items[currentIndex].qty;
        frm.doc.items[currentIndex].custom_margin = values.margin;
        frm.doc.items[currentIndex].custom_selling_price =
          values.selling_price_wo_taxes;

        // Refresh the grid to reflect the changes
        frm.fields_dict["items"].grid.refresh();

        // Mark the form as clean
        frm.dirty(false);

        // Increment the index for the next item
        currentIndex++;

        // Check if there are more items to display
        if (currentIndex < items.length) {
          // If yes, update the dialog content again
          dialog.set_values({
            item_code: frm.doc.items[currentIndex].item_code,
            received_qty: frm.doc.items[currentIndex].qty,
            mrp: frm.doc.items[currentIndex].custom_mrp,
            buying_price: frm.doc.items[currentIndex].rate,
            margin: "",
            tax_rate: frm.doc.items[currentIndex].custom_tax,
            selling_price_wo_taxes: "",
            selling_price_with_taxes: "",
            original_rate: frm.doc.items[currentIndex].rate,
            discount_amount: "",
            discount_percentage: "",
          });
        } else {
          // If no more items, close the dialog or perform any other actions
          dialog.hide();
          frappe.msgprint("Prices updated successfully");
        }
      },

      primary_action_label: __("Update"),
    });
    // Show the dialog
    dialog.show();
  }
  // Start the dialog with the first item
  if (items.length > 0) {
    updateDialogContent();
  } else {
    frappe.msgprint("No items to update");
  }
}

function calculateSellingPrice(dialog) {
  var buying_price = dialog.get_value("buying_price") || 0;
  var margin_percent = dialog.get_value("margin") || 0;
  var tax_rate = dialog.get_value("tax_rate") || 0;
  var original_rate = dialog.get_value("original_rate") || 0;

  console.log("buying_price:", buying_price);
  console.log("margin_percent:", margin_percent);
  console.log("tax_rate:", tax_rate);
  console.log("original_rate:", original_rate);

  var selling_price_wo_taxes = (
    buying_price *
    (1 + margin_percent / 100)
  ).toFixed(2);
  var selling_price_with_taxes = (
    selling_price_wo_taxes *
    (1 + tax_rate / 100)
  ).toFixed(2);

  var discount_amount = original_rate - buying_price;
  var discount_percentage = (discount_amount / original_rate) * 100;

  // Add console log to check discount_amount
  console.log("discount_amount:", discount_amount);

  dialog.set_value("selling_price_wo_taxes", selling_price_wo_taxes);
  dialog.set_value("selling_price_with_taxes", selling_price_with_taxes);
  dialog.set_value("discount_amount", discount_amount);
  dialog.set_value("discount_percentage", discount_percentage);
}

frappe.ui.form.on("Purchase Receipt Item", {
  custom_margin: function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    calSellingPrice(row);
  },

  rate: function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    calSellingPrice(row);
  },

  custom_selling_price: function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var mrp = row.custom_mrp || 0;
    var sellingPrice = row.custom_selling_price || 0;

    if (mrp > 0 && sellingPrice > mrp) {
      frappe.msgprint(
        "Selling price cannot exceed MRP for item " + row.item_code
      );
      frappe.model.set_value(cdt, cdn, "custom_selling_price", mrp);
      frappe.model.set_value(cdt, cdn, "custom_margin", 0); // Set margin to 0
    }

    calculateSellingPrice(row); // Call calculateSellingPrice after custom_selling_price is updated
  },
});

function calSellingPrice(row) {
  var buying_price = row.rate || 0;
  var margin_percent = row.custom_margin || 0;

  var selling_price_wo_taxes = (
    buying_price *
    (1 + margin_percent / 100)
  ).toFixed(2);

  row.custom_selling_price = selling_price_wo_taxes;

  // Check if selling price exceeds MRP after setting margin
  var mrp = row.custom_mrp || 0;
  var sellingPrice = row.custom_selling_price || 0;

  if (mrp > 0 && sellingPrice > mrp) {
    frappe.msgprint(
      "Selling price cannot exceed MRP for item " + row.item_code
    );
    row.custom_selling_price = mrp;
    row.custom_margin = 0; // Set margin to 0
  }

  cur_frm.fields_dict["items"].grid.refresh();
}

frappe.ui.form.on("Purchase Receipt Item", {
  item_code: function (frm, cdt, cdn) {
    var child = locals[cdt][cdn];
    var warehouse = child.set_warehouse || child.warehouse; // Use set_warehouse from parent if provided, otherwise use warehouse from child table
    // var custom_mrp = child.custom_mrp; // Assuming custom_mrp is defined in the child table

    console.log("Fetching item details for:", child.item_code);

    frappe.call({
      method:
        "ez_supermarket.ez_supermarket.custom.purchase_receipt.purchase_receipt.fetch_item_details",
      args: {
        item_code: child.item_code,
        set_warehouse: warehouse,
        warehouse: warehouse,
        // custom_mrp: custom_mrp,
      },
      callback: function (r) {
        if (r.message) {
          console.log("Received item details:", r.message);
          frappe.model.set_value(cdt, cdn, "warehouse", r.message.warehouse);
          // frappe.model.set_value(cdt, cdn, "custom_mrp", r.message.custom_mrp);
          frappe.model.set_value(
            cdt,
            cdn,
            "item_location",
            r.message.item_location
          );
        }
      },
    });
  },
});
