from jade.inventory.models import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from jade.inventory.widgets import *
from django.forms.widgets import *
from django.forms.models import ModelForm, modelform_factory, inlineformset_factory
from django.forms.models import BaseModelFormSet, modelformset_factory, formset_factory
from django.forms.formsets import BaseFormSet
from datetime import datetime
import settings

def clean_lookup(form, name, model, by_pk=False, title=None):
    if not title: title=name
    data = form.cleaned_data[name]
    if (not data) and (not form.fields[name].required): return data
    try: 
        if by_pk:
            data = model.objects.filter(pk=int(data)).get()
        else:
            data = model.objects.filter(name=data).get()
    except model.MultipleObjectsReturned: 
            raise forms.ValidationError('There are more than one %ss with the name %s. Resolve this issue and try again.' % (title, data))
    except model.DoesNotExist: 
        raise forms.ValidationError('Unable to find %s in the list of %ss.' % (data, title))
    return data
    
def clean_bar_code(form, name, model):
    data = form.cleaned_data[name]
    if (not data) and (not form.fields[name].required): return None
    try: 
        data = model.objects.filter(bar_code=data).get()
    except model.DoesNotExist: 
        try: 
            data = model.objects.filter(name=data).get()
        except model.MultipleObjectsReturned: 
            raise forms.ValidationError('There are more than one %ss with the name %s. Try using a bar code.' % (name, data))
        except model.DoesNotExist: 
            raise forms.ValidationError("Unable to find '%s' in the list of items." % (data, ))
    except model.MultipleObjectsReturned:
        raise forms.ValidationError('There are more than one %ss with the bar code %s. Try using the name and later resolve the issue.' % (name, data))
    return data


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields=('doc_number','date','account','item','quantity','serial','unit_cost','unit_tax','unit_discount','unit_price')
    def save(self, commit=True):
        model = super(SaleForm, self).save(commit=False)
        model.client =      self.cleaned_data['account']
        model.date =        self.cleaned_data['date']
        model.quantity =    self.cleaned_data['quantity']
        model.item =        self.cleaned_data['item']
        model.serial =      self.cleaned_data['serial']
        model.tax =         (self.cleaned_data['unit_tax'] or 0)
        model.discount =    (self.cleaned_data['unit_discount'] or 0)
        model.price =       self.cleaned_data['unit_price'] 
#        if not self.cleaned_data['unit_price'] and model.item: 
#            print "resetting price"
#            model.price = model.item.price(model.client)
#        print "self.cleaned_data['unit_price'] = " + str(self.cleaned_data['unit_price'])
        
        if self.cleaned_data['unit_cost']:
            model.cost = self.cleaned_data['unit_cost']
        if model.item and not model.cost: model.cost = model.item.cost
        if self.cleaned_data['quantity']!=0: 
            model.tax=              model.tax            * self.cleaned_data['quantity']
            model.discount=         model.discount       * self.cleaned_data['quantity']
            model.price=            model.price          * self.cleaned_data['quantity']
            model.cost=             model.cost           * self.cleaned_data['quantity']
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    account =           forms.CharField(initial=settings.DEFAULT_CLIENT_NAME)
    item =              forms.CharField(required=False)
    unit_price =        forms.DecimalField()
    quantity =          forms.DecimalField()
    unit_tax =          forms.DecimalField()
    unit_discount =     forms.DecimalField()
    unit_cost =         forms.CharField(required=False)#forms.DecimalField()
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    serial =            forms.CharField(required=False)
    def clean_account(self):
        return clean_lookup(self, 'account', Client)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x
    def clean_unit_cost(self):
        try:
            data=self.cleaned_data['unit_cost']
            if data=='undefined': return None
            return Decimal(data)
        except:
            raise forms.ValidationError('Enter a number')
            return data
            
