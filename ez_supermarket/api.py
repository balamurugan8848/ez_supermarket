import frappe

class EzSuperMarket:
    @staticmethod
    @frappe.whitelist()
    def get_last_purchase_rate(name, conversion_rate, item_code, conversion_factor=1.0):
        """Get last purchase rate for an item"""

        conversion_rate = frappe.utils.flt(conversion_rate) or 1.0

        last_purchase_details = EzSuperMarket.get_last_purchase_details(item_code, name)
        if last_purchase_details:
            last_purchase_rate = (
                last_purchase_details["base_net_rate"] * (frappe.utils.flt(conversion_factor) or 1.0)
            ) / conversion_rate
            return last_purchase_rate
        else:
            item_last_purchase_rate = frappe.get_cached_value("Item", item_code, "last_purchase_rate")
            if item_last_purchase_rate:
                return item_last_purchase_rate

    @staticmethod
    @frappe.whitelist()
    def get_last_purchase_details(item_code, parent_name):
        """Retrieve the last purchase details for an item"""
        
        last_purchase_details = frappe.get_all(
            "Purchase Order Item",
            filters={"item_code": item_code, "docstatus": 1},
            fields=["base_net_rate"],
            order_by="creation DESC",
            limit=1,
        )

        if last_purchase_details:
            return last_purchase_details[0]

        return None
@frappe.whitelist()
def get_last_purchase_rate(name, conversion_rate, item_code, conversion_factor=1.0):
    return EzSuperMarket.get_last_purchase_rate(name, conversion_rate, item_code, conversion_factor)

# @frappe.whitelist()
# def get_budget_tracking(company_name):
#   return frappe.get_doc("AV Budget Tracking", {
#     "company_name": company_name,

#   })