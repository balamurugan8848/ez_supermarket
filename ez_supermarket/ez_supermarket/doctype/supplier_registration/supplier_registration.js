// Copyright (c) 2024, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier Registration", {
  validate: function (frm) {
    // Use validate instead of before_save
    var gstin = frm.doc.gstin;
    var pan = frm.doc.pan;
    var gstholder = frm.doc.gst_holder;

    if (gstholder === "Yes") {
      frappe.call({
        method:
          "ceba_utilities.ceba_utilities.doctype.supplier_registration.supplier_registration.validate_gstin",
        args: {
          gstin: gstin,
          pan: pan,
          docname: frm.docname,
          from_validate: true, // Pass true as a flag value
        },
        callback: function (r) {
          if (!r.message.valid) {
            frappe.msgprint(r.message.message); // Display the correct error message
            frappe.validated = false; // Prevent form submission
          }
        },
      });
    }
  },
  gstin: function (frm) {
    var gstin = frm.doc.gstin;
    if (gstin && gstin.length >= 15) {
      // Assuming GSTIN has a length of 15
      var pan = gstin.substring(2, 12); // Extract PAN from GSTIN

      // Call the gstin_validation function
      frm.call("gstin_validation");
    }
  },
  pan: function (frm) {
    var pan = frm.doc.pan;
    if (pan) {
      // Make the API call to validate PAN
      frappe.call({
        method:
          "ceba_utilities.ceba_utilities.doctype.supplier_registration.supplier_registration.validate_pan",
        args: {
          pan: pan,
        },
        callback: function (r) {
          if (!r.message) {
            // If the function returns False
            frappe.msgprint("Invalid PAN format"); // Display the error message
            frappe.validated = false; // Prevent form submission
          }
        },
      });
    }
  },
  pan: function (frm) {},
  refresh: function (frm) {
    if (frm.doc.workflow_state === "Approved") {
      frm.add_custom_button(
        __("Approve the Supplier"),
        function () {
          frappe.call({
            method:
              "ceba_utilities.ceba_utilities.doctype.supplier_registration.supplier_registration.create_supplier_from_registration",
            args: {
              supplier_registration: frm.doc.name,
            },
            callback: function (response) {
              if (!response.exc) {
                frm.set_value("status", "Approved");
                // Show the "Supplier Created" message with green background
                frappe.msgprint({
                  message: __(
                    "Supplier has been created with the details from Supplier Registration. Supplier Name: {0}",
                    [response.message.supplier_name]
                  ),
                  indicator: "green",
                });
                frm.save();

                frm.reload_doc(); // Refresh the form to show the updated supplier information

                frm.refresh_fields();
              }
            },
          });
        },
        __("Process")
      );

      frm.add_custom_button(
        __("Reject the Supplier"),
        function () {
          frappe.msgprint("Rejection Mail Sent");
          frm.set_value("status", "Rejected");
        },
        __("Process")
      );
    }
  },
  are_you_an_av_unit: function (frm) {
    if (frm.doc.are_you_an_av_unit === "Yes") {
      frm.set_value("naming_series", "CEBA-AV-.1.###");
    } else {
      frm.set_value("naming_series", "CEBA-NAV-.2.###");
    }
  },
  on_load: function (frm) {
    if (frm.doc.are_you_an_av_unit === "Yes") {
      frm.set_value("naming_series", "CEBA-AV-.1.###");
    } else {
      frm.set_value("naming_series", "CEBA-NAV-.2.###");
    }
  },
});
