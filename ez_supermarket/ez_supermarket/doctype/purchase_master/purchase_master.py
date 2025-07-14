# Copyright (c) 2024, Balamurugan and contributors
# For license information, please see license.txt


import frappe
from frappe import db
from datetime import datetime, timedelta
from frappe.utils import flt
from frappe import _
from frappe import _, throw
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate

import erpnext
from erpnext.accounts.deferred_revenue import validate_service_stop_date
from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
from erpnext.accounts.doctype.repost_accounting_ledger.repost_accounting_ledger import (
	validate_docs_for_deferred_accounting,
	validate_docs_for_voucher_types,
)
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	check_if_return_invoice_linked_with_payment_entry,
	get_total_in_party_account_currency,
	is_overdue,
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import (
	get_party_tax_withholding_details,
)
from erpnext.accounts.general_ledger import (
	get_round_off_account_and_cost_center,
	make_gl_entries,
	make_reverse_gl_entries,
	merge_similar_entries,
)
from erpnext.accounts.party import get_due_date, get_party_account
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from erpnext.assets.doctype.asset.asset import is_cwip_accounting_enabled
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.buying.utils import check_on_hold_or_closed_status
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock import get_warehouse_account_map
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import (
	get_item_account_wise_additional_cost,
	update_billed_amount_based_on_po,
)


class WarehouseMissingError(frappe.ValidationError):
	pass


form_grid_templates = {"items": "templates/form_grid/item_grid.html"}


