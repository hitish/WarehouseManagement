# import form class from django
from django import forms
  
# import GeeksModel from models.py
from .models import Purchase_order,checked_stock
  
# create a ModelForm
class Purchase_order_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Purchase_order
        fields = "__all__"

class add_checked_stock_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = checked_stock
        fields = "__all__"