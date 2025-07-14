// Copyright (c) 2024, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quality Check", {
  refresh(frm) {
    if (frm.doc.docstatus == 1) {
      frm.page.add_inner_button(
        __("Generate Purchase Receipt"),
        () => {
          const doc_name = frm.docname;
          const doc_type = frm.doctype;

          frappe.call({
            method:
              "ez_supermarket.ez_supermarket.doctype.quality_check.quality_check.generate_purchase_receipt",
            args: {
              doc_name: doc_name,
              doc_type: doc_type,
            },
            callback: (r) => {
              frappe.set_route("Form", "Purchase Receipt", r.message);
            },
          });
        },
        __("Create")
      );
    }
    frm.set_query(
      "article_location",
      "accepted_item",
      function (doc, cdt, cdn) {
        var d = locals[cdt][cdn];
        return {
          filters: {
            warehouse: d.warehouse,
          },
        };
      }
    );
  },
});

frappe.ui.form.on("Accepted Items", {
  accepted_qty: function (frm, cdt, cdn) {
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

  rejected_qty: function (frm, cdt, cdn) {
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

  received_qty: function (frm, cdt, cdn) {
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

  frm.doc.accepted_item.forEach((row) => {
    accepted += row.accepted_qty;
    rejected += row.rejected_qty;
  });

  if (accepted == 0) {
    frm.set_value("status", "Rejected");
    frm.toggle_reqd("rejected_warehouse", true);
  } else if (rejected == 0) {
    frm.set_value("status", "Accepted");
    frm.toggle_reqd("rejected_warehouse", false);
  } else {
    frm.set_value("status", "Partially Accepted");
    frm.toggle_reqd("rejected_warehouse", true);
  }

  refresh_field("status");
}