class AccountingForm(forms.ModelForm):
    class Meta:
        model = Accounting
        fields=('doc_number','date','account','account2','value')
    def save(self, commit=True):
        model = super(AccountingForm, self).save(commit=False)
        model.debit_account =      self.cleaned_data['account']
        model.credit_account =      self.cleaned_data['account2']
        model.date =        self.cleaned_data['date']
        model.value =    self.cleaned_data['value']
        if commit: model.save()
        return model
    doc_number =     forms.CharField()
    account =  forms.CharField(initial=settings.DEFAULT_ACCOUNTING_DEBIT_ACCOUNT_NAME)
    account2 = forms.CharField(initial=settings.DEFAULT_ACCOUNTING_CREDIT_ACCOUNT_NAME)
    value =          forms.DecimalField()
    date =           forms.DateField(initial=datetime.now())
    def clean_account(self):
        print "asdafahhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
        return clean_lookup(self, 'account', Account)
    def clean_account2(self):
        print "asdadadadadadddddddddddd"
        a=self.cleaned_data
        return clean_lookup(self, 'account2', Account, title='account')

class ClientGaranteeForm(forms.ModelForm):
    class Meta:
        model = ClientGarantee
        fields=('doc_number','date','account','item','quantity','serial','value')
    def save(self, commit=True):
        model = super(ClientGaranteeForm, self).save(commit=False)
        model.client =      self.cleaned_data['account']
        model.date =        self.cleaned_data['date']
        model.item =        self.cleaned_data['item']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.price =        (self.cleaned_data['value'] or 0)
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    account =           forms.CharField(initial=settings.DEFAULT_CLIENT_NAME)
    item =              forms.CharField(required=False)
    value =             forms.DecimalField(required=False)
    quantity =          forms.DecimalField()
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    serial =            forms.CharField(required=False)
    def clean_account(self):
        return clean_lookup(self, 'account', Client)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x
        

class VendorGaranteeForm(forms.ModelForm):
    class Meta:
        model = VendorGarantee
        fields=('doc_number','date','account','item','quantity','serial','value')
    def save(self, commit=True):
        model = super(VendorGaranteeForm, self).save(commit=False)
        model.vendor =      self.cleaned_data['account']
        model.item =        self.cleaned_data['item']
        model.date =        self.cleaned_data['date']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.price =       (self.cleaned_data['value'] or 0)
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    account =           forms.CharField(initial=settings.DEFAULT_VENDOR_NAME)
    item =              forms.CharField(required=False)
    value =             forms.DecimalField()
    quantity =          forms.DecimalField()
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    serial =            forms.CharField(required=False)
    def clean_account(self):
        return clean_lookup(self, 'account', Vendor)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x

class ClientPaymentForm(forms.ModelForm):
    class Meta:
        model = ClientPayment
        fields=('doc_number','date','account','value')
    def save(self, commit=True):
        model = super(ClientPaymentForm, self).save(commit=False)
        model.source =      self.cleaned_data['account']
        model.date =        self.cleaned_data['date']
        model.value =        (self.cleaned_data['value'] or 0)
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    value =             forms.DecimalField(required=False)
    account =           forms.CharField(initial=settings.DEFAULT_CLIENT_NAME)
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    def clean_account(self):
        return clean_lookup(self, 'account', Client)