class PurchaseMaster(BuyingController):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.accounts.doctype.advance_tax.advance_tax import AdvanceTax
		from erpnext.accounts.doctype.payment_schedule.payment_schedule import PaymentSchedule
		from erpnext.accounts.doctype.pricing_rule_detail.pricing_rule_detail import PricingRuleDetail
		from erpnext.accounts.doctype.purchase_invoice_advance.purchase_invoice_advance import (
			PurchaseMasterAdvance,
		)
		from erpnext.accounts.doctype.purchase_invoice_item.purchase_invoice_item import (
			PurchaseMasterItem,
		)
		from erpnext.accounts.doctype.purchase_taxes_and_charges.purchase_taxes_and_charges import (
			PurchaseTaxesandCharges,
		)
		from erpnext.accounts.doctype.tax_withheld_vouchers.tax_withheld_vouchers import (
			TaxWithheldVouchers,
		)
		from erpnext.buying.doctype.purchase_receipt_item_supplied.purchase_receipt_item_supplied import (
			PurchaseReceiptItemSupplied,
		)

		additional_discount_percentage: DF.Float
		address_display: DF.SmallText | None
		advance_tax: DF.Table[AdvanceTax]
		advances: DF.Table[PurchaseMasterAdvance]
		against_expense_account: DF.SmallText | None
		allocate_advances_automatically: DF.Check
		amended_from: DF.Link | None
		apply_discount_on: DF.Literal["", "Grand Total", "Net Total"]
		apply_tds: DF.Check
		auto_repeat: DF.Link | None
		base_discount_amount: DF.Currency
		base_grand_total: DF.Currency
		base_in_words: DF.Data | None
		base_net_total: DF.Currency
		base_paid_amount: DF.Currency
		base_rounded_total: DF.Currency
		base_rounding_adjustment: DF.Currency
		base_tax_withholding_net_total: DF.Currency
		base_taxes_and_charges_added: DF.Currency
		base_taxes_and_charges_deducted: DF.Currency
		base_total: DF.Currency
		base_total_taxes_and_charges: DF.Currency
		base_write_off_amount: DF.Currency
		bill_date: DF.Date | None
		bill_no: DF.Data | None
		billing_address: DF.Link | None
		billing_address_display: DF.SmallText | None
		buying_price_list: DF.Link | None
		cash_bank_account: DF.Link | None
		clearance_date: DF.Date | None
		company: DF.Link | None
		contact_display: DF.SmallText | None
		contact_email: DF.SmallText | None
		contact_mobile: DF.SmallText | None
		contact_person: DF.Link | None
		conversion_rate: DF.Float
		cost_center: DF.Link | None
		credit_to: DF.Link
		currency: DF.Link | None
		disable_rounded_total: DF.Check
		discount_amount: DF.Currency
		due_date: DF.Date | None
		from_date: DF.Date | None
		grand_total: DF.Currency
		group_same_items: DF.Check
		hold_comment: DF.SmallText | None
		ignore_default_payment_terms_template: DF.Check
		ignore_pricing_rule: DF.Check
		in_words: DF.Data | None
		incoterm: DF.Link | None
		inter_company_invoice_reference: DF.Link | None
		is_internal_supplier: DF.Check
		is_old_subcontracting_flow: DF.Check
		# is_opening: DF.Literal["No", "Yes"]
		is_paid: DF.Check
		is_return: DF.Check
		is_subcontracted: DF.Check
		items: DF.Table[PurchaseMasterItem]
		language: DF.Data | None
		letter_head: DF.Link | None
		mode_of_payment: DF.Link | None
		named_place: DF.Data | None
		naming_series: DF.Literal["ACC-PINV-.YYYY.-", "ACC-PINV-RET-.YYYY.-"]
		net_total: DF.Currency
		on_hold: DF.Check
		only_include_allocated_payments: DF.Check
		other_charges_calculation: DF.LongText | None
		outstanding_amount: DF.Currency
		paid_amount: DF.Currency
		party_account_currency: DF.Link | None
		payment_schedule: DF.Table[PaymentSchedule]
		payment_terms_template: DF.Link | None
		per_received: DF.Percent
		plc_conversion_rate: DF.Float
		posting_date: DF.Date
		posting_time: DF.Time | None
		price_list_currency: DF.Link | None
		pricing_rules: DF.Table[PricingRuleDetail]
		project: DF.Link | None
		rejected_warehouse: DF.Link | None
		release_date: DF.Date | None
		remarks: DF.SmallText | None
		repost_required: DF.Check
		represents_company: DF.Link | None
		return_against: DF.Link | None
		rounded_total: DF.Currency
		rounding_adjustment: DF.Currency
		scan_barcode: DF.Data | None
		select_print_heading: DF.Link | None
		set_from_warehouse: DF.Link | None
		set_posting_time: DF.Check
		set_warehouse: DF.Link | None
		shipping_address: DF.Link | None
		shipping_address_display: DF.SmallText | None
		shipping_rule: DF.Link | None
		status: DF.Literal[
			"",
			"Draft",
			"Return",
			"Debit Note Issued",
			"Submitted",
			"Paid",
			"Partly Paid",
			"Unpaid",
			"Overdue",
			"Cancelled",
			"Internal Transfer",
		]
		subscription: DF.Link | None
		supplied_items: DF.Table[PurchaseReceiptItemSupplied]
		supplier: DF.Link
		supplier_address: DF.Link | None
		supplier_name: DF.Data | None
		supplier_warehouse: DF.Link | None
		tax_category: DF.Link | None
		tax_id: DF.ReadOnly | None
		tax_withheld_vouchers: DF.Table[TaxWithheldVouchers]
		tax_withholding_category: DF.Link | None
		tax_withholding_net_total: DF.Currency
		taxes: DF.Table[PurchaseTaxesandCharges]
		taxes_and_charges: DF.Link | None
		taxes_and_charges_added: DF.Currency
		taxes_and_charges_deducted: DF.Currency
		tc_name: DF.Link | None
		terms: DF.TextEditor | None
		title: DF.Data | None
		to_date: DF.Date | None
		total: DF.Currency
		total_advance: DF.Currency
		total_net_weight: DF.Float
		total_qty: DF.Float
		total_taxes_and_charges: DF.Currency
		unrealized_profit_loss_account: DF.Link | None
		# update_stock: DF.Check
		use_company_roundoff_cost_center: DF.Check
		use_transaction_date_exchange_rate: DF.Check
		write_off_account: DF.Link | None
		write_off_amount: DF.Currency
		write_off_cost_center: DF.Link | None
	# end: auto-generated types

	def __init__(self, *args, **kwargs):
		super(PurchaseMaster, self).__init__(*args, **kwargs)
		self.status_updater = [
			{
				"source_dt": "Purchase Invoice Item",
				"target_dt": "Purchase Order Item",
				"join_field": "po_detail",
				"target_field": "billed_amt",
				"target_parent_dt": "Purchase Order",
				"target_parent_field": "per_billed",
				"target_ref_field": "amount",
				"source_field": "amount",
				"percent_join_field": "purchase_order",
				"overflow_type": "billing",
			}
		]

