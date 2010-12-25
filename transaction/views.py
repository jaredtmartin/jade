from django.views.generic import create_update, list_detail
from jade.common.views import object_detail, lookup_object, update_object, process_form, process_formset, show_update_results
from jade.transaction.models import Sale, SaleLine
from jade.transaction.forms import SaleLineFormSet, SaleForm, SaleLineForm, NewSaleLineForm
from jade.common.widgets import DeleteCheckBox
from django.forms.fields import BooleanField
from django.utils.translation import ugettext as _
from django.forms.formsets import DELETION_FIELD_NAME
 
def sale_detail(request, object_id):
    obj, model, form=process_form(request, form_class=SaleForm, object_id=object_id)
    object_list, linemodel, saleline_formset=process_formset(request, formset_class=SaleLineFormSet, queryset=SaleLine.objects.filter(document=obj))
    new_saleline_form=NewSaleLineForm()
    return show_update_results(request, model, context={'obj':obj, 'form':form, 'lines':object_list, 'saleline_formset':saleline_formset, 'new_saleline_form':new_saleline_form}, template_name=None)

def saleline_new(request, object_id):
    form=NewSaleLineForm(request.POST)
    if form.is_valid():
        formset_id = form.cleaned_data['formset_id']
        item = form.cleaned_data['item']
        obj=lookup_object(Sale, object_id)
        form=SaleLineForm(instance=SaleLine(document=obj, item=item), formset_id=formset_id)
        form.fields[DELETION_FIELD_NAME] = BooleanField(widget=DeleteCheckBox(), label=_(u'Delete'), required=False)
        form.group=form.prefix
        form.prefix = "%s-%s" % (form.prefix, formset_id)    
    return show_update_results(request, SaleLine, context={'form':form}, template_name='transaction/saleline_new.html')
