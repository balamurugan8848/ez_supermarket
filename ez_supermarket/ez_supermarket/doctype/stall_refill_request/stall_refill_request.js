// Copyright (c) 2024, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stall Refill Request", {
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
        if (settings_doc.stall_refill_request == 0) {
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
            "You must enable <strong>Stall Refill Request</strong> feature in <a href='" +
              settings_link +
              "'><strong>Yb Supermarket Settings</a></strong> to access this page."
          );
        }
      }
    );
    // Add Supplierwise item function
    frm.add_custom_button("Fetch Items Sold", () => {
      frm.set_value("request_raised_by", frappe.session.user);
      console.log("Button clicked"); // Log that the button was clicked

      // Stringify the doc
      let doc_str = JSON.stringify(frm.doc);

      frappe.call({
        method:
          "ez_supermarket.ez_supermarket.doctype.stall_refill_request.stall_refill_request.set_timestamps",
        args: { doc_str: doc_str }, // Pass stringified doc
        callback: function (r) {
          console.log("Callback received", r); // Log the callback response
          if (r.message) {
            let updatedDoc = r.message;

            // Explicitly set values in the form
            frm.set_value("timestamp", updatedDoc.timestamp);
            frm.set_value(
              "last_fetch_timestamp",
              updatedDoc.last_fetch_timestamp
            );

            // Refresh the form to reflect the changes
            frm.refresh();

            fetch_items_sold(frm);
          }
        },
      });
    });
    filterChildTable(frm);
    if (frm.doc.docstatus === 1)
      frm.add_custom_button("Send The Item", () => {
        var doc = frappe.model.get_new_doc("Stock Entry");

        // Set the fields of the document as required
        doc.stock_entry_type = "Item Transfer to Stall";
        (doc.naming_series = "MAT-STE-.YYYY.-"),
          (doc.posting_date = frm.doc.posting_date);
        doc.posting_time = frm.doc.posting_time;
        doc.custom_document_type = "Stall Refill Request";
        doc.custom_reference_document = frm.doc.name;

        $.each(frm.doc.stall_request_details, function (i, d) {
          var child = frappe.model.add_child(
            doc,
            "Stock Entry Detail",
            "items"
          );
          child.item_code = d.item_code;
          child.qty = d.qty_sold;
          // child.s_warehouse = "Store - PTPS"; // Ensure this is set
          // child.t_warehouse = "Stall - PTPS";
          child.uom = d.uom;
          child.stock_uom = d.uom;
          child.valuation_rate = d.valuation_rate;
          child.allow_zero_valuation_rate = 1;
        });

        // Navigate to the new unsaved document
        frappe.set_route("Form", "Stock Entry", doc.name);
      });
    function fetch_items_sold(frm) {
      let posting_date = frm.doc.posting_date;
      let timestamp = frm.doc.timestamp;
      let last_fetch_ts = frm.doc.last_fetch_timestamp;

      frappe.call({
        method:
          "ez_supermarket.ez_supermarket.doctype.stall_refill_request.stall_refill_request.fetch_items_sold",
        args: {
          posting_date: posting_date,
          timestamp: timestamp,
          last_fetch_ts: last_fetch_ts,
        },
        callback: function (r) {
          if (r.message) {
            frm.doc.stall_request_details = [];
            for (var i = 0; i < r.message.length; i++) {
              var d = frm.add_child("stall_request_details");
              d.item_code = r.message[i].item_code;
              d.item_name = r.message[i].item_name;
              d.uom = r.message[i].stock_uom;
              d.qty_sold = r.message[i].qty_sold;
              d.stall_location = r.message[i].stall_location;
              d.store_location = r.message[i].store_location;
              d.max_qty = r.message[i].max_qty;
              d.store_warehouse = r.message[i].store_warehouse;
              d.stall_warehouse = r.message[i].stall_warehouse;
              d.refill_qty = r.message[i].max_qty - r.message[i].qty_sold;
            }
            frm.refresh_field("stall_request_details");
          }
        },
      });
    }
    // Filter child table function
    function filterChildTable(frm) {
      const warehouseSettingsName = "Yb Supermarket Settings";

      // Fetch warehouse settings doc
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Yb Supermarket Settings",
          name: warehouseSettingsName,
        },
        callback: function (response) {
          if (response.message) {
            const warehouseKeepers = response.message.warehouse_keeper;
            const warehouseMap = {};

            warehouseKeepers.forEach((row) => {
              warehouseMap[row.role] = row.warehouse;
            });

            console.log("Warehouse Map:", warehouseMap); // Log warehouse roles

            // Get user roles
            const userRoles = frappe.user_roles.filter(
              (role) => warehouseMap[role]
            );
            console.log("User Roles:", userRoles); // Log user roles

            // Get user warehouses
            const userWarehouses = userRoles.map((role) => warehouseMap[role]);

            // Filter rows based on user's warehouses
            const filteredRows = frm.doc.stall_request_details.filter((row) => {
              return userWarehouses.includes(row.store_warehouse);
            });

            // Update child table with filtered rows
            frm.fields_dict.stall_request_details.grid.get_field(
              "store_warehouse"
            ).get_query = function (doc, cdt, cdn) {
              return {
                filters: {
                  warehouse: userWarehouses,
                },
              };
            };

            // Update child table with filtered rows
            frm.fields_dict.stall_request_details.grid.df.options =
              userWarehouses;
            frm.doc.stall_request_details = filteredRows;
            frm.refresh_field("stall_request_details");
          }
        },
      });
    }
  },
});
