# Copyright (c) 2024, Balamurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExpenseEntry(Document):
	pass

def setup(expense_entry, method):
    # add expenses up and set the total field

    total = 0
    count = 0
    expense_items = []

    
    for detail in expense_entry.expenses:
        total += float(detail.amount)        
        count += 1
        
        if not detail.cost_center and expense_entry.default_cost_center:
            detail.cost_center = expense_entry.default_cost_center

        expense_items.append(detail)

    expense_entry.expenses = expense_items

    expense_entry.total = total
    expense_entry.quantity = count

    make_journal_entry(expense_entry)

    


@frappe.whitelist()
def initialise_journal_entry(expense_entry_name):
    # make JE from javascript form Make JE button

    make_journal_entry(
        frappe.get_doc('Expense Entry', expense_entry_name)
    )


def make_journal_entry(expense_entry):

    if expense_entry.status == "Approved":         

        # check for duplicates
        
        if frappe.db.exists({'doctype': 'Journal Entry', 'bill_no': expense_entry.name}):
            frappe.throw(
                title="Error",
                msg="Journal Entry {} already exists.".format(expense_entry.name)
            )


        # Preparing the JE: convert expense_entry details into je account details

        accounts = []

        for detail in expense_entry.expenses:            

            accounts.append({  
                'debit_in_account_currency': float(detail.amount),
                'user_remark': str(detail.description),
                'account': detail.expense_account,
                'cost_center': detail.cost_center
            })

        # finally add the payment account detail

        pay_account = ""

        if (expense_entry.mode_of_payment != "Cash" and (not 
            expense_entry.payment_reference or not expense_entry.clearance_date)):
            frappe.throw(
                title="Enter Payment Reference",
                msg="Payment Reference and Date are Required for all non-cash payments."
            )
        else:
            expense_entry.clearance_date = ""
            expense_entry.payment_reference = ""


        pay_account = frappe.db.get_value('Mode of Payment Account', {'parent' : expense_entry.mode_of_payment, 'company' : expense_entry.company}, 'default_account')
        if not pay_account or pay_account == "":
            frappe.throw(
                title="Error",
                msg="The selected Mode of Payment has no linked account."
            )

        accounts.append({  
            'credit_in_account_currency': float(expense_entry.total),
            'user_remark': str(detail.description),
            'account': pay_account,
            'cost_center': expense_entry.default_cost_center
        })

        # create the journal entry
        je = frappe.get_doc({
            'title': expense_entry.name,
            'doctype': 'Journal Entry',
            'voucher_type': 'Journal Entry',
            'posting_date': expense_entry.posting_date,
            'company': expense_entry.company,
            'accounts': accounts,
            'user_remark': expense_entry.remarks,
            'mode_of_payment': expense_entry.mode_of_payment,
            'cheque_date': expense_entry.clearance_date,
            'reference_date': expense_entry.clearance_date,
            'cheque_no': expense_entry.payment_reference,
            'pay_to_recd_from': expense_entry.payment_to,
            'document_type': "Expense Entry",
            'reference_document': expense_entry.name,
            'bill_no': expense_entry.name
        })

        user = frappe.get_doc("User", frappe.session.user)

        full_name = str(user.first_name) + ' ' + str(user.last_name)
        expense_entry.db_set('approved_by', full_name)
        

        je.insert()
        je.submit()
        
        frappe.msgprint("Journal Entry {} has been created succesfully.".format(je.name))