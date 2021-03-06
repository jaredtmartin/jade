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
function editTransaction(object_id) {
    if ($('#transaction-'+object_id).attr('tipo') == 'sale'){$('#last_sale').val(object_id);}
    $('#transaction-'+object_id+' .field').each(function(i){
        var input = '<td style="'+ $(this).attr('style') +'"><input id="'+ $(this).attr('id') +'" class="'+ $(this).attr('class') +'" value="'+$(this).attr('value')+'" name="'+ $(this).attr('name') +'" type="text"></td>'
        $(this).before(input).removeClass('Inventory').hide();
    });
    $('#id_transaction-'+object_id+'-date').datepicker($.datepicker.regional[ $("#lang-code").val()]);
    $('#id_transaction-'+object_id+'-item').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.client').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.vendor').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.employee').autocomplete('/inventory/employee_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account2.accounting').autocomplete('/inventory/account_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.accounting').autocomplete('/inventory/account_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-garantee_months').attr('onblur', 'getGaranteePrice('+object_id+')');
    $('#transaction-'+object_id).children().children('.field:visible').keydown(function(e){
        if (e.keyCode == 13) {
            $(this).parents('.transaction').children().children('.save').trigger('click');
            $('#item').select();
            e.preventDefault();
            return false;
        }
    });    
    $('#transaction-'+object_id+' .show').hide();
    $('#transaction-'+object_id+' .edit').show();
    $('#transaction-'+object_id).children().children('.quantity:first').select();
}
function getTransaction(object_id, url){
    jQuery("#last_id").val(object_id);
    if ($('#transaction-'+object_id).attr('tipo') == 'sale'){$('#last_sale').val(object_id);}
    $.ajax({
        url: url ,
        type:'POST',
        success: updateAndSelectQuantity
    });
}

function addGarantee(object_id, tipo){
    jQuery("#last_id").val(object_id);
    $.ajax({
        url: '/inventory/'+tipo+'/'+object_id+'/new/' ,
        type:'POST',
        success: updateTransaction
    });
}

function saveTransaction(object_id, url) {
    jQuery("#transaction-"+object_id+"-entries-table").remove();
    hide_entries(object_id);
    jQuery("#last_id").val(object_id);
    $.ajax({
        url: url ,
        type:'POST',
        data:{ 
            doc_number:     jQuery('#id_transaction-'+object_id+'-doc_number').val(),
            date:           jQuery('#id_transaction-'+object_id+'-date').val(),
            account:        jQuery('#id_transaction-'+object_id+'-account').val(),
            item:           jQuery('#id_transaction-'+object_id+'-item').val(),
            quantity:       jQuery('#id_transaction-'+object_id+'-quantity').val(),
            serial:         jQuery('#id_transaction-'+object_id+'-serial').val(),
            value:          jQuery('#id_transaction-'+object_id+'-value').val(),
            unit_value:     jQuery('#id_transaction-'+object_id+'-unit_value').val(),
            account2:        jQuery('#id_transaction-'+object_id+'-account2').val(),
        },
        success: updateAndSelectItemField
    });
}

