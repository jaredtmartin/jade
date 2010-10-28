$(document).ready(function(){
    jQuery(document).bind('keydown', 'f1',function (evt){window.location = '/inventory/item/'; return false; }); 
	jQuery(document).bind('keydown', 'f2',function (evt){window.location = '/inventory/client/'; return false; }); 
	jQuery(document).bind('keydown', 'f3',function (evt){window.location = '/inventory/vendor/'; return false; }); 
	jQuery(document).bind('keydown', 'f4',function (evt){window.location = '/inventory/sales/'; return false; }); 
	jQuery(document).bind('keydown', 'f5',function (evt){window.location = '/inventory/purchases/'; return false; }); 
	jQuery(document).bind('keydown', 'f6',function (evt){window.location = '/inventory/items/'; return false; }); 
	jQuery(document).bind('keydown', 'f7',function (evt){window.location = '/inventory/clients/'; return false; }); 
	jQuery(document).bind('keydown', 'f8',function (evt){window.location = '/inventory/vendors/'; return false; }); 
});
