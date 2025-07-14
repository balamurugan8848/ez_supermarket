app_name = "ez_supermarket"
app_title = "Ez-Supermarket"
app_publisher = "Balamurugan"
app_description = "Super Market"
app_email = "balamurugan@yuvabe.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ez_supermarket/css/ez_supermarket.css"
# app_include_js = "/assets/ez_supermarket/js/ez_supermarket.js"

# include js, css files in header of web template
# web_include_css = "/assets/ez_supermarket/css/ez_supermarket.css"
# web_include_js = "/assets/ez_supermarket/js/ez_supermarket.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ez_supermarket/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Material Request" : "ez_supermarket/custom/material_request/material_request.js",
    "Purchase Order" : "ez_supermarket/custom/purchase_order/purchase_order.js",
    # "Purchase Invoice" : "ez_supermarket/custom/purchase_invoice/purchase_invoice.js",
    "Purchase Receipt" : "ez_supermarket/custom/purchase_receipt/purchase_receipt.js",
    "Stock Entry" : "ez_supermarket/custom/stock_entry/stock_entry.js",
    "Item" : "ez_supermarket/custom/item/item.js",
    "Supplier Quotation" : "ez_supermarket/custom/supplier_quotation/supplier_quotation.js",}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ez_supermarket/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "ez_supermarket.utils.jinja_methods",
#	"filters": "ez_supermarket.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ez_supermarket.install.before_install"
# after_install = "ez_supermarket.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ez_supermarket.uninstall.before_uninstall"
# after_uninstall = "ez_supermarket.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ez_supermarket.utils.before_app_install"
# after_app_install = "ez_supermarket.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ez_supermarket.utils.before_app_uninstall"
# after_app_uninstall = "ez_supermarket.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ez_supermarket.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    # "Purchase Invoice": {
    #     "on_submit": "ez_supermarket.ez_supermarket.custom.purchase_invoice.purchase_invoice.on_submit"
    # },
    "Purchase Receipt": {
        "on_submit": "ez_supermarket.ez_supermarket.custom.purchase_receipt.purchase_receipt.on_submit",
        # "on_submit": "ez_supermarket.ez_supermarket.custom.purchase_receipt.purchase_receipt.update_item_lead_time",
        # "before_save": "ez_supermarket.ez_supermarket.custom.purchase_receipt.purchase_receipt.update_item_lead_time",
        "before_submit" : "ez_supermarket.ez_supermarket.custom.purchase_receipt.purchase_receipt.update_item_fields"
    },
    "Quick Purchase": {
         "on_submit": "ez_supermarket.ez_supermarket.doctype.quick_purchase.quick_purchase.on_submit"
    },
    "Expense Entry": {
        "on_update": "ez_supermarket.ez_supermarket.doctype.expense_entry.expense_entry.setup"
    },
    "Stock Adjust":{
        "on_submit": "ez_supermarket.ez_supermarket.doctype.stock_adjust.stock_adjust.on_submit"
    },
    "Purchase Master": {
         "on_submit": "ez_supermarket.ez_supermarket.doctype.purchase_master.purchase_master.on_submit"
    },
}
# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"ez_supermarket.tasks.all"
#	],
#	"daily": [
#		"ez_supermarket.tasks.daily"
#	],
#	"hourly": [
#		"ez_supermarket.tasks.hourly"
#	],
#	"weekly": [
#		"ez_supermarket.tasks.weekly"
#	],
#	"monthly": [
#		"ez_supermarket.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "ez_supermarket.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "ez_supermarket.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "ez_supermarket.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ez_supermarket.utils.before_request"]
# after_request = ["ez_supermarket.utils.after_request"]

# Job Events
# ----------
# before_job = ["ez_supermarket.utils.before_job"]
# after_job = ["ez_supermarket.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"ez_supermarket.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
#	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    "Workflow State", "Workflow Action Master",
    # {"dt": "Workflow", "filters": [["name", "=", "Purchase & Price Update"]]},
    {"dt": "Workflow", "filters": [["name", "in", ["Purchase & Price Update", "Supplier Approval", "Expense Entry Approval", "Purchase Master Workflow", "Procurement Master"]]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Ez-Supermarket"]]},
    # {"dt": "Workflow", "filters": [["document_type", "=", "Procurement Master"]]}
]