class VendorPaymentForm(forms.ModelForm):
    class Meta:
        model = VendorPayment
        fields=('doc_number','date','account','value')
    def save(self, commit=True):
        model = super(VendorPaymentForm, self).save(commit=False)
        model.dest =      self.cleaned_data['account']
        model.date =        self.cleaned_data['date']
        model.value =        self.cleaned_data['value']
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    value =             forms.DecimalField(required=False)
    account =           forms.CharField(initial=settings.DEFAULT_VENDOR_NAME)
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    def clean_account(self):
        return clean_lookup(self, 'account', Vendor)

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields=('doc_number','date','account','item','quantity','serial','tax','cost')
    def save(self, commit=True):
        model = super(PurchaseForm, self).save(commit=False)
        model.vendor =      self.cleaned_data['account']
        model.item =        self.cleaned_data['item']
        model.date =        self.cleaned_data['date']
        model.tax =         self.cleaned_data['tax']
        print "self.cleaned_data['tax'] = " + str(self.cleaned_data['tax'])
        print "model.tax = " + str(model.tax)
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.cost =        (self.cleaned_data['cost'] or 0)
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    account =           forms.CharField(initial=settings.DEFAULT_VENDOR_NAME)
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField()
    cost =              forms.DecimalField()
    tax =               forms.DecimalField()
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    serial =            forms.CharField(required=False)
    def clean_account(self):
        return clean_lookup(self, 'account', Vendor)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields=('doc_number','date','account','item','quantity','serial','cost')
    def save(self, commit=True):
        model = super(TransferForm, self).save(commit=False)
        model.account =      self.cleaned_data['account']
        model.item =        self.cleaned_data['item']
        model.date =        self.cleaned_data['date']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.cost =        (self.cleaned_data['cost'] or 0)
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    account =           forms.CharField()
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField()
    cost =              forms.DecimalField()
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    serial =            forms.CharField(required=False)
    def clean_account(self):
        return clean_lookup(self, 'account', Site)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x

class CountForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields=('doc_number','date','item','quantity','serial','cost')
    def save(self, commit=True):
        model = super(CountForm, self).save(commit=False)
        model.item =        self.cleaned_data['item']
        model.count =    self.cleaned_data['quantity']
        model.date =        self.cleaned_data['date']
        model.serial =      self.cleaned_data['serial']
        model.unit_cost =        (self.cleaned_data['cost'] or 0)
        if commit: model.save()
        return model
    doc_number =        forms.CharField()
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField(required=False)
    cost =              forms.DecimalField()
    date =              forms.DateField(initial=datetime.now()) #, input_formats=['%Y-%m-%d', '%d/%m/%Y',]) # Uncomment this for spanish dates
    serial =            forms.CharField(required=False)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x

class SearchForm(forms.Form):
    q =                 forms.CharField(required=False)
    start =             forms.DateField(required=False)
    end =               forms.DateField(required=False)
    def __init__(self, *args, **kwargs):
        validate = kwargs.pop('validate','')
        super(SearchForm, self).__init__(*args, **kwargs)
        if validate: self.is_valid()

class BoxForm(forms.Form):
    box = forms.ModelChoiceField(queryset=Item.objects.all(), empty_label="---")


class ItemImageForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('image',)


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ('tipo',)
    unit=forms.CharField(widget=AutoCompleteInput(url="/inventory/unit_list/"), required=False)
    description=forms.CharField(widget=Textarea(),required=False)
    def save(self, commit=True, tipo=None):        
        model = super(ItemForm, self).save(commit=False)
        if tipo: model.tipo=tipo
        if commit: model.save()
        return model
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['unit'] = instance.unit
    def clean_bar_code(self):
        if (not self.cleaned_data['bar_code']) or self.cleaned_data['bar_code']=='':
            print "HERE"
            print "Item.objects.next_bar_code()=" + str(Item.objects.next_bar_code())
            self.cleaned_data['bar_code']=Item.objects.next_bar_code()
            print "self.cleaned_data['bar_code']=" + str(self.cleaned_data['bar_code'])
        return self.cleaned_data['bar_code']
    def clean_unit(self):
        if self.cleaned_data['unit']=='':
            self.cleaned_data['unit']=settings.DEFAULT_UNIT_NAME
        data = self.cleaned_data['unit']
        if (not data) and (not self.fields['unit'].required): return data
        try: data = Unit.objects.get_or_create(name=data)[0]
        except Unit.MultipleObjectsReturned: 
                raise forms.ValidationError('There are more than one %ss with the name %s. Resolve this issue and try again.' % (name, data))
        except Unit.DoesNotExist: 
            raise forms.ValidationError('Unable to find %s in the list of %ss.' % (data, 'unit'))
        return data
        

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields=('relative','fixed')
PriceFormSet = modelformset_factory(Price, form=PriceForm, extra=0)

