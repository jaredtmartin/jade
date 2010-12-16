# Jade Inventory Control System
#Copyright (C) 2010  Jared T. Martin

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied account of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.conf.urls.defaults import *
from jade.inventory.models import Sale, Purchase, Item, Account, Client, Vendor
from django.views.generic import list_detail, create_update

item={'model' : Item, 'post_save_redirect':'/inventory/items', 'template_name':'inventory/item_show.html'}

urlpatterns = patterns('',
    # ajax lists    
    (r'^client_list/$', 'jade.inventory.views.ajax_client_list'),
    (r'^vendor_list/$', 'jade.inventory.views.ajax_vendor_list'),
    (r'^account_list/$', 'jade.inventory.views.ajax_account_list'),
    (r'^item_list/$', 'jade.inventory.views.ajax_item_list'),
    (r'^account_group_list/$', 'jade.inventory.views.ajax_account_group_list'),
    (r'^report_list/$', 'jade.inventory.views.ajax_report_list'),
    (r'^price_group_list/$', 'jade.inventory.views.ajax_price_group_list'),
    (r'^unit_list/$', 'jade.inventory.views.ajax_unit_list'),
    (r'^site_list/$', 'jade.inventory.views.ajax_site_list'),
    (r'^user_list/$', 'jade.inventory.views.ajax_user_list'),
    (r'^tax_list/$', 'jade.inventory.views.ajax_tax_list'),
    (r'^transaction_entry_list/(?P<object_id>\d+)/$', 'jade.inventory.views.ajax_transaction_entry_list'),
    (r'^set-language/$', 'jade.inventory.views.set_languages'),
    
    # Sales
    (r'^sales/$', 'jade.inventory.views.list_sales'),
    (r'^sale/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_sale'),
    (r'^sale/new/$', 'jade.inventory.views.new_sale'),
    (r'^sale/(?P<doc_number>\w+)/receipt.pdf$', 'jade.inventory.views.sale_receipt'),
    (r'^sale/(?P<doc_number>\w+)/garantee.pdf$', 'jade.inventory.views.garantee_report'),
    (r'^sale/(?P<object_id>\d+)/pay/$', 'jade.inventory.views.add_payment_to_sale'),

    # Tax
    (r'^transaction/(?P<object_id>\d+)/get_tax_form/$', 'jade.inventory.views.get_tax_form'),
    (r'^saletax/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_saletax'),
    (r'^transaction/(?P<object_id>\d+)/addtax/$', 'jade.inventory.views.add_tax'),
    (r'^purchasetax/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchasetax'),
    
    # Discounts
    (r'^transaction/(?P<object_id>\d+)/add_discount/$', 'jade.inventory.views.add_discount'),
    (r'^salediscount/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_salediscount'),
    (r'^purchasediscount/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchasediscount'),
    
    # Sale Returns
    (r'^salereturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_salereturn'),
    (r'^salereturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_salereturn'),
    
    # Purchases
    (r'^purchases/$', 'jade.inventory.views.list_purchases'),
    (r'^purchase/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchase'),
    (r'^purchase/new/$', 'jade.inventory.views.new_purchase'),
    (r'^purchase/(?P<object_id>\d+)/pay/$', 'jade.inventory.views.add_payment_to_purchase'),
    
    # Transfers
    (r'^transfers/$', 'jade.inventory.views.list_transfers'),
    (r'^transfer/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_transfer'),
    (r'^transfer/new/$', 'jade.inventory.views.new_transfer'),
    
    # Equity
    (r'^equity_list/$', 'jade.inventory.views.list_equity'),
    (r'^equity/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_equity'),
    (r'^equity/new/$', 'jade.inventory.views.new_equity'),
    
    #Purchase Returns
    (r'^purchasereturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchasereturn'),
    (r'^purchasereturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_purchasereturn'),
    
    # Client Payments
    (r'^clientpayment/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientpayment'),
    (r'^clientpayment/new/$', 'jade.inventory.views.new_clientpayment'),
    
    # Client Refunds
    (r'^clientrefund/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientrefund'),
    (r'^clientrefund/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_clientrefund'),
    
    # Vendor Payments
    (r'^vendorpayment/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorpayment'),
    (r'^vendorpayment/new/$', 'jade.inventory.views.new_vendorpayment'),
    
    # Vendor Refunds
    (r'^vendorrefund/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorrefund'),
    (r'^vendorrefund/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_vendorrefund'),
    
    #Counts
    (r'^counts/$', 'jade.inventory.views.list_counts'),
    (r'^count/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_count'),
    (r'^count/new/$', 'jade.inventory.views.new_count'),
    (r'^count/(?P<object_id>\d+)/post/$', 'jade.inventory.views.post_count'),
    (r'^count/(?P<object_id>\d+)/post-as-sale/$', 'jade.inventory.views.post_count_as_sale'),
    (r'^count/(?P<doc_number>\w+)/sheet.pdf$', 'jade.inventory.views.count_sheet'),
    
    #Labels
    (r'^labels/(?P<doc_number>\w+).pdf$', 'jade.inventory.views.labels'),
    
    #Items
    (r'^items/$', 'jade.inventory.views.item_list'),
    (r'^items/low_stock/$', 'jade.inventory.views.low_stock'),
    (r'^item/$', 'jade.inventory.views.new_item'),
    (r'^services/$', 'jade.inventory.views.list_services'),
    (r'^service/$', 'jade.inventory.views.new_service'),
    (r'^service//$', 'jade.inventory.views.new_service'),
    (r'^item//$', 'jade.inventory.views.new_item'),
    (r'^items/prices.pdf$', 'jade.inventory.views.price_report'),
    (r'^items/inventory.pdf$', 'jade.inventory.views.inventory_report'),
    (r'^items/low_stock.pdf$', 'jade.inventory.views.low_stock_report'),
    (r'^item/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_item'),
    (r'^item/(?P<object_id>\d+)/image_upload/$', 'jade.inventory.views.item_image_upload'),
    (r'^item/edit/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_item'),
    (r'^item/(?P<object_id>\d+)/$', 'jade.inventory.views.item_show'),
        
    #Serials
    (r'^serial/(?P<serial>\w+)/$', 'jade.inventory.views.serial_history'),
    
    #Accounts    
    (r'^clients/$', 'jade.inventory.views.client_list'),
    (r'^accounts/$', 'jade.inventory.views.account_list'),
    (r'^vendors/$', 'jade.inventory.views.vendor_list'),
    (r'^account/(?P<object_id>\d+)/$', 'jade.inventory.views.account_show'),
    (r'^client/(?P<object_id>\d+)/$', 'jade.inventory.views.account_show'),
    (r'^vendor/(?P<object_id>\d+)/$', 'jade.inventory.views.account_show'),
    (r'^account/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_account'),
    (r'^client//$', 'jade.inventory.views.new_client'),
    (r'^vendor//$', 'jade.inventory.views.new_vendor'),
    (r'^account//$', 'jade.inventory.views.new_account'),
    (r'^client/$', 'jade.inventory.views.new_client'),
    (r'^vendor/$', 'jade.inventory.views.new_vendor'),
    (r'^account/$', 'jade.inventory.views.new_account'),
    (r'^account/(?P<object_id>\d+)/statement.pdf$', 'jade.inventory.views.account_statement'),

    #Prices
    (r'^prices/$', 'jade.inventory.views.price_list'),
    (r'^price/(?P<object_id>\d+)/$', 'jade.inventory.views.price_edit'),

    #Garantees
    (r'^clientgarantee/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientgarantee'),
    (r'^clientgarantee/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_clientgarantee'),
    
    (r'^vendorgarantee/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorgarantee'),
    (r'^vendorgarantee/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_vendorgarantee'),
    
    # GaranteeOffers
    (r'^garanteeoffer/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_garanteeoffer'),
    (r'^garanteeoffer/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_garanteeoffer'),
    (r'^garanteeoffer/new/$', 'jade.inventory.views.new_garanteeoffer'),
    (r'^garantee_price/$', 'jade.inventory.views.garantee_price'),
    
    # LinkedItems
    
    (r'^linkeditem/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_linkeditem'),
    (r'^linkeditem/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_linkeditem'),
    (r'^item/(?P<object_id>\d+)/addlinkeditem/$', 'jade.inventory.views.new_linkeditem'),
    
    # CashClosing
    (r'^transactions/close/$', 'jade.inventory.views.new_cash_closing'),
    (r'^cashclosing/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_cash_closing'),
    (r'^cashclosing/(?P<object_id>\d+)/report.pdf$', 'jade.inventory.views.cash_closing_report'),
    
    # Transactions
    (r'^transactions/movements.pdf$', 'jade.inventory.views.movements_report'),
    (r'^transactions/$', 'jade.inventory.views.transaction_list'),
    (r'^transaction/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_transaction'),
    (r'^transaction/(?P<object_id>\d+)/activate/$', 'jade.inventory.views.activate_transaction'),
    (r'^transaction/(?P<object_id>\d+)/deactivate/$', 'jade.inventory.views.deactivate_transaction'),
    (r'^transaction/(?P<object_id>\d+)/deliver/$', 'jade.inventory.views.deliver_transaction'),
    (r'^transaction/(?P<object_id>\d+)/undeliver/$', 'jade.inventory.views.undeliver_transaction'),
    (r'^transaction/(?P<object_id>\d+)/get/$', 'jade.inventory.views.get_transaction'),
    (r'^transaction/(?P<object_id>\d+)/edit/$', 'jade.inventory.views.get_transaction',{'edit_mode':True}),
)

