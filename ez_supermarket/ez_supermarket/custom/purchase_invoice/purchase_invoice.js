// // Copyright (c) 2023, Balamurugan and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Purchase Invoice", {
//   refresh: function (frm) {
//     if (
//       frappe.user.has_role("PTPS_EXECUTIVE_1") ||
//       frappe.user.has_role("PTPS_EXECUTIVE_2")
//     ) {
//       // if (frm.doc.docstatus === 0 && frm.doc.workflow_state == "Update Price") {
//       frm.fields_dict.items.grid.add_custom_button(
//         __("Update Price"),
//         function () {
//           showItemDialog(frm);
//         }
//       );
//     }
//   },
// });

// function showItemDialog(frm) {
//   // Fetch items from the Purchase Order
//   var items = frm.doc.items || [];

//   // Index to keep track of the current item being displayed
//   var currentIndex = 0;

//   function updateDialogContent() {
//     var dialog = new frappe.ui.Dialog({
//       title: __("Update Prices"),
//       size: "large",
//       fields: [
//         {
//           fieldname: "item_code",
//           label: "Item Code",
//           fieldtype: "Data",
//           reqd: 1,
//           default: frm.doc.items[currentIndex].item_code,
//           read_only: 1,
//         },
//         {
//           fieldname: "received_qty",
//           label: "Received",
//           fieldtype: "Float",
//           reqd: 1,
//           default: frm.doc.items[currentIndex].qty,
//         },
//         {
//           fieldname: "date_received",
//           label: "Date Received",
//           fieldtype: "Date",
//           default: "Today",
//         },
//         {
//           fieldname: "margin",
//           label: "Margin",
//           fieldtype: "Currency",
//           onchange: function () {
//             calculateSellingPrice(dialog);
//           },
//         },
//         {
//           fieldname: "column_break234",
//           fieldtype: "Column Break",
//         },
//         {
//           fieldname: "buying_price",
//           label: "Buying Rate",
//           fieldtype: "Currency",
//           reqd: 1,
//           default: frm.doc.items[currentIndex].rate,
//           onchange: function () {
//             calculateSellingPrice(dialog);
//           },
//         },
//         {
//           fieldname: "selling_price_wo_taxes",
//           label: "Selling Price without Taxes",
//           fieldtype: "Currency",
//           read_only: 1,
//         },
//         {
//           fieldname: "selling_price_with_taxes",
//           label: "Selling Price with Taxes",
//           fieldtype: "Currency",
//           read_only: 1,
//         },
//         {
//           fieldname: "tax_rate",
//           label: "Tax %",
//           fieldtype: "Data",
//           read_only: 1,
//           default: frm.doc.items[currentIndex].custom_tax,
//         },

//         {
//           fieldname: "original_rate",
//           label: "Original Rate",
//           fieldtype: "Currency",
//           default: frm.doc.items[currentIndex].rate,
//           read_only: 1,
//           hidden: 1,
//         },
//         {
//           fieldname: "discount_amount",
//           label: "Discount Rate",
//           fieldtype: "Currency",
//           hidden: 1,
//         },
//         {
//           fieldname: "discount_percentage",
//           label: "Discount Percentage",
//           fieldtype: "Currency",
//           hidden: 1,
//         },
//       ],
//       primary_action: function () {
//         var values = dialog.get_values();

//         // Update the current item with the new values
//         frm.doc.items[currentIndex].item_code = values.item_code;
//         frm.doc.items[currentIndex].qty = values.received_qty;
//         frm.doc.items[currentIndex].rate = values.buying_price;
//         frm.doc.items[currentIndex].amount =
//           values.buying_price * frm.doc.items[currentIndex].qty;
//         frm.doc.items[currentIndex].custom_margin = values.margin;
//         frm.doc.items[currentIndex].custom_selling_price =
//           values.selling_price_wo_taxes;

//         frm.fields_dict["items"].grid.refresh();

//         // Increment the index for the next item
//         currentIndex++;

//         // Check if there are more items to display
//         if (currentIndex < items.length) {
//           // If yes, update the dialog content again
//           dialog.set_values({
//             item_code: frm.doc.items[currentIndex].item_code,
//             mrp_rate: frm.doc.items[currentIndex].custom_mrp,
//             buying_price: frm.doc.items[currentIndex].rate,
//             margin: "",
//             tax_rate: frm.doc.items[currentIndex].custom_tax,
//             selling_price_wo_taxes: "",
//             selling_price_with_taxes: "",
//             original_rate: frm.doc.items[currentIndex].rate,
//             discount_amount: "",
//             discount_percentage: "",
//           });
//         } else {
//           // If no more items, close the dialog or perform any other actions
//           dialog.hide();
//           frappe.msgprint("Prices updated successfully");
//         }
//       },
//       primary_action_label: __("Update"),
//     });
//     // Show the dialog
//     dialog.show();
//   }
//   // Start the dialog with the first item
//   if (items.length > 0) {
//     updateDialogContent();
//   } else {
//     frappe.msgprint("No items to update");
//   }
// }

// function calculateSellingPrice(dialog) {
//   var buying_price = dialog.get_value("buying_price") || 0;
//   var margin_percent = dialog.get_value("margin") || 0;
//   var tax_rate = dialog.get_value("tax_rate") || 0;
//   var original_rate = dialog.get_value("original_rate") || 0;

//   console.log("buying_price:", buying_price);
//   console.log("margin_percent:", margin_percent);
//   console.log("tax_rate:", tax_rate);
//   console.log("original_rate:", original_rate);

//   var selling_price_wo_taxes = (
//     buying_price *
//     (1 + margin_percent / 100)
//   ).toFixed(2);
//   var selling_price_with_taxes = (
//     selling_price_wo_taxes *
//     (1 + tax_rate / 100)
//   ).toFixed(2);

//   var discount_amount = original_rate - buying_price;
//   var discount_percentage = (discount_amount / original_rate) * 100;

//   // Add console log to check discount_amount
//   console.log("discount_amount:", discount_amount);

//   dialog.set_value("selling_price_wo_taxes", selling_price_wo_taxes);
//   dialog.set_value("selling_price_with_taxes", selling_price_with_taxes);
//   dialog.set_value("discount_amount", discount_amount);
//   dialog.set_value("discount_percentage", discount_percentage);
// }

// frappe.ui.form.on("Purchase Invoice Item", {
//   custom_margin: function (frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     calSellingPrice(row);
//   },

//   rate: function (frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     calSellingPrice(row);
//   },
// });

// function calSellingPrice(row) {
//   var buying_price = row.rate || 0;
//   var margin_percent = row.custom_margin || 0;

//   var selling_price_wo_taxes = (
//     buying_price *
//     (1 + margin_percent / 100)
//   ).toFixed(2);

//   row.custom_selling_price = selling_price_wo_taxes;

//   cur_frm.fields_dict["items"].grid.refresh();
// }