class GaranteeOfferForm(forms.ModelForm):
    months=forms.IntegerField(initial=0)
    price=forms.DecimalField(initial=Decimal('0.00'))
    class Meta:
        model = GaranteeOffer
        fields=('item', 'months','price')
        
class LinkedItemForm(forms.ModelForm):
    class Meta:
        model = LinkedItem
        fields=('quantity',)
 
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude=('tax_group', 'price_group', 'tipo','site')
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        if not kwargs.has_key('instance'):
            self.initial['number'] = Account.objects.next_number()
    def save(self, commit=True, tipo=None):        
        model = super(AccountForm, self).save(commit=False)
        if tipo: model.tipo=tipo
        if commit: model.save()
        return model

class ContactForm(forms.ModelForm):
    class Meta:
        model = Account
        fields=('name', 'number', 'multiplier', 'tax_group', 'price_group', 'address','state_name','country', 
            'home_phone', 'cell_phone', 'work_phone', 'fax', 'tax_number', 'description', 'email', 'registration', 'user')
    address =       forms.CharField(required=False)
    state_name =    forms.CharField(required=False)
    country =       forms.CharField(required=False)
    home_phone =    forms.CharField(required=False)
    cell_phone =    forms.CharField(required=False)
    work_phone =    forms.CharField(required=False)
    fax =           forms.CharField(required=False)
    tax_number =    forms.CharField(required=False)
    tax_group =     forms.CharField(widget=AutoCompleteInput('/inventory/tax_group_list/'))
    price_group =   forms.CharField(widget=AutoCompleteInput('/inventory/price_group_list/'))
    description =   forms.CharField(required=False)
    email =         forms.CharField(required=False)
    credit_days =   forms.IntegerField(required=False)
    registration =  forms.CharField(required=False)
    user =          forms.CharField(widget=AutoCompleteInput('/inventory/user_list/'), required=False)
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.fields['address'].label = _('Address')
            self.fields['state_name'].label = _('State')
            self.fields['country'].label = _('Country')
            self.fields['home_phone'].label = _('Home Phone')
            self.fields['cell_phone'].label = _('Cell Phone')
            self.fields['work_phone'].label = _('Work Phone')
            self.fields['fax'].label = _('Fax')
            self.fields['tax_number'].label = _('Tax ID Number')
            self.fields['description'].label = _('Description')
            self.fields['email'].label = _('Email')
            self.fields['registration'].label = _('Registration')
            self.fields['user'].label = _('User')
            self.fields['credit_days'].label = _('Days of Credit')
            self.initial['address'] = instance.address
            self.initial['state_name'] = instance.state_name
            self.initial['country'] = instance.country
            self.initial['home_phone'] = instance.home_phone
            self.initial['cell_phone'] = instance.cell_phone
            self.initial['work_phone'] = instance.work_phone
            if instance.tax_group: self.initial['tax_group'] = instance.tax_group.name
            else: self.initial['tax_group'] = settings.DEFAULT_TAX_GROUP_NAME
            if instance.price_group: self.initial['price_group'] = instance.price_group.name
            else: self.initial['price_group'] = settings.DEFAULT_PRICE_GROUP_NAME
            self.initial['fax'] = instance.fax
            self.initial['tax_number'] = instance.tax_number
            self.initial['description'] = instance.description
            self.initial['email'] = instance.email
            self.initial['registration'] = instance.registration
            self.initial['user'] = instance.user
            self.initial['credit_days'] = instance.credit_days
        else:
            self.initial['price_group'] = settings.DEFAULT_PRICE_GROUP_NAME
            self.initial['tax_group'] = settings.DEFAULT_TAX_GROUP_NAME
            self.initial['credit_days'] = settings.DEFAULT_CREDIT_DAYS
    def clean_tax_group(self):
        return clean_lookup(self, 'tax_group', TaxGroup)
    def clean_price_group(self):
        return clean_lookup(self, 'price_group', PriceGroup)
    def clean_user(self):
        print "self.cleaned_data['user'] = " + str(self.cleaned_data['user'])
        data = self.cleaned_data['user']
        if (not data) and (not self.fields['user'].required): return None
        try: data = User.objects.filter(username=data).get()
        except User.MultipleObjectsReturned: 
                raise forms.ValidationError('There are more than one %ss with the name %s. Resolve this issue and try again.' % ('user', data))
        except User.DoesNotExist: 
            raise forms.ValidationError('Unable to find %s in the list of %ss.' % (data, 'user'))
        return data
    def save(self, commit=True, tipo=None):        
        model = super(ContactForm, self).save(commit=False)
        if tipo: model.tipo=tipo
        model.address =        self.cleaned_data['address']
        model.state_name =        self.cleaned_data['state_name']
        model.country =        self.cleaned_data['country']
        model.home_phone =        self.cleaned_data['home_phone']
        model.cell_phone =        self.cleaned_data['cell_phone']
        model.work_phone =        self.cleaned_data['work_phone']
        model.fax =        self.cleaned_data['fax']
        model.tax_number =        self.cleaned_data['tax_number']
        model.tax_group =        self.cleaned_data['tax_group']
        model.price_group =        self.cleaned_data['price_group']
        model.description =        self.cleaned_data['description']
        model.email =        self.cleaned_data['email']
        model.registration =        self.cleaned_data['registration']
        model.user =        self.cleaned_data['user']
        model.credit_days =        self.cleaned_data['credit_days']
        if commit: model.save()
        return model
