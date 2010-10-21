from django.conf.urls.defaults import *
from jade.inventory.models import Sale, Purchase, Item, Account, Client, Vendor
from django.views.generic import list_detail, create_update

item={'model' : Item, 'post_save_redirect':'/inventory/items', 'template_name':'inventory/item_show.html'}

urlpatterns = patterns('',
    # ajax lists    
    (r'^client_list/$', 'jade.inventory.views.ajax_client_list', "ajax_client_list"),
    (r'^vendor_list/$', 'jade.inventory.views.ajax_vendor_list', "ajax_vendor_list"),
    (r'^account_list/$', 'jade.inventory.views.ajax_account_list', "ajax_account_list"),
    (r'^item_list/$', 'jade.inventory.views.ajax_item_list', "ajax_item_list"),
    (r'^tax_group_list/$', 'jade.inventory.views.ajax_tax_group_list', "ajax_tax_group_list"),
    (r'^price_group_list/$', 'jade.inventory.views.ajax_price_group_list', "ajax_price_group_list"),
    (r'^unit_list/$', 'jade.inventory.views.ajax_unit_list', "ajax_unit_list"),
    (r'^site_list/$', 'jade.inventory.views.ajax_site_list', "ajax_site_list"),
    (r'^user_list/$', 'jade.inventory.views.ajax_user_list', "ajax_user_list"),
    (r'^transaction_entry_list/(?P<object_id>\d+)/$', 'jade.inventory.views.ajax_transaction_entry_list', "ajax_transaction_entry_list"),
    (r'^set-language/$', 'jade.inventory.views.set_languages', "ajax_set-language"),
    
    # Sales
    (r'^sales/$', 'jade.inventory.views.list_sales'),
    (r'^sale/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_sale','edit_sale'),
    (r'^sale/new/$', 'jade.inventory.views.new_sale','new_sale'),
    (r'^sale/(?P<doc_number>\w+)/receipt.pdf$', 'jade.inventory.views.sale_receipt','sale_receipt'),
    (r'^sale/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_sale','delete_sale'),
    (r'^sale/(?P<object_id>\d+)/pay/$', 'jade.inventory.views.add_payment_to_sale','add_payment_to_sale'),

    # Sale Returns
    (r'^salereturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_salereturn','edit_sale_return'),
    (r'^salereturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_salereturn','new_sale_return'),
    (r'^salereturn/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_salereturn','delete_sale_return'),
    
    # Purchases
    (r'^purchases/$', 'jade.inventory.views.list_purchases','list_purchases'),
    (r'^purchase/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchase','edit_purchase'),
    (r'^purchase/new/$', 'jade.inventory.views.new_purchase','new_purchase'),
    (r'^purchase/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_purchase','delete_purchase'),
    (r'^purchase/(?P<object_id>\d+)/pay/$', 'jade.inventory.views.add_payment_to_purchase','add_payment_to_purchase'),
    
    # Transfers
    (r'^transfers/$', 'jade.inventory.views.list_transfers','list_transfers'),
    (r'^transfer/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_transfer','edit_transfer'),
    (r'^transfer/new/$', 'jade.inventory.views.new_transfer','new_transfer'),
    (r'^transfer/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_transfer','delete_transfer'),
    
    #Transfer Returns
#    (r'^transferreturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_transferreturn'),
#    (r'^transferreturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_transferreturn'),
#    (r'^transferreturn/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_transferreturn'),
    
    #Purchase Returns
    (r'^purchasereturn/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_purchasereturn','edit_purchase_return'),
    (r'^purchasereturn/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_purchasereturn','new_purchase_return'),
    (r'^purchasereturn/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_purchasereturn','delete_purchase_return'),
    
    # Client Payments
    (r'^clientpayment/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientpayment','edit_client_payment'),
    (r'^clientpayment/new/$', 'jade.inventory.views.new_clientpayment','new_client_payment'),
    (r'^clientpayment/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_clientpayment','delete_client_payment'),
    
    # Client Refunds
    (r'^clientrefund/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientrefund','edit_client_refund'),
    (r'^clientrefund/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_clientrefund','new_client_refund'),
    (r'^clientrefund/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_clientrefund','delete_client_refund'),
    
    # Vendor Payments
    (r'^vendorpayment/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorpayment','edit_vendor_payment'),
    (r'^vendorpayment/new/$', 'jade.inventory.views.new_vendorpayment','new_vendor_payment'),
    (r'^vendorpayment/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_vendorpayment','delete_vendor_payment'),
    
    # Vendor Refunds
    (r'^vendorrefund/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorrefund','edit_vendor_refund'),
    (r'^vendorrefund/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_vendorrefund','new_vendor_refund'),
    (r'^vendorrefund/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_vendorrefund','delete_vendor_refund'),
    
    #Counts
    (r'^counts/$', 'jade.inventory.views.list_counts','list_counts'),
    (r'^count/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_count','edit_count'),
    (r'^count/new/$', 'jade.inventory.views.new_count','new_count'),
    (r'^count/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_count','delete_count'),
    (r'^count/(?P<object_id>\d+)/post/$', 'jade.inventory.views.post_count','post_count'),
    (r'^count/(?P<doc_number>\w+)/sheet.pdf$', 'jade.inventory.views.count_sheet','count_sheet'),
    
    #Labels
    (r'^labels/(?P<doc_number>\w+).pdf$', 'jade.inventory.views.labels','labels'),
    
    #Items
    (r'^items/$', 'jade.inventory.views.item_list','item_list'),
#    (r'^item/$', create_update.create_object, item),
    (r'^item/$', 'jade.inventory.views.new_item','new_item'),
    (r'^item//$', 'jade.inventory.views.new_item'),
    (r'^items/prices.pdf$', 'jade.inventory.views.price_report','price_report'),
    (r'^items/inventory.pdf$', 'jade.inventory.views.inventory_report','inventory_report'),
    (r'^item/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_item','delete_item'),
    (r'^item/(?P<object_id>\d+)/image_upload/$', 'jade.inventory.views.item_image_upload','item_image_upload'),
#    (r'^item/edit/(?P<object_id>\d+)/$', create_update.update_object, item),
    (r'^item/edit/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_item','edit_item'),

    (r'^item/(?P<object_id>\d+)/$', 'jade.inventory.views.item_show','item_show'),
        
    #Serials
    (r'^serial/(?P<serial>\w+)/$', 'jade.inventory.views.serial_history','serial_history'),
    
    #Accounts    
    (r'^clients/$', 'jade.inventory.views.client_list','client_list'),
    (r'^accounts/$', 'jade.inventory.views.account_list','account_list'),
    (r'^vendors/$', 'jade.inventory.views.vendor_list','vendor_list'),
    (r'^account/(?P<object_id>\d+)/$', 'jade.inventory.views.account_show','account_show'),
    (r'^client/(?P<object_id>\d+)/$', 'jade.inventory.views.account_show','client_show'),
    (r'^vendor/(?P<object_id>\d+)/$', 'jade.inventory.views.account_show','vendor_show'),
    (r'^account/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_account','delete_account'),
    (r'^client//$', 'jade.inventory.views.new_client'),
    (r'^vendor//$', 'jade.inventory.views.new_vendor'),
    (r'^account//$', 'jade.inventory.views.new_account'),
    (r'^client/$', 'jade.inventory.views.new_client','new_client'),
    (r'^vendor/$', 'jade.inventory.views.new_vendor','new_vendor'),
    (r'^account/$', 'jade.inventory.views.new_account','new_account'),
    (r'^account/(?P<object_id>\d+)/statement.pdf$', 'jade.inventory.views.account_statement','account_statement'),
    
#    (r'^account/edit/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_account'),

    #Prices
    (r'^prices/$', 'jade.inventory.views.price_list','price_list'),
    (r'^price/(?P<object_id>\d+)/$', 'jade.inventory.views.price_edit','price_edit'),

    #Garantees
    (r'^clientgarantee/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_clientgarantee','delete_client_garantee'),
    (r'^clientgarantee/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_clientgarantee','edit_client_garantee'),
    (r'^clientgarantee/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_clientgarantee','new_client_garantee'),
    
    (r'^vendorgarantee/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_vendorgarantee','delete_vendor_garantee'),
    (r'^vendorgarantee/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_vendorgarantee','edit_vendor_garantee'),
    (r'^vendorgarantee/(?P<object_id>\d+)/new/$', 'jade.inventory.views.new_vendorgarantee','new_vendor_garantee'),
    
    # GaranteeOffers
    (r'^garanteeoffer/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_garanteeoffer','delete_garantee_offer'),
    (r'^garanteeoffer/(?P<object_id>\d+)/$', 'jade.inventory.views.edit_garanteeoffer','edit_garanteeoffer'),
    (r'^garanteeoffer/new/$', 'jade.inventory.views.new_garanteeoffer','new_garanteeoffer'),
    (r'^garantee_price/$', 'jade.inventory.views.garantee_price','garantee_price'),
    
    # Transactions
    (r'^transactions/movements.pdf$', 'jade.inventory.views.movements_report','movements_report'),
    (r'^transactions/corte.pdf$', 'jade.inventory.views.corte','corte'),
    (r'^transactions/$', 'jade.inventory.views.transaction_list','transaction_list'),
    (r'^transaction/(?P<object_id>\d+)/delete/$', 'jade.inventory.views.delete_transaction','delete_transaction'),
    (r'^transaction/(?P<object_id>\d+)/activate/$', 'jade.inventory.views.activate_transaction','activate_transaction'),
    (r'^transaction/(?P<object_id>\d+)/deactivate/$', 'jade.inventory.views.deactivate_transaction','deactivate_transaction'),
    (r'^transaction/(?P<object_id>\d+)/deliver/$', 'jade.inventory.views.deliver_transaction','deliver_transaction'),
    (r'^transaction/(?P<object_id>\d+)/undeliver/$', 'jade.inventory.views.undeliver_transaction','undeliver_transaction'),

)

