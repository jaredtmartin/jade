# Jade Inventory Control System
#Copyright (C) 2010  Jared T. Martin

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied account of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
        fields=('doc_number','item','quantity','serial','value')
    def save(self, commit=True):
        model = super(ProcessForm, self).save(commit=False)
        model.item =        self.cleaned_data['item']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.value =        (self.cleaned_data['value'] or 1)
        if commit: model.save()
        return model        
    doc_number =        forms.CharField()
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField()
    value =              forms.CharField(required=False)
    serial =            forms.CharField(required=False)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x
    def clean_value(self):
        try:
            data=self.cleaned_data['value']
            if data=='undefined': return 0
            return Decimal(data)
        except:
            raise forms.ValidationError('Enter a number')
            return data
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields=('doc_number', 'item', 'quantity', 'serial', 'value')
    def save(self, commit=True):
        model = super(JobForm, self).save(commit=False)
        model.item =        self.cleaned_data['item']
        model.quantity =    self.cleaned_data['quantity']
        model.serial =      self.cleaned_data['serial']
        model.value =        (self.cleaned_data['value'] or 1)
        if commit: model.save()
        return model        
    doc_number =        forms.CharField()
    item =              forms.CharField(required=False)
    quantity =          forms.DecimalField()
    value =              forms.CharField(required=False)
    serial =            forms.CharField(required=False)
    def clean_item(self):
        x=clean_bar_code(self, 'item', Item)
        return x
    def clean_value(self):
        try:
            data=self.cleaned_data['value']
            if data=='undefined': return 0
            return Decimal(data)
        except:
            raise forms.ValidationError('Enter a number')
            return data

