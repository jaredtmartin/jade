function editobject(tipo, object_id) {
    $('#'+tipo+'-'+object_id+' .field').each(function(i){
        var input = '<td style="'+ $(this).attr('style') +'"><input id="'+ $(this).attr('id') +'" class="'+ $(this).attr('class') +'" value="'+$(this).attr('value')+'" name="'+ $(this).attr('name') +'" type="text"></td>'
        $(this).before(input).hide();
    });
    $('.datelookup').datepicker();
    $('.itemlookup').autocomplete('/inventory/item_list/', {matchSubset:0, autoFill:1,});
    $('.clientlookup').autocomplete('/inventory/client_list/', {matchSubset:0, autoFill:1,});
    $('.vendorlookup').autocomplete('/inventory/vendor_list/', {matchSubset:0, autoFill:1,});
    $('.employeelookup').autocomplete('/inventory/employee_list/', {matchSubset:0, autoFill:1,});
    $('.accountlookup').autocomplete('/inventory/account_list/', {matchSubset:0, autoFill:1,});
    $('.monthslookup').attr('onblur', 'getGaranteePrice('+object_id+')');
    $('#'+tipo+'-'+object_id).children().children('.field:visible').keydown(function(e){
        if (e.keyCode == 13) {
            $(this).parents('.'+tipo).children().children('.save').trigger('click');
            $('#item').select();
            e.preventDefault();
            return false;
        }
    });
    $('#'+tipo+'-'+object_id+' .showmode').hide();
    $('#'+tipo+'-'+object_id+' .editmode').show();
//    $('#'+tipo+'-'+object_id).children().children('.quantity:first').select();
}
function cancelTransaction(tipo,object_id) {
    $('#'+tipo+'-'+object_id+' .field').each(function(i){
        if (!$(this).attr('style')){
            $(this).parent().remove();
        }
    });
    $('#'+tipo+'-'+object_id+' .field').show();
    $('#'+tipo+'-'+object_id+' .showmode').show();
    $('#'+tipo+'-'+object_id+' .editmode').hide();
}
function saveTransaction(tipo, object_id, url, success) {
    if (!success){success=update}
    jQuery("#last_id").val(object_id);
    jQuery("#last_tipo").val(tipo);
    $.ajax({
        url: url ,
        type:'POST',
        data:{ 
            doc_number:     jQuery('#id_'+tipo+'-'+object_id+'-doc_number').val(),
            date:           jQuery('#id_'+tipo+'-'+object_id+'-date').val(),
            account:        jQuery('#id_'+tipo+'-'+object_id+'-account').val(),
            item:           jQuery('#id_'+tipo+'-'+object_id+'-item').val(),
            quantity:       jQuery('#id_'+tipo+'-'+object_id+'-quantity').val(),
            serial:         jQuery('#id_'+tipo+'-'+object_id+'-serial').val(),
            value:          jQuery('#id_'+tipo+'-'+object_id+'-value').val(),
            unit_value:     jQuery('#id_'+tipo+'-'+object_id+'-unit_value').val(),
            account2:        jQuery('#id_'+tipo+'-'+object_id+'-account2').val(),
        },
        success: success
    });
}
function update(data){
    $('.message').remove();
    object_id=jQuery("#last_id").val();
    tipo=jQuery("#last_tipo").val();
    section=jQuery("#last_section").val();
    $('#ajax-data').replaceWith('<div id="ajax-data" style="display: none;"></div>');
    var d = $('#ajax-data').append(data);
    $('.message', d).appendTo($('#messages')) //.hide().slideDown('slow');
    results=$('.'+tipo, d);
    results.each(function(i){
        if ($('#'+this.id+":visible").length>0){
            $('#'+this.id+":visible:first").replaceWith(this);
        } else {
            $('#'+section+'s').prepend(this);
            $('.'+section+'section').removeAttr('style')
        }
    });
}
function markTransaction(tipo, object_id, command) {
    jQuery("#last_id").val(object_id);
    jQuery("#last_tipo").val(tipo);
    url='/inventory/doctransaction/'+object_id+'/'+command+'/'
    $.ajax({
        url: url,
        type:'POST',
        success: update
    });
}
function deleteTransaction(tipo, object_id) {
    jQuery('#'+tipo+'-'+object_id).remove();
    $.ajax({
        url: '/inventory/transaction/'+object_id+'/delete/' ,
        type:'POST',
    });
}
function addObject(object_id, tipo, section, success){
    if (!success){success=updateAndSelect}
    jQuery("#last_id").val(object_id);
    jQuery("#last_tipo").val(tipo);
    jQuery("#last_section").val(section);
    $.ajax({
        url: '/inventory/'+tipo+'/'+object_id+'/create/',
        type:'POST',
        success: success
    });
}
function updateAndSelect(data){
    update(data);
    section=jQuery("#last_section").val();
    $('#'+section+'s .field:visible').keydown(function(e){
        if (e.keyCode == 13) {
            $(this).parents('tr').children().children('.save').trigger('click');
            e.preventDefault();
            return false;
        }
    });   
    window.location = '#'+section+'spot';
    $('#'+section+'s input.field:first').select();   
}

