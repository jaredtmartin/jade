from jade.inventory.models import *
from django.contrib import admin
from django import forms
from jade.inventory.widgets import *
class SaleAdminForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],widget=CalanderInput(), required=False)
    client = forms.CharField(widget=AutoCompleteInput(url="/inventory/client_list/"), required=False)
    item = forms.CharField(widget=AutoCompleteInput(url="/inventory/item_list/"), required=False)
    quantity = forms.DecimalField(required=False)
    cost = forms.DecimalField(required=False)
    serial = forms.CharField(required=False)
    unit_value = forms.DecimalField(required=False)
    unit_tax = forms.DecimalField(required=False)
    unit_discount = forms.DecimalField(required=False)
    class Meta:
        model = Sale
        exclude=('tipo',)
    def __init__(self, *args, **kwargs):
        super(SaleAdminForm, self).__init__(*args, **kwargs)
        # Set the form fields based on the model object
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['date'] = datetime.strftime((instance.date or datetime.now()), '%d/%m/%Y')
            self.initial['client'] = instance.client
            self.initial['unit_value'] = instance.unit_value
            self.initial['quantity'] = instance.quantity
            self.initial['item'] = instance.item
            self.initial['cost'] = instance.cost
            self.initial['serial'] = instance.serial
    def save(self, commit=True):
        model = super(SaleAdminForm, self).save(commit=False)
        model.date = self.cleaned_data['date']
        model.client = self.cleaned_data['client']
        model.quantity = self.cleaned_data['quantity'] or 0
        model.item = self.cleaned_data['item']
        model.cost = self.cleaned_data['cost']
        model.serial = self.cleaned_data['serial']
        model.price = self.cleaned_data['unit_value']
        if model.quantity!=0: 
            model.value=model.value*model.quantity
        if commit:
            model.save()
        return model
    def clean_item(self):
        if (not self.cleaned_data['item']) and (not self.fields['item'].required): return None
        try:
            item=Item.objects.get(bar_code=self.cleaned_data['item'])  
        except Item.DoesNotExist:
            try:
                item=Item.objects.filter(name__icontains=self.cleaned_data['item'])[0]
            except:
                raise forms.ValidationError("The item specified is not valid")
        return item
    def clean_client(self):
        if not self.cleaned_data['client'] and not self.fields['client'].required: return None
        try: return Account.objects.filter(name=self.cleaned_data['client'], tipo='Client')[0]
        except: raise forms.ValidationError("The client specified is not valid")
class PurchaseAdminForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],widget=CalanderInput(), required=False)
    vendor = forms.CharField(widget=AutoCompleteInput(url="/inventory/vendor_list/"), required=False)
    item = forms.CharField(widget=AutoCompleteInput(url="/inventory/item_list/"), required=False)
    quantity = forms.DecimalField(required=False)
    value = forms.DecimalField(required=False)
    serial = forms.CharField(required=False)
    class Meta:
        model = Purchase
        exclude=('tipo',)
    def __init__(self, *args, **kwargs):
        super(PurchaseAdminForm, self).__init__(*args, **kwargs)
        # Set the form fields based on the model object
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['date'] = instance.date
            self.initial['vendor'] = instance.vendor
            self.initial['item'] = instance.item
            self.initial['quantity'] = instance.quantity
            self.initial['value'] = instance.value
            self.initial['serial'] = instance.serial
    def save(self, commit=True):
        model = super(PurchaseAdminForm, self).save(commit=False)
        model.date = self.cleaned_data['date']
        model.vendor = self.cleaned_data['vendor']
        model.item = self.cleaned_data['item']
        model.quantity = self.cleaned_data['quantity'] or 0
        model.value = self.cleaned_data['value']
        model.serial = self.cleaned_data['serial']
        if commit:
            model.save()
        return model
    def clean_item(self):
        if (not self.cleaned_data['item']) and (not self.fields['item'].required): return None
        try:
            item=Item.objects.get(bar_code=self.cleaned_data['item'])  
        except Item.DoesNotExist:
            try:
                item=Item.objects.filter(name__icontains=self.cleaned_data['item'])[0]
            except:
                raise forms.ValidationError("The item specified is not valid")
        return item
    def clean_vendor(self):
        if not self.cleaned_data['vendor'] and not self.fields['vendor'].required: return None
        try: return Account.objects.filter(name=self.cleaned_data['vendor'], tipo='Vendor')[0]
        except: raise forms.ValidationError("The vendor specified is not valid")
class CountAdminForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],widget=CalanderInput(), required=False)
    item = forms.CharField(widget=AutoCompleteInput(url="/inventory/item_list/"), required=False)
    quantity = forms.DecimalField(required=False)
    count = forms.DecimalField(required=False)
    value = forms.DecimalField(required=False)
    serial = forms.CharField(required=False)
    class Meta:
        model = Count
        exclude=('tipo',)
    def __init__(self, *args, **kwargs):
        super(CountAdminForm, self).__init__(*args, **kwargs)
        # Set the form fields based on the model object
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['date'] = instance.date
            self.initial['count'] = instance.count
            self.initial['item'] = instance.item
            self.initial['quantity'] = instance.quantity
            self.initial['value'] = instance.value
            self.initial['serial'] = instance.serial
    def save(self, commit=True):
        model = super(CountAdminForm, self).save(commit=False)
        model.date = self.cleaned_data['date']
        model.count = self.cleaned_data['count']
        model.item = self.cleaned_data['item']
        model.quantity = self.cleaned_data['quantity'] or 0
        model.value = self.cleaned_data['value']
        model.serial = self.cleaned_data['serial']
        if commit:
            model.save()
        return model
    def clean_item(self):
        if (not self.cleaned_data['item']) and (not self.fields['item'].required): return None
        try:
            item=Item.objects.get(bar_code=self.cleaned_data['item'])  
        except Item.DoesNotExist:
            try:
                item=Item.objects.filter(name__icontains=self.cleaned_data['item'])[0]
            except:
                raise forms.ValidationError("The item specified is not valid")
        return item
        
class PaymentAdminForm(forms.ModelForm):
    date = forms.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],widget=CalanderInput(), required=False)
    dest= forms.CharField(widget=AutoCompleteInput(url="/inventory/account_list/"), required=False)
    source= forms.CharField(widget=AutoCompleteInput(url="/inventory/account_list/"), required=False)
    value = forms.DecimalField(required=False)
    class Meta:
        model = Payment
        exclude=('tipo',)
    def __init__(self, *args, **kwargs):
        super(PaymentAdminForm, self).__init__(*args, **kwargs)
        # Set the form fields based on the model object
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['date'] = instance.date
            self.initial['dest'] = instance.dest
            self.initial['source'] = instance.source
            self.initial['value'] = instance.value
    def save(self, commit=True):
        model = super(PaymentAdminForm, self).save(commit=False)
        model.date = self.cleaned_data['date']
        model.dest = self.cleaned_data['dest']
        model.source = self.cleaned_data['source']
        model.value = self.cleaned_data['value'] or 0
        if commit: model.save()
        return model
    def clean_dest(self):
        if not self.cleaned_data['dest'] and not self.fields['dest'].required: return None
        try: return Account.objects.filter(name=self.cleaned_data['dest'])[0]
        except: raise forms.ValidationError("The destination specified is not valid")
    def clean_source(self):
        if not self.cleaned_data['source'] and not self.fields['source'].required: return None
        try: return Account.objects.filter(name=self.cleaned_data['source'])[0]
        except: raise forms.ValidationError("The source specified is not valid")
        
class SaleAdmin(admin.ModelAdmin):
    form = SaleAdminForm
    list_display = ('doc_number', 'date','client', 'value','cost','item','quantity','serial')

class ClientPaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = ('doc_number', 'value', 'debit','credit')

class VendorPaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = ('doc_number', 'value', 'debit','credit')

class CountAdmin(admin.ModelAdmin):
    form = CountAdminForm
    list_display = ('doc_number', 'count', 'value','item','quantity','serial')

class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseAdminForm
    list_display = ('doc_number', 'vendor', 'value','item','quantity','serial')

class EntryInline(admin.TabularInline):
    model = Entry
    extra=0
class GaranteeOfferAdmin(admin.ModelAdmin):
    list_display = ('item', 'months', 'price')
#class GaranteeAdmin(admin.ModelAdmin):
#    list_display = ('transaction', 'months', 'price')
    
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'tipo','price_group','tax_group')
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'tipo')
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'doc_number', 'tipo')
    inlines = [EntryInline]
class AccountAdmin(admin.ModelAdmin):
    list_display = ('number','name', 'tipo','multiplier', 'balance', 'site')
    search_fields = ('name', )
    list_filter = ('tipo','multiplier')
class PriceAdmin(admin.ModelAdmin):
    list_display = ('item','group', 'fixed', 'relative','fixed_discount','relative_discount')  
    list_filter = ('group',)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name','unit', 'stock', 'description','minimum','maximum','cost')  
    search_fields = ('name', )
class EntryAdmin(admin.ModelAdmin):
    list_display = ('transaction','tipo', 'value', 'account','item','quantity')  
class CostLinkAdmin(admin.ModelAdmin):
    list_display = ('incoming', 'outgoing','quantity','value')
class ContactAdmin(admin.ModelAdmin):
    search_fields = ('account__name', )
class ReportAdmin(admin.ModelAdmin):
  class Media: 
    js = ('js/jquery.js',
          'js/codemirror/codemirror.js',
          'js/codemirror_config.js',)
admin.site.register(Client, ClientAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(GaranteeOffer, GaranteeOfferAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Count, CountAdmin)
admin.site.register(ClientPayment, ClientPaymentAdmin)
admin.site.register(VendorPayment, VendorPaymentAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TaxRate)
admin.site.register(Unit)
admin.site.register(AccountGroup)
admin.site.register(Contact, ContactAdmin)
admin.site.register(UserProfile)
admin.site.register(PriceGroup)
admin.site.register(Price, PriceAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(TransactionTipo)

