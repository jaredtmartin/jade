from django import forms

class ProductAddToCartForm(forms.Form):
    quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'size':'2', 'value':'1', 'class':'quantity', 'maxlength':'5'}),
        error_messages={'invalid':'Please enter a valid quantity.'},
        min_value=1
    )
    product_slug = forms.CharField(widget=forms.HiddenInput())
    def __init__(self, request=None, *args, **kwargs):
        # override the default __init__ so we can set the request
        self.request = request
        super(ProductAddToCartForm, self).__init__(*args, **kwargs)

    def clean(self):
        # custom validation to check for cookies
        if self.request:
            if not self.request.session.test_cookie_worked():
            raise forms.ValidationError("Cookies must be enabled.")
        return self.cleaned_data

