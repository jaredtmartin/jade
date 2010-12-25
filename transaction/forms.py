from jade.transaction.models import *
from jade.common.widgets import AutoCompleteField
from django.utils.safestring import mark_safe
from django import forms
from jade.common.widgets import CalanderInput
from django.utils.html import conditional_escape
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.translation import ugettext as _


def modelformset_factory(*args, **kwargs):
    """
    Returns a FormSet class for the given Django model class.
    Change its as_table function to show the forms as rows
    """
    prefix=kwargs.pop('prefix',None)
    can_delete=kwargs.get('can_delete',False)
    def get_default_prefix(cls): return prefix
    def as_table(self):
        "Returns this formset rendered as HTML <tr>s -- excluding the <table></table>."
        form_list = u' '.join([form.as_row() for form in self.forms])
        header_form=self.form()
        if can_delete: header_form.fields[forms.formsets.DELETION_FIELD_NAME] = forms.fields.BooleanField(label=_(u'Delete'), required=False)
        header=header_form.as_header_row()
        return mark_safe(u'\n'.join([unicode(self.management_form),header, form_list]))
    def _construct_form(self, i, **kwargs):
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i), 'formset_id':i, 'group':self.prefix}
        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
        defaults.update(kwargs)
        form = self.form(**defaults)
        self.add_fields(form, i)
        return form
    FormSet = forms.models.modelformset_factory(*args, **kwargs)
    FormSet._construct_form=_construct_form
    FormSet.as_table=as_table
    FormSet.get_default_prefix=get_default_prefix
    return FormSet
class RowForm(forms.ModelForm):
    """ Adds four features to the ModelForms.
        1. Adds .as_row method that renders the form as a table row, appropriate for a formset
        2. Adds .default_prefix method as well as its hook in init so a default prefix can be specified in subclasses
        3. Adds formset_id and group attributes to be set by a formset
        4. Adds arguments to put html at the beginning and end of the html_output... This is important when working 
        with formsets
    """
    def get_default_prefix(self): return 'rowform'
    def __init__(self, *args, **kwargs):
        self.formset_id=kwargs.pop('formset_id',None)
        self.group=kwargs.pop('group',None)
        super(RowForm, self).__init__(*args, **kwargs)
        if not self.prefix: self.prefix=self.get_default_prefix()
    def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row, start='', end=''):
        "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [start], []

        for name, field in self.fields.items():
            html_class_attr = ''
            bf = forms.forms.BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                # Create a 'class="..."' atribute if the row should have any
                # CSS classes applied.
                css_classes = bf.css_classes()
                if css_classes:
                    html_class_attr = ' class="%s"' % css_classes

                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))

                if bf.label:
                    label = conditional_escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if self.label_suffix:
                        if label[-1] not in ':?.!':
                            label += self.label_suffix
                    label = bf.label_tag(label) or ''
                else:
                    label = ''

                if field.help_text:
                    help_text = help_text_html % force_unicode(field.help_text)
                else:
                    help_text = u''

                output.append(normal_row % {
                    'errors': force_unicode(bf_errors),
                    'label': force_unicode(label),
                    'field': unicode(bf),
                    'help_text': help_text,
                    'html_class_attr': html_class_attr
                })

        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))

        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                if not last_row.endswith(row_ender):
                    # This can happen in the as_p() case (and possibly others
                    # that users write): if there are only top errors, we may
                    # not be able to conscript the last row for our purposes,
                    # so insert a new, empty row.
                    last_row = (normal_row % {'errors': '', 'label': '',
                                              'field': '', 'help_text':'',
                                              'html_class_attr': html_class_attr})
                    output.append(last_row)
                output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        output.append(end)
        return mark_safe(u'\n'.join(output))
    def as_row(self):
        "Returns this form rendered as a row in a table."
        row_attr=''
        if self.group: row_attr+=' group="%s" ' % self.group
        if not self.formset_id==None: row_attr+=' formset_id="%s" ' % self.formset_id
        return self._html_output(
            normal_row = u'<td%(html_class_attr)s>%(errors)s%(field)s%(help_text)s</td>',
            error_row = u'<td colspan="2">%s</td>',
            row_ender = u'</td>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False,
            start=u'<tr%s>' % row_attr,
            end=u'</tr>',
            )
    def as_header_row(self):
        "Returns this form rendered as a row in a table."
        return self._html_output(
            normal_row = u'<th>%(label)s</th>',
            error_row = u'<td colspan="2">%s</td>',
            row_ender = u'</td>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False,
            start=u'<tr>',
            end=u'</tr>',
            )
class GroupForm(RowForm):
    def __init__(self, *args, **kwargs):
        self.group=kwargs.pop('group',None)
        super(RowForm, self).__init__(*args, **kwargs)
    def as_row(self):
        "Returns this form rendered as a row in a table with the specified group."
        group_spec=' group="%s" ' % self.prefix.split('-')[0]
        return self._html_output(
            normal_row = u'aa<td'+group_spec+u' %(html_class_attr)s>%(errors)s%(field)s%(help_text)s</td>',
            error_row = u'bb<td'+group_spec+u' colspan="2">%s</td>',
            row_ender = u'cc</td>',
            help_text_html = u'dd<br />%s',
            errors_on_separate_row = False)
        
    
class SaleForm(RowForm):
    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['account'] = instance.account.name
    def get_default_prefix(self): return 'saleform'
    class Meta:
        model = Sale
    date = forms.DateField(widget=CalanderInput())
    account=AutoCompleteField(model=Client, url="/accounting/ajax-client-list/", required=False, label='Client')
class TransactionForm(RowForm):
    class Meta:
        fields=('date', 'value', 'active','inventorytransaction')
        model = Transaction
TransactionFormSet = modelformset_factory(Transaction, form=TransactionForm, extra=1)

class SaleLineForm(RowForm):
    def __init__(self, *args, **kwargs):
        super(SaleLineForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            if instance.item: self.initial['item'] = instance.item.name
    item=AutoCompleteField(model=Item, url='/inventory/ajax-item-list/', required=False)
    date = forms.DateField(widget=CalanderInput())
    document = forms.ModelChoiceField(Document, widget=forms.HiddenInput())
    def get_default_prefix(self): return 'salelineform'
    class Meta:
        fields=('document','date', 'value', 'quantity', 'item', 'serial', 'active', 'delivered')
        model = SaleLine
SaleLineFormSet = modelformset_factory(SaleLine, form=SaleLineForm, extra=0, prefix='salelineform', can_order=False, can_delete=True)


class NewSaleLineForm(forms.Form):
    formset_id = forms.IntegerField()
    item=AutoCompleteField(model=Item, url='/inventory/ajax-item-list/', required=False)

