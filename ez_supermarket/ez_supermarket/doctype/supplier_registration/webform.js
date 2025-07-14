frappe.web_form.on("are_you_an_av_unit", (field, value) => {
  console.log("are_you_an_av_unit:", value);
  updateNamingSeries(value);
});

frappe.web_form.on("gstin", (field, value) => {
  if (value && value.length >= 2) {
    let state_code = value.substring(0, 2);

    const state_mapping = {
      "01": "Jammu & Kashmir",
      "02": "Himachal Pradesh",
      "03": "Punjab",
      "04": "Chandigarh",
      "05": "Uttarkhand",
      "06": "Haryana",
      "07": "Delhi",
      "08": "Rajasthan",
      "09": "Uttar Pradesh",
      10: "Bihar",
      11: "Sikkim",
      12: "Arunachal Pradesh",
      13: "Nagaland",
      14: "Manipur",
      15: "Mizoram",
      16: "Tripura",
      17: "Meghalaya",
      18: "Assam",
      19: "West Bengal",
      20: "Jharkhand",
      21: "Orissa",
      22: "Chhattisgarh",
      23: "Madhya Pradesh",
      24: "Gujarat",
      25: "Daman & Diu",
      26: "Dadra and Nagar Haveli and Daman and Diu",
      27: "Maharashtra",
      28: "Andhra Pradesh (Old)",
      29: "Karnataka",
      30: "Goa",
      31: "Lakshadweep",
      32: "Kerala",
      33: "Tamil Nadu",
      34: "Pondicherry",
      35: "Andaman & Nicobar Islands",
      36: "Telengana",
      37: "Andhra Pradesh",
      38: "Ladakh",
      97: "Other Territory",
      99: "Other Territory",
    };

    let state = state_mapping[state_code];
    frappe.web_form.set_value("state", state);
    frappe.web_form.set_value("country", "India");
  }
});

frappe.web_form.validate = () => {
  console.log("Validating form...");
  let pan = frappe.web_form.get_value("pan");
  let gstin = frappe.web_form.get_value("gstin");
  console.log("pan:", pan);
  console.log("gstin:", gstin);
  let errors = [];
  let hasErrors = false; // Flag to track if any errors occurred during validation

  let gstHolderValue = frappe.web_form.get_value("gst_holder");

  if (gstHolderValue !== "No") {
    if (pan && /[a-z]/.test(pan)) {
      errors.push("PAN cannot contain lowercase letters.");
      hasErrors = true;
    }

    if (gstin && /[a-z]/.test(gstin)) {
      errors.push("GSTIN cannot contain lowercase letters.");
      hasErrors = true;
    }

    // Validate PAN
    if (!validate_pan(pan, gstin)) {
      errors.push("Invalid PAN / PAN Mismatch");
      hasErrors = true;
    }

    // Validate GSTIN
    if (!validate_gstin(gstin)) {
      errors.push("Invalid GSTIN. Please enter a valid GSTIN.");
      hasErrors = true;
    }

    // Check for already linked GSTIN only if "are_you_an_av_unit" field is not blank
    let areYouAnAVUnit = frappe.web_form.get_value("are_you_an_av_unit");
    if (areYouAnAVUnit === "Yes" || areYouAnAVUnit === "No") {
      validateLinkedGSTIN(gstin);
    }
  }

  if (hasErrors) {
    console.log("Validation errors:", errors);
    frappe.msgprint(errors.join("<br>"));
    frappe.validated = false; // prevent form submission
    return false;
  } else {
    console.log("Validation passed.");
  }
};

// Your other functions (updateNamingSeries, validate_pan, validate_gstin, validateLinkedGSTIN) remain the same.

function updateNamingSeries(value) {
  let namingSeries =
    value === "Yes" ? "CEBA-AV-.1.######" : "CEBA-NAV-.2.######";
  frappe.web_form.set_value("naming_series", namingSeries);
}

function validate_pan(pan, gstin) {
  if (!pan) {
    // PAN is not mandatory, so return true if it's not provided
    return true;
  }

  console.log("Validating PAN:", pan);

  // Extract PAN from the GSTIN (characters from 2nd to 12th position)
  let extractedPanFromGSTIN = gstin.slice(2, 12);

  // Remove any non-alphanumeric characters and whitespace from the extracted PAN and provided PAN
  let cleanPan = pan.replace(/[^a-zA-Z0-9]/g, "").toUpperCase();
  let cleanExtractedPan = extractedPanFromGSTIN
    .replace(/[^a-zA-Z0-9]/g, "")
    .toUpperCase();

  console.log("PAN:", cleanPan);
  console.log("Extracted PAN from GSTIN:", cleanExtractedPan);

  // Check if the extracted PAN from GSTIN matches the provided PAN
  if (cleanPan !== cleanExtractedPan) {
    return false;
  }

  return true;
}

function validate_gstin(gstin) {
  if (!gstin) {
    // GSTIN is not mandatory, so return true if it's not provided
    return true;
  }

  console.log("Validating GSTIN:", gstin);
  if (gstin.length != 15) return false;
  if (!gstin.slice(0, 2).match(/^\d+$/)) return false;
  if (!gstin.slice(2, 12).match(/^[A-Z0-9]+$/)) return false;
  if (!gstin[12].match(/^[1-9A-Z]$/)) return false;
  if (gstin[13] != "Z") return false;
  if (!gstin[14].match(/^[A-Z0-9]$/)) return false;
  return true;
}

function validateLinkedGSTIN(gstin) {
  let alreadyLinked = false;

  function showError(message) {
    alreadyLinked = true;
    frappe.msgprint({
      title: __("Already Registered"),
      indicator: "red",
      message: message,
    });
    frappe.validated = false; // prevent form submission
  }

  frappe.call({
    method: "frappe.client.get_list",
    args: {
      doctype: "Address",
      filters: {
        gstin: gstin,
      },
      fields: ["name"],
    },
    callback: function (r) {
      if (r.message.length > 0 && !alreadyLinked) {
        showError(__("GSTIN {0} already exists in Address", [gstin]));
      }
    },
  });

  frappe.call({
    method: "frappe.client.get_list",
    args: {
      doctype: "Supplier",
      filters: {
        gstin: gstin,
      },
      fields: ["name"],
    },
    callback: function (r) {
      if (r.message.length > 0 && !alreadyLinked) {
        showError(__("GSTIN {0} already linked with a Supplier", [gstin]));
      }
    },
  });
}