@frappe.whitelist()
def fetch_supplier_items(supplier):
    items = []
    
    item_supplier = frappe.get_all("Item Supplier", 
        filters={
            "supplier": supplier
        },
        fields=["parent"]
    )
    
    for row in item_supplier:
        item_code = row.parent
        item = frappe.get_doc("Item", item_code)
        
        # Fetch current balance of the item
        stall_qty, store_rooms_qty = get_item_current_balance(item_code)
        
        # Get the first and last day of the current month
        today = datetime.today()
        first_day_of_current_month = datetime(today.year, today.month, 1)
        last_day_of_current_month = (first_day_of_current_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Make sure the dates cover the entire day
        first_day_of_current_month = first_day_of_current_month.replace(hour=0, minute=0, second=0, microsecond=0)
        last_day_of_current_month = last_day_of_current_month.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get the first and last day of the last month
        last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        # Get the first and last day of the month before the last month
        last_day_of_month_before_last = first_day_of_last_month - timedelta(days=1)
        first_day_of_month_before_last = last_day_of_month_before_last.replace(day=1)
        
        # Fetch sales and purchases for the last two months
        last_month_sales, last_month_purchase = get_qty_and_price(item_code, first_day_of_last_month, last_day_of_last_month)
        previous_last_month_sales, previous_last_month_purchase = get_qty_and_price(item_code, first_day_of_month_before_last, last_day_of_month_before_last)
        current_month_sales, current_month_purchase = get_qty_and_price(item_code, first_day_of_current_month, last_day_of_current_month)
        
        items.append({
                    "item_code": item_code,
                    "item_name": item.item_name,
                    "uom": item.stock_uom,
                    "custom_available_qty": f"{stall_qty if stall_qty is not None else 0} / {store_rooms_qty if store_rooms_qty is not None else 0}",
                    "custom_last_month_sales": f"{last_month_sales['total_qty'] if last_month_sales['total_qty'] is not None else 0} {item.stock_uom} / Rs {last_month_sales['avg_rate'] if last_month_sales['avg_rate'] is not None else 0}",
                    "custom_previous_last_month_sales": f"{previous_last_month_sales['total_qty'] if previous_last_month_sales['total_qty'] is not None else 0} {item.stock_uom} / Rs {previous_last_month_sales['avg_rate'] if previous_last_month_sales['avg_rate'] is not None else 0}",
                    "custom_current_month_sales_2": f"{current_month_sales['total_qty'] if current_month_sales['total_qty'] is not None else 0} {item.stock_uom} / Rs {current_month_sales['avg_rate'] if current_month_sales['avg_rate'] is not None else 0}",
                    "custom_last_month_purchase": f"{last_month_purchase['total_qty'] if last_month_purchase['total_qty'] is not None else 0} {item.stock_uom} / Rs {last_month_purchase['avg_rate'] if last_month_purchase['avg_rate'] is not None else 0}",
                    "custom_previous_last_month_purchase": f"{previous_last_month_purchase['total_qty'] if previous_last_month_purchase['total_qty'] is not None else 0} {item.stock_uom} / Rs {previous_last_month_purchase['avg_rate'] if previous_last_month_purchase['avg_rate'] is not None else 0}",
                    "custom_current_month_purchase": f"{current_month_purchase['total_qty'] if current_month_purchase['total_qty'] is not None else 0} {item.stock_uom} / Rs {current_month_purchase['avg_rate'] if current_month_purchase['avg_rate'] is not None else 0}",
                    "custom_tax": item.custom_tax_rate if item.custom_tax_rate is not None else 0,
                    "custom_mrp": item.custom_mrp if item.custom_mrp is not None else 0,
                })

    return items
@frappe.whitelist()																	
def get_qty_and_price(item_code, start_date, end_date):
    # Query Sales Invoices for the given item within the given date range
    sales_qty = frappe.db.sql("""
        SELECT SUM(sii.qty) as total_qty, AVG(sii.rate) as avg_rate
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE sii.item_code = %s
            AND si.posting_date BETWEEN %s AND %s
            AND si.docstatus = 1
    """, (item_code, start_date, end_date), as_dict=True)[0]

    # Query Purchase Invoices for the given item within the given date range
    purchase_qty = frappe.db.sql("""
        SELECT SUM(pii.qty) as total_qty, AVG(pii.rate) as avg_rate
        FROM `tabPurchase Invoice` pi
        JOIN `tabPurchase Invoice Item` pii ON pi.name = pii.parent
        WHERE pii.item_code = %s
            AND pi.posting_date BETWEEN %s AND %s
            AND pi.docstatus = 1
    """, (item_code, start_date, end_date), as_dict=True)[0]

    return sales_qty, purchase_qty


def get_last_purchase_rate_from_item_price(item_code):
    item_price = frappe.get_all("Item Price",
                                 filters={"item_code": item_code, "price_list": "Standard Buying"},
                                 fields=["price_list_rate"],
                                 order_by="valid_from DESC",
                                 limit=1)

    if item_price:
        return item_price[0].price_list_rate
    else:
        return 0  # Return 0 if no item price is found

def get_item_tax_template(item):
    # Fetch the item's tax template (you may need to adjust the field name)
    return item.get("taxes")[0].get("item_tax_template", "") if item.get("taxes") else ""


def get_item_current_balance(item_code):
    # Fetch all warehouses
    all_warehouses = frappe.get_all("Warehouse", fields=["name", "custom_selling_warehouse"])

    # Separate the selling warehouse from the other warehouses
    selling_warehouse = next((wh['name'] for wh in all_warehouses if wh['custom_selling_warehouse']), None)
    other_warehouses = [wh['name'] for wh in all_warehouses if not wh['custom_selling_warehouse']]

    bin_docs = frappe.get_all("Bin",
                              filters={"item_code": item_code, "warehouse": ["in", [selling_warehouse] + other_warehouses]},
                              fields=["warehouse", "actual_qty"])

    quantity_by_warehouse = {warehouse: 0 for warehouse in [selling_warehouse] + other_warehouses}

    for bin_doc in bin_docs:
        warehouse = bin_doc.get("warehouse")
        actual_qty = bin_doc.get("actual_qty")
        quantity_by_warehouse[warehouse] += actual_qty

    # Sum up the quantities from all the other warehouses
    other_qty = sum(qty for warehouse, qty in quantity_by_warehouse.items() if warehouse in other_warehouses)

    return quantity_by_warehouse[selling_warehouse], other_qty


@frappe.whitelist()
def get_previous_purchase_details(item_code, rate):
    try:
        # Find the previous purchase details
        sql_query = """
            SELECT
                pi.supplier,
                pi.posting_date as date,
                MIN(pi_item.rate) as rate
            FROM
                `tabPurchase Invoice` pi
            JOIN
                `tabPurchase Invoice Item` pi_item ON pi.name = pi_item.parent
            WHERE
                pi_item.item_code = %(item_code)s
                AND pi_item.rate < %(rate)s
            GROUP BY
                pi.supplier,
                pi.posting_date
            ORDER BY
                rate ASC
            LIMIT 1
        """

        result = frappe.db.sql(sql_query, {'item_code': item_code, 'rate': rate}, as_dict=True)

        if result:
            return {
                'supplier': result[0].supplier,
                'date': result[0].date,
                'rate': result[0].rate
            }
        else:
            return _("No previous purchase invoice found for the given criteria.")

    except Exception as e:
        frappe.log_error(f"Error in get_previous_purchase_details: {e}")
        return _("Error occurred while fetching previous purchase details.")


@frappe.whitelist()
def get_tax_rate(item_tax_template):
    tax_rate = frappe.db.get_value('Item Tax Template Detail', {'parent': item_tax_template}, ['tax_rate'])
    print(tax_rate)
    return tax_rate

@frappe.whitelist()
def check_supplier_bill_no(supplier, custom_suppliers_bill_no):
    existing_po = frappe.get_value("Purchase Order", {
        'supplier': supplier,
        'custom_suppliers_bill_no': custom_suppliers_bill_no,
        'docstatus': 1  # Include only submitted Purchase Orders
    }, 'name')

    return {'existing_po': existing_po}

@frappe.whitelist()
def get_bank_cash_account(mode_of_payment, company):
	account = frappe.db.get_value(
		"Mode of Payment Account", {"parent": mode_of_payment, "company": company}, "default_account"
	)
	if not account:
		frappe.throw(
			_("Please set default Cash or Bank account in Mode of Payment {0}").format(
				get_link_to_form("Mode of Payment", mode_of_payment)
			),
			title=_("Missing Account"),
		)
	return {"account": account}


@frappe.whitelist()
def create_purchase_invoice(purchase_master):
    purchase_master = frappe.get_doc("Purchase Master", purchase_master)

    purchase_invoice = frappe.new_doc("Purchase Invoice")

    purchase_invoice.supplier = purchase_master.supplier
    # purchase_invoice.custom_payment_made_to = purchase_master.payment_made_to
    purchase_invoice.posting_date = purchase_master.posting_date
    purchase_invoice.set_posting_time = 1
    
    if purchase_master.payment_made == 'Yes':
        purchase_invoice.is_paid = 1
    else:
        purchase_invoice.is_paid = 0
    purchase_invoice.mode_of_payment = purchase_master.mode_of_payment
    purchase_invoice.cash_bank_account = purchase_master.cashbank_account
    purchase_invoice.update_stock = purchase_master.update_stock
    purchase_invoice.set_warehouse = purchase_master.set_warehouse
    purchase_invoice.custom_document_type = "Purchase Master"
    purchase_invoice.custom_reference_document = purchase_master.name
    purchase_invoice.tax_category = purchase_master.tax_category
    purchase_invoice.taxes_and_charges = purchase_master.taxes_and_charges

    for item in purchase_master.items:
        purchase_invoice.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "amount": item.amount,
            "batch_no": item.batch_no,
        })
        
    for tax in purchase_master.taxes:
        purchase_invoice.append("taxes", {
			"charge_type": tax.charge_type,
			"account_head": tax.account_head,
        	"rate": tax.rate,
        	"tax_amount": tax.tax_amount,
        	"total": tax.total,
        	"description": tax.description
	
		})

    purchase_invoice.insert()
    purchase_invoice.submit()

    msg = f"Purchase Invoice <b>{purchase_invoice.name}</b> has been created successfully!!!" 
    link = f"<b><a href='/app/purchase-invoice/{purchase_invoice.name}'>{purchase_invoice.name}</a></b>"
    full_msg = _(msg + ". " + link)
    frappe.msgprint(full_msg)
    
    return purchase_invoice




@frappe.whitelist()
def on_submit(doc, method):
  create_purchase_invoice(doc.name)
  
@frappe.whitelist()
def get_total_purchase_qty(item_code, number_of_months):
    result = frappe.db.sql("""
        SELECT SUM(pii.qty) AS total_qty
        FROM `tabPurchase Invoice Item` pii
        JOIN `tabPurchase Invoice` pi ON pi.name = pii.parent
        WHERE pii.item_code = %s
        AND pi.posting_date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
        AND pi.docstatus = 1
    """, (item_code, number_of_months))

    if result:
        return {"total_qty": result[0][0] or 0}
    else:
        return {"total_qty": 0}
