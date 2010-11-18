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
    (r'^tax_group_list/$', 'jade.inventory.views.ajax_tax_group_list'),
    (r'^price_group_list/$', 'jade.inventory.views.ajax_price_group_list'),
    (r'^unit_list/$', 'jade.inventory.views.ajax_unit_list'),
    (r'^site_list/$', 'jade.inventory.views.ajax_site_list'),
    (r'^user_list/$', 'jade.inventory.views.ajax_user_list'),
    (r'^transaction_entry_list/(?P<object_id>\d+)/$', 'jade.inventory.views.ajax_transaction_entry_list'),
    (r'^set-language/$', 'jade.inventory.views.set_languages'),
    
    # Sales
    (r'^sales/$', 'jade.inventory.views.list_sales'),
    (r'^sale/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_sale'),
    (r'^sale/new/$', 'jade.inventory.views.new_sale'),
    (r'^sale/(?P<doc_number>\w+)/receipt.pdf$', 'jade.inventory.views.sale_receipt'),
    (r'^sale/(?P<doc_number>\w+)/garantee.pdf$', 'jade.inventory.views.garantee_report'),
    (r'^sale/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_sale'),
    (r'^sale/(?P<object_id>\d+)/pay/$', 'jade.inventory.views.add_payment_to_sale'),

    # Sale Returns
    (r'^salereturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_salereturn'),
    (r'^salereturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_salereturn'),
    (r'^salereturn/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_salereturn'),
    
    # Purchases
    (r'^purchases/$', 'jade.inventory.views.list_purchases'),
    (r'^purchase/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchase'),
    (r'^purchase/new/$', 'jade.inventory.views.new_purchase'),
    (r'^purchase/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_purchase'),
    (r'^purchase/(?P<object_id>\d+)/pay/$', 'jade.inventory.views.add_payment_to_purchase'),
    
    # Transfers
    (r'^transfers/$', 'jade.inventory.views.list_transfers'),
    (r'^transfer/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_transfer'),
    (r'^transfer/new/$', 'jade.inventory.views.new_transfer'),
    (r'^transfer/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_transfer'),
    
    # Accounting
    (r'^accounting/$', 'jade.inventory.views.list_accounting'),
    (r'^accounting/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_accounting'),
    (r'^accounting/new/$', 'jade.inventory.views.new_accounting'),
    (r'^accounting/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_accounting'),
    
    #Purchase Returns
    (r'^purchasereturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchasereturn'),
    (r'^purchasereturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_purchasereturn'),
    (r'^purchasereturn/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_purchasereturn'),
    
    # Client Payments
    (r'^clientpayment/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientpayment'),
    (r'^clientpayment/new/$', 'jade.inventory.views.new_clientpayment'),
    (r'^clientpayment/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_clientpayment'),
    
    # Client Refunds
    (r'^clientrefund/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientrefund'),
    (r'^clientrefund/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_clientrefund'),
    (r'^clientrefund/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_clientrefund'),
    
    # Vendor Payments
    (r'^vendorpayment/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorpayment'),
    (r'^vendorpayment/new/$', 'jade.inventory.views.new_vendorpayment'),
    (r'^vendorpayment/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_vendorpayment'),
    
    # Vendor Refunds
    (r'^vendorrefund/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorrefund'),
    (r'^vendorrefund/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_vendorrefund'),
    (r'^vendorrefund/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_vendorrefund'),
    
    #Counts
    (r'^counts/$', 'jade.inventory.views.list_counts'),
    (r'^count/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_count'),
    (r'^count/new/$', 'jade.inventory.views.new_count'),
    (r'^count/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_count'),
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
    (r'^clientgarantee/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_clientgarantee'),
    (r'^clientgarantee/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientgarantee'),
    (r'^clientgarantee/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_clientgarantee'),
    
    (r'^vendorgarantee/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_vendorgarantee'),
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
    
    # Transactions
    (r'^transactions/movements.pdf$', 'jade.inventory.views.movements_report'),
    (r'^transactions/corte.pdf$', 'jade.inventory.views.corte'),
    (r'^transactions/$', 'jade.inventory.views.transaction_list'),
    (r'^transaction/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_transaction'),
    (r'^transaction/(?P<object_id>\d+)/activate/$', 'jade.inventory.views.activate_transaction'),
    (r'^transaction/(?P<object_id>\d+)/deactivate/$', 'jade.inventory.views.deactivate_transaction'),
    (r'^transaction/(?P<object_id>\d+)/deliver/$', 'jade.inventory.views.deliver_transaction'),
    (r'^transaction/(?P<object_id>\d+)/undeliver/$', 'jade.inventory.views.undeliver_transaction'),
    (r'^transaction/(?P<object_id>\d+)/get/$', 'jade.inventory.views.get_transaction'),
    (r'^transaction/(?P<object_id>\d+)/edit/$', 'jade.inventory.views.get_transaction',{'edit_mode':True}),
)

