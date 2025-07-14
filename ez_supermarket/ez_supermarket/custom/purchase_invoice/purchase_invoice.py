

# # Import necessary libraries
# import frappe
# from frappe import _# import frappe
# from frappe.model.document import Document


# class PurchaseInvoice(Document):
# 	pass

# # Function to be called on Purchase Invoice submission
# def create_item_prices(doc, method):
#     for item in doc.items:
#         # Create a unique batch ID using item code and current date
#         batch_id = f"{item.item_code}-{frappe.utils.nowdate()}"
        
#         # Check if the item price already exists
#         existing_item_price = frappe.get_all("Item Price", filters={"item_code": item.item_code, "price_list": doc.buying_price_list, "batch_no": batch_id}, fields=["name"])

#         if not existing_item_price:
#             # Create a new Item Price entry
#             item_price = frappe.get_doc({
#                 "doctype": "Item Price",
#                 "item_code": item.item_code,
#                 "price_list": "Standard Selling",
#                 "selling": 1,
#                 "price_list_rate": item.custom_selling_price,
#                 "batch_no": batch_id
#             })
            
#             item_price.insert()

# # Attach the function to the Purchase Invoice submit event
# def on_submit(doc, method):
#     create_item_prices(doc, method)

# # Register the custom script
# def register_custom_script():
#     if "Purchase Invoice" not in frappe.get_hooks("on_submit"):
#         frappe.append_hook("on_submit", on_submit)

# # Uncomment the line below to register the custom script
# # register_custom_script()
