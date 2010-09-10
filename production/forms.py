from jade.production.models import *
from jade.inventory.models import Item
from django import forms
from jade.inventory.forms import NewTransactionForm, clean_bar_code

class NewProcessForm(NewTransactionForm):
#    def clean(self):
#        super(NewProcessForm, self).clean()
#        if 'cost' in self.cleaned_data: 
#            if not self.cleaned_data['cost']: self.cleaned_data['cost']=1
#        return self.cleaned_data
    def save(self, commit=True):
        try: self.model
        except: self.model=Process()    
        if self.cleaned_data:
            self.model.cost=-1
            super(NewProcessForm, self).save(commit)
        return self.model
        
class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields=('doc_number','item','quantity','serial','cost')
    def save(self, commit=True):
        model = super(ProcessForm, self).save(commit=False)
        model.item =        self.cleaned_data['item']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.cost =        (self.cleaned_data['cost'] or 1)
        if commit: model.save()
        return model        
    doc_number =        forms.CharField()
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField()
    cost =              forms.DecimalField(required=False)
    serial =            forms.CharField(required=False)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x
        
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields=('doc_number', 'item', 'quantity', 'serial', 'cost')
    def save(self, commit=True):
        model = super(JobForm, self).save(commit=False)
        model.item =        self.cleaned_data['item']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.cost =        (self.cleaned_data['cost'] or 1)
        if commit: model.save()
        return model        
    doc_number =        forms.CharField()
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField()
    cost =              forms.DecimalField(required=False)
    serial =            forms.CharField(required=False)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x