class ClientForm(ContactForm):
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        if not kwargs.has_key('instance'):
            self.initial['number'] = Client.objects.next_number()
            self.initial['multiplier'] = 1
class VendorForm(ContactForm):
    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        if not kwargs.has_key('instance'):
            self.initial['number'] = Vendor.objects.next_number()
            self.initial['multiplier'] = -1
class NewTransactionForm(forms.Form):
    doc_number =            forms.CharField(required=False)
    account =               forms.CharField(required=False)
    item =                  forms.CharField(required=False)

    def save(self, commit=True):
        if not self.model:self.model=Transaction()
        if 'item' in self.cleaned_data: self.model.item=self.cleaned_data['item']
        if 'doc_number' in self.cleaned_data: self.model.doc_number=self.cleaned_data['doc_number']
#        if 'date' in self.cleaned_data: self.model.date=self.cleaned_data['date']
        if commit: self.model.save()
        return self.model
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x

class NewTransferForm(NewTransactionForm):
    source = forms.CharField(required=False)
    dest = forms.CharField(required=False)
    def clean_dest(self):
        data=self.cleaned_data['client']
        if (not data) and (not self.fields['dest'].required): return None
        try: data = Site.objects.filter(name=data).get()
        except Site.MultipleObjectsReturned: 
                raise forms.ValidationError('There are more than one %ss with the name %s. Resolve this issue and try again.' % ('site', data))
        except Site.DoesNotExist: 
            raise forms.ValidationError('Unable to find %s in the list of %ss.' % (data, 'site'))
        return data
    def clean_source(self):
        data=self.cleaned_data['source']
        if (not data) and (not self.fields['source'].required): return None
        try: data = Site.objects.filter(name=data).get()
        except Site.MultipleObjectsReturned: 
                raise forms.ValidationError('There are more than one %ss with the name %s. Resolve this issue and try again.' % ('site', data))
        except Site.DoesNotExist: 
            raise forms.ValidationError('Unable to find %s in the list of %ss.' % (data, 'site'))
        return data
        
    
