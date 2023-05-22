# import form class from django
from django import forms
from .models import Purchase_order,unchecked_stock
  
# create a ModelForm
class Purchase_order_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Purchase_order
        fields = "__all__"

class po_stock_check_form(forms.Form):
    Purchase_order = forms.ModelChoiceField(queryset=Purchase_order.objects.all())
    Box_no = forms.CharField( max_length=100, required=False)