function updateTransaction(data){
    update('transaction',data);
// Enableing the following will cause the page to show edit buttons even though edit_mode is 
// activated for the get_transaction view (BAD)
//    if ($('.error').length==0){
//        $('#transaction-'+object_id+' .show').show();
//        $('#transaction-'+object_id+' .edit').hide();
//    }
    $('.transaction:first').children().children('.field:visible').keydown(function(e){
        if (e.keyCode == 13) {
            $(this).parents('.transaction').children().children('.save').trigger('click');
            e.preventDefault();
            return false;
        }
    });    
}
function updateAndSelectQuantity(data){
    object_id=jQuery("#last_id").val();
    updateTransaction(data)
    
    jQuery('.ui-dialog-content:visible').children().children('#doc_number').val(jQuery('.doc_number:first').val());
//    jQuery('#doc_number').val(jQuery('.doc_number:first').val());
    if (object_id=="None") { 
            $('.quantity:first').select();
    }else {
        $('#transaction-'+object_id).children().children('.quantity:first').select();
    }
}
function updateAndSelectItemField(data){
    updateTransaction(data)
    $('#item.ac_input').select();
}
function cancelTransaction(object_id) {
    $('#transaction-'+object_id+' .field').each(function(i){
        if (!$(this).attr('style')){
            $(this).parent().remove();
        }
    });
    $('#transaction-'+object_id+' .field').show();
    $('#transaction-'+object_id+' .show').show();
    $('#transaction-'+object_id+' .edit').hide();
}
function newTransaction(url) {
    jQuery("#last_id").val("None");
    $.ajax({
        url: url,
        type:'POST',
        data:{
            doc_number: jQuery('.ui-dialog-content:visible').children().children('#doc_number').val(),
            client:     jQuery('#client.ac_input').val(),
            vendor:     jQuery('#vendor.ac_input').val(),
            value:     jQuery('.ui-dialog-content:visible').children().children('#value').val(),
            item:     jQuery('#item.ac_input').val(),
        },
        success: updateAndSelectQuantity
    });
}
function markTransaction(url) {
    $.ajax({
        url: url,
        type:'POST',
        success: updateTransaction
    });
}
function deleteTransaction(object_id) {
    jQuery("#transaction-"+object_id+"-entries-table").remove();
    hide_entries(object_id);
    jQuery("#last_id").val(object_id);
    $.ajax({
        url: '/inventory/transaction/'+object_id+'/delete/' ,
        type:'POST',
        data:{ 
            doc_number:     jQuery('#doc_number').val()
        },
        success: removeTransaction
    });
}
function removeTransaction(object_id) {
    object_id=jQuery("#last_id").val();
    jQuery('#transaction-'+object_id).remove();
}
function get_entries(object_id){
    jQuery("#last_id").val(object_id);
    jQuery.get( '/inventory/transaction_entry_list/'+object_id, {}, insert_entries);
    
}
function insert_entries(data){
    object_id=jQuery("#last_id").val();
    jQuery('#transaction-'+object_id).after(data);
    jQuery('#hide_entries_link_'+object_id).show();
    jQuery('#show_entries_link_'+object_id).hide();
}
function show_entries(object_id){
    if (jQuery('#transaction-'+object_id+'-entries-table').length == 0){
        get_entries(object_id);
    } else {
        jQuery('#transaction-'+object_id+'-entries-table').show();
        jQuery('#transaction-'+object_id+'-costs-table').show();
    }
    jQuery('#hide_entries_link_'+object_id).show();
    jQuery('#show_entries_link_'+object_id).hide();
}
function hide_entries(object_id){
    jQuery('#transaction-'+object_id+'-entries-table').hide();
    jQuery('#transaction-'+object_id+'-costs-table').hide();
    jQuery('#hide_entries_link_'+object_id).hide();
    jQuery('#show_entries_link_'+object_id).show();
}
function getGaranteePrice(object_id) {
    jQuery("#last_id").val(object_id);
    $.ajax({
        url: '/inventory/garantee_price/',
        type:'GET',
        data:{ 
            item:     jQuery('#id_transaction-'+object_id+'-item').val(),
            months:     jQuery('#id_transaction-'+object_id+'-garantee_months').val(),
        },
        success: updateGaranteePrice,
    });
}
function updateTotal(x){
    results=$('.'+x);
    total=0
    count=0;
    do {
        if (parseFloat($(results[count]).attr('totalvalue'))){
            total += parseFloat($(results[count]).attr('totalvalue'));
        }
        count++;
    } while (count < results.length);
//    results.each(function(i){
//        total+=this.attr('totalvalue');
//    });
    if ($('#'+x).length>0){
        old=$('#'+x).html().split('$');
        $('#'+x).html(old[0]+'$'+total.toFixed(2));
    }
}
function updateTotals(){
    updateTotal('value');
}
function update(prefix, data){
    $('.message').remove();
    object_id=jQuery("#last_id").val();
    $('#ajax-data').replaceWith('<div id="ajax-data" style="display: none;"></div>');
    var d = $('#ajax-data').append(data);
    $('.message', d).appendTo($('#messages')) //.hide().slideDown('slow');
    results=$('.'+prefix, d);
    results.each(function(i){
        if ($('#'+this.id+":visible").length>0){
            $('#'+this.id+":visible:first").replaceWith(this);
            $('#id_transaction-'+object_id+'-date').datepicker($.datepicker.regional[ $("#lang-code").val()]);
            $('#id_transaction-'+object_id+'-item').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
            $('#id_transaction-'+object_id+'-account.client').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
            $('#id_transaction-'+object_id+'-account.vendor').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
            $('#id_transaction-'+object_id+'-account.employee').autocomplete('/inventory/employee_list/', {matchSubset:0, autoFill:1,});
        } else {
            $('#'+prefix+'s').prepend(this);
            $('.date:first').datepicker($.datepicker.regional[ $("#lang-code").val() ]);
            $('.item:first').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
            $('.account:first.client').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
            $('.account:first.vendor').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
            $('.account:first.employee').autocomplete('/inventory/employee_list/', {matchSubset:0, autoFill:1,});
            if ($('.transaction:first').attr('tipo') == 'sale'){$('#last_sale').val($('.transaction:first').attr('transaction_id'));}
        }
    });
    if ($('.error').length==0){
        $('.new').remove();
        updateTotals();
    }
}
function updateGaranteePrice(data){
    object_id=jQuery("#last_id").val();
    $('.message').remove();
    $('#ajax-data').replaceWith('<div id="ajax-data" style="display: none;"></div>');
    var d = $('#ajax-data').append(data)
    $('.message', d).appendTo($('#messages')) //.hide().slideDown('slow');
    value=$('#value', d).html();
    jQuery('#id_transaction-'+object_id+'-garantee_unit_value').val(value)
}
function postCount(object_id){
    hide_entries(object_id);
    jQuery("#transaction-"+object_id+"-entries-table").remove();
    jQuery("#last_id").val(object_id);
    $.ajax({
        url: '/inventory/count/'+object_id+'/post/',
        type:'POST',
        success: updateTransaction
    });
}
