$(document).ready(function(){
    jQuery(document).bind('keydown', 'f1',function (evt){window.location = '/inventory/item/'; return false; }); 
	jQuery(document).bind('keydown', 'f2',function (evt){window.location = '/inventory/client/'; return false; }); 
	jQuery(document).bind('keydown', 'f3',function (evt){window.location = '/inventory/vendor/'; return false; }); 
	jQuery(document).bind('keydown', 'f4',function (evt){window.location = '/inventory/sales/'; return false; }); 
	jQuery(document).bind('keydown', 'f5',function (evt){window.location = '/inventory/purchases/'; return false; }); 
	jQuery(document).bind('keydown', 'f6',function (evt){getTaxForm($('#last_sale').val(),'saletax'); return false; }); 
	jQuery(document).bind('keydown', 'f7',function (evt){jQuery('#last_id').val($('#last_sale').val()); $('#discount-form').dialog('open'); return false; }); 
	jQuery(document).bind('keydown', 'f8',function (evt){newTransaction('/inventory/sale/'+$('#last_sale').val()+'/pay/'); return false; }); 
	jQuery(document).bind('keydown', 'f9',function (evt){addGarantee($('#last_sale').val(),'clientgarantee'); return false; }); 
	jQuery(document).bind('keydown', 'f10',function (evt){newTransaction('/inventory/salereturn/'+$('#last_sale').val()+'/new/'); return false; }); 
});



