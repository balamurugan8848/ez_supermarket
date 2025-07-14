// Copyright (c) 2023, Balamurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Article Location", {
  refresh(frm) {
    frm.set_query("warehouse", function (frm) {
      return {
        filters: {
          is_group: "0",
        },
      };
    });
  },
  on_submit: function (frm) {
    updateName1Field(frm);
  },
  location_id: function (frm) {
    updateName1Field(frm);
  },
  warehouse: function (frm) {
    updateName1Field(frm);
  },
});

function updateName1Field(frm) {
  let location_id = frm.doc.location_id;
  let warehouse = frm.doc.warehouse;

  if (warehouse && location_id) {
    let storeAbbreviation = getStoreAbbreviation(warehouse);
    frm.set_value("name1", storeAbbreviation + "-" + location_id);
  }
  refersh_field("name1");
}

function getStoreAbbreviation(warehouse) {
  if (warehouse === "Store 1 - PTPS") {
    return "S1";
  } else if (warehouse === "Store 2 - PTPS") {
    return "S2";
  } else if (warehouse === "Store 3 - PTPS") {
    return "S3";
  } else if (warehouse === "Store 4 - PTPS") {
    return "S4";
  } else if (warehouse === "Stall - PTPS") {
    return "ST";
  } else {
    return ""; // Handle other cases if needed
  }
}
