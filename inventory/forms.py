from django import forms
from .models import Stock,SuperMarket

class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):                                                        # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['super_market'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control', 'min': '0'})
        self.fields['barcode'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['cost_price'].widget.attrs.update({'class': 'textinput form-control','min': '0','step':'0.01'})
        self.fields['selling_price'].widget.attrs.update({'class': 'textinput form-control','min': '0','step':'0.01'})
        self.fields['sgst'].widget.attrs.update({'class': 'textinput form-control','min': '0','step':'0.01'})
        self.fields['cgst'].widget.attrs.update({'class': 'textinput form-control','min': '0','step':'0.01'})


    class Meta:
        model = Stock
        fields = ['name','super_market','quantity','cost_price','selling_price','sgst','cgst','barcode']