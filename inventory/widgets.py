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
from django import forms
from django.utils import simplejson
from django.utils.safestring import mark_safe

class AutoCompleteInput(forms.TextInput):
    class Media:
        js = ('js/jquery.js', 'js/jquery.autocomplete.js')
    def __init__(self, url, attrs=None):
        self.url=url
        super(AutoCompleteInput, self).__init__(attrs)
    def render(self, name, value,  attrs=None):
        output = super(AutoCompleteInput, self).render(name, value, attrs)
        return output + mark_safe(u'''<script type="text/javascript">
            jQuery("#id_%s").autocomplete('%s', {
                matchSubset:0,
                autoFill:1,
            });
            </script>''' % (name, self.url))
            
            
class AjaxUploader(forms.FileInput):
    class Media:
        js = ('js/jquery.js', 'js/ajaxfileupload.js')
    def __init__(self, url, attrs=None):
        self.url=url
        super(AjaxUploader, self).__init__(attrs)
    def render(self, name, value,  attrs=None):
        output = super(AutoCompleteInput, self).render(name, value, attrs)
        return output + mark_safe(u'''
            
            ''' % (self.url, name))
            
            
            

            
class CalanderInput(forms.TextInput):
    class Media:
        js = ('js/jquery.js', 'js/jquery-ui.js')

    def render(self, name, value,  attrs=None):
        output = super(CalanderInput, self).render(name, value, attrs)
        return output + mark_safe(u'''<script type="text/javascript">
	        jQuery("#id_%s").datepicker();
            </script>''' % (name))
#class LiveInput(forms.TextInput):
#    class Media:
#        js = ('js/jquery.js')
#    def render(self, name, value,  attrs=None):
#        attrs["onblur"] = mark_safe(u'''jQuery.ajax({type: 'POST', url: jQuery('#id_%s').parents('form').attr('action'),data:{pk:jQuery('#id_%s').parents('.sale'), key:'id_%s', value:jQuery('#id_%s').val()},success:function update(data){jQuery('.message').remove();jQuery('#messages').append(data);}});''' % (name, name, name, name))
#        return super(LiveInput, self).render(name, value, attrs)
#        
#class LiveAutoComplete(AutoCompleteInput):
#    def render(self, name, value,  attrs=None):
#        attrs["onblur"] = mark_safe(u'''jQuery.ajax({type: 'POST', url: jQuery('#id_%s').parents('form').attr('action'),data:{key:'id_%s', value:jQuery('#id_%s').val()},success:function update(data){jQuery('.message').remove();jQuery('#messages').append(data);}});''' % (name, name, name))
#        return super(LiveAutoComplete, self).render(name, value, attrs)
#        
#class LiveCalander(CalanderInput):
#    def render(self, name, value,  attrs=None):
#        attrs["onblur"] = mark_safe(u'''jQuery.ajax({type: 'POST', url: jQuery('#id_%s').parents('form').attr('action'),data:{key:'id_%s', value:jQuery('#id_%s').val()},success:function update(data){jQuery('.message').remove();jQuery('#messages').append(data);}});''' % (name, name, name))
#        return super(LiveCalander, self).render(name, value, attrs)
        
class FixedInput(forms.HiddenInput):
    def render(self, name, value,  attrs=None):
#        value=value.name
        output = super(FixedInput, self).render(name, value, attrs)
        return output + mark_safe(str(value))
