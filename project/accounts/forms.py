from django import forms
from .models import account,voucher_type
from django.db.models import Q
  
# create a ModelForm
class create_account_form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = account
        fields = "__all__"


class create_account_transaction_form(forms.Form):
  
   voucher = forms.ChoiceField(choices=[('','Select Voucher Type')]+[(voucher1.id,voucher1.name) for voucher1 in voucher_type.objects.all()])

   selected_account =  forms.ChoiceField(choices=[('','Select Account')]+[(account1.id,account1.name) for account1 in 
                                                                          account.objects.filter(~Q(group = 3 ))])
   transaction_type = forms.ChoiceField(choices=[(0,"Payment Recieved"),(1,"Payment Done")])
   payment_account =  forms.ChoiceField(choices=[('','Select method')]+[(method.id,method.name) for method in account.objects.filter(group = 3)])
   narration = forms.CharField(max_length=200)
   amount = forms.DecimalField(min_value=0.0)
  
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    


class create_account_display_form(forms.Form):

    selected_account =  forms.ChoiceField(choices=[('','Select Account')]+[(account1.id,account1.name) for account1 in 
                                                                          account.objects.filter()])
    
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'} ))
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'} ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)