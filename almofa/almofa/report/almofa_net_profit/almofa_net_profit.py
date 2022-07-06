# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_data(filters):
    return frappe.db.sql(
        """
select 
tsi.name , tsi.customer , tsi.customer_group , tsi.posting_date ,
tsi.base_net_total , coalesce(si_cogs.debit, 0) + coalesce(cogs.debit, 0) buying_amount , 
tsi.base_net_total - coalesce(si_cogs.debit, 0) - coalesce(cogs.debit,0) gross_profit, 
round((tsi.base_net_total - coalesce(si_cogs.debit, 0) - coalesce(cogs.debit,0))/tsi.base_net_total * 100, 2) gross_profit_pct ,
coalesce(tpi_coll.amount,0) + coalesce(coll.amount,0) collection_fees , 
coalesce(tpi_trans.amount,0) + coalesce(trans.amount,0) transport_fees , 
coalesce(tpi_dlay.amount,0) + coalesce(dlay.amount,0) dlay_fine , 
coalesce(tpi_oex.amount,0) + coalesce(oex.amount,0) other_expenses ,
tsi.base_net_total - coalesce(si_cogs.debit, 0)- coalesce(cogs.debit,0) 
- coalesce(dlay.amount,0) - coalesce(trans.amount,0) - coalesce(coll.amount,0) - coalesce(oex.amount,0) 
- coalesce(tpi_dlay.amount,0) - coalesce(tpi_trans.amount,0) - coalesce(tpi_coll.amount,0) - coalesce(tpi_oex.amount,0) net_profit , 
round(100 * (tsi.base_net_total - coalesce(si_cogs.debit, 0) - coalesce(cogs.debit,0) 
- coalesce(dlay.amount,0) - coalesce(trans.amount,0) - coalesce(coll.amount,0) - coalesce(oex.amount,0)
- coalesce(tpi_dlay.amount,0) - coalesce(tpi_trans.amount,0) - coalesce(tpi_coll.amount,0) - coalesce(tpi_oex.amount,0)) /tsi.base_net_total,2) net_profit_pct
from `tabSales Invoice` tsi
left outer join (
    select voucher_no , sum(debit) debit from `tabGL Entry` tge 
    where account in (
        select name from tabAccount ta  
        where company = %(company)s
        and account_type = 'Cost of Goods Sold'
    )
    and voucher_type = 'Sales Invoice'
    group by voucher_no
) si_cogs on si_cogs.voucher_no = tsi.name
left outer join (
	select parent , against_sales_invoice  
	from `tabDelivery Note Item` tdni 
	where against_sales_invoice is not null
	group by parent , against_sales_invoice
) dn on dn.against_sales_invoice = tsi.name 
left outer join (
    select voucher_no , sum(debit) debit from `tabGL Entry` tge 
    where account in (
        select name from tabAccount ta  
        where company = %(company)s
        and account_type = 'Cost of Goods Sold'
    )
    and voucher_type = 'Delivery Note'
    group by voucher_no
) cogs on cogs.voucher_no = dn.parent
left outer join (
	select sales_invoice_for_net_profit_cf si_name, 
	sum(debit) amount from `tabJournal Entry Account` tjea 
	where account = (
		select default_delay_fine_account_cf 
		from tabCompany tc where name = %(company)s
	)
	group by sales_invoice_for_net_profit_cf
) dlay on dlay.si_name = tsi.name
left outer join (
	select sales_invoice_for_net_profit_cf si_name, 
	sum(debit) amount from `tabJournal Entry Account` tjea 
	where account = (
		select default_transport_fees_account_cf 
		from tabCompany tc where name = %(company)s
	)
	group by sales_invoice_for_net_profit_cf
) trans on trans.si_name = tsi.name
left outer join (
	select sales_invoice_for_net_profit_cf si_name, 
	sum(debit) amount from `tabJournal Entry Account` tjea 
	where account = (
		select default_collection_fees_account_cf 
		from tabCompany tc where name = %(company)s
	)
	group by sales_invoice_for_net_profit_cf
) coll on coll.si_name = tsi.name
left outer join (
	select sales_invoice_for_net_profit_cf si_name, 
	sum(debit) amount from `tabJournal Entry Account` tjea 
	inner join tabAccount ta2 on ta2.company = %(company)s and ta2.account_type = 'Expense Account' and ta2.name = tjea.account 
	group by sales_invoice_for_net_profit_cf
) oex on oex.si_name = tsi.name
left outer join (
    select sales_invoice_for_net_profit_cf si_name, sum(base_net_amount) amount
    from `tabPurchase Invoice Item` tpii 
    where expense_account = (
        select default_delay_fine_account_cf 
		from tabCompany tc where name = %(company)s
    )
    group by sales_invoice_for_net_profit_cf
) tpi_dlay on tpi_dlay.si_name = tsi.name
left outer join (
    select sales_invoice_for_net_profit_cf si_name, sum(base_net_amount) amount
    from `tabPurchase Invoice Item` tpii 
    where expense_account = (
        select default_transport_fees_account_cf 
		from tabCompany tc where name = %(company)s
    )
    group by sales_invoice_for_net_profit_cf
) tpi_trans on tpi_trans.si_name = tsi.name
left outer join (
    select sales_invoice_for_net_profit_cf si_name, sum(base_net_amount) amount
    from `tabPurchase Invoice Item` tpii 
    where expense_account = (
        select default_collection_fees_account_cf 
		from tabCompany tc where name = %(company)s
    )
    group by sales_invoice_for_net_profit_cf
) tpi_coll on tpi_coll.si_name = tsi.name
left outer join (
    select sales_invoice_for_net_profit_cf si_name, sum(base_net_amount) amount
    from `tabPurchase Invoice Item` tpii 
	inner join tabAccount ta2 on ta2.company = %(company)s and ta2.account_type = 'Expense Account' 
        and ta2.name = tpii.expense_account 
    group by sales_invoice_for_net_profit_cf
) tpi_oex on tpi_oex.si_name = tsi.name
        {conditions}
order by tsi.name 
    """.format(
            conditions=get_conditions(filters)
        ),
        filters,
        debug=1,
    )


def get_columns(filters):
    return csv_to_columns(
        """
        Sales Invoice,name,Link,Sales Invoice,140
        Customer,customer,Link,Customer,260
        Customer Group,customer_group,Link,Customer Group,200
        Posting Date,posting_date,Date,120
        Selling Amount,base_net_total,Currency,120
        Buying Amount,buying_amount,Currency,120
        Gross Profit,gross_profit,Currency,120
        Profit Percent,profit_percent,Percent,120
        Collection Fees,collection_fees,Currency,120
        Transport Fees,transport_fees,Currency,120
        Delay Fine,delay_fine,Currency,120
        Other Expenses,other_expenses,Currency,120
        Net Profit,net_profit,Currency,120
        Net Profit %,net_profit_percent,Percent,120
    """
    )


def csv_to_columns(csv_str):
    props = ["label", "fieldname", "fieldtype", "options", "width"]
    return [
        zip(props, [x.strip() for x in col.split(",")])
        for col in csv_str.split("\n")
        if col.strip()
    ]


def get_conditions(filters):
    where_conditions = []

    if filters.get("company"):
        where_conditions += ["tsi.docstatus = 1 and tsi.company = %(company)s "]
    if filters.get("from_date"):
        where_conditions += ["tsi.posting_date >= %(from_date)s"]
    if filters.get("to_date"):
        where_conditions += ["tsi.posting_date <= %(to_date)s"]

    return where_conditions and " where {}".format(" and ".join(where_conditions)) or ""
