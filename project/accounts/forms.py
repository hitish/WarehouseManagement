from django import forms
from .models import account
  
# create a ModelForm
class create_account_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = account
        fields = "__all__"