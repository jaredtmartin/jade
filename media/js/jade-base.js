//# Jade Inventory Control System
//#Copyright (C) 2010  Jared T. Martin
//
//#    This program is free software: you can redistribute it and/or modify
//#    it under the terms of the GNU General Public License as published by
//#    the Free Software Foundation, either version 3 of the License, or
//#    (at your option) any later version.
//
//#    This program is distributed in the hope that it will be useful,
//#    but WITHOUT ANY WARRANTY; without even the implied account of
//#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#    GNU General Public License for more details.
//
//#    You should have received a copy of the GNU General Public License
//#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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



