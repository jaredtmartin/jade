function editTransaction(object_id) {
    $('#transaction-'+object_id+' .field').each(function(i){
        var input = '<td style="'+ $(this).attr('style') +'"><input id="'+ $(this).attr('id') +'" class="'+ $(this).attr('class') +'" value="'+$(this).attr('value')+'" name="'+ $(this).attr('name') +'" type="text"></td>'
        $(this).before(input).removeClass('Inventory').hide();
    });
    $('#id_transaction-'+object_id+'-date').datepicker();
    $('#id_transaction-'+object_id+'-item').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.client').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.vendor').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account2.accounting').autocomplete('/inventory/account_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-account.accounting').autocomplete('/inventory/account_list/', {matchSubset:0, autoFill:1,});
    $('#id_transaction-'+object_id+'-garantee_months').attr('onblur', 'getGaranteePrice('+object_id+')');
    $('.transaction:first').children().children('.field:visible').keydown(function(e){
        if (e.keyCode == 13) {
            $(this).parents('.transaction').children().children('.save').trigger('click');
            $('#item').select();
            e.preventDefault();
            return false;
        }
    });    
    $('#transaction-'+object_id+' .show').hide();
    $('#transaction-'+object_id+' .edit').show();
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
            cost:           jQuery('#id_transaction-'+object_id+'-cost').val(),
            tax:            jQuery('#id_transaction-'+object_id+'-tax').val(),
            unit_tax:       jQuery('#id_transaction-'+object_id+'-unit_tax').val(),
            unit_cost:      jQuery('#id_transaction-'+object_id+'-unit_cost').val(),
            unit_discount:  jQuery('#id_transaction-'+object_id+'-unit_discount').val(),
            unit_price:     jQuery('#id_transaction-'+object_id+'-unit_price').val(),
            account2:        jQuery('#id_transaction-'+object_id+'-account2').val(),
        },
        success: updateAndSelectItemField
    });
}

function updateTransaction(data){
    update('transaction',data);
    if ($('.error').length==0){
        $('#transaction-'+object_id+' .show').show();
        $('#transaction-'+object_id+' .edit').hide();
    }
    $('.transaction:first').children().children('.field:visible').keydown(function(e){
        if (e.keyCode == 13) {
            $(this).parents('.transaction').children().children('.save').trigger('click');
            e.preventDefault();
            return false;
        }
    });    
}
function updateAndSelectQuantity(data){
    updateTransaction(data)
    jQuery('#doc_number').val(jQuery('.doc_number:first').val());
    $('.quantity:first').select();
}
function updateAndSelectItemField(data){
    updateTransaction(data)
//    $('#item.ac_input').select();
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
    $.ajax({
        url: url,
        type:'POST',
        data:{
            doc_number:     jQuery('#doc_number').val(),
            client:     jQuery('#client.ac_input').val(),
            vendor:     jQuery('#vendor.ac_input').val(),
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
        success: updateGaranteePrice
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
    updateTotal('charge');
    updateTotal('cost');
    updateTotal('discount');
    updateTotal('tax');
    updateTotal('price');
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
            $('#id_transaction-'+object_id+'-date').datepicker();
            $('#id_transaction-'+object_id+'-item').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
            $('#id_transaction-'+object_id+'-account.client').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
            $('#id_transaction-'+object_id+'-account.vendor').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
        } else {
            $('#'+prefix+'s').prepend(this);
            $('.date:first').datepicker();
            $('.item:first').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
//            $('.account:first').autocomplete('/inventory/account_list/', {matchSubset:0, autoFill:1,});
            $('.account:first.client').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
            $('.account:first.vendor').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
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
    price=$('#price', d).html();
    jQuery('#id_transaction-'+object_id+'-garantee_unit_price').val(price)
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

