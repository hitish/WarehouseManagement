from django.shortcuts import render
from django.http import HttpResponse
from accounts.forms import create_account_transaction_form,create_account_display_form
from .models import voucher,transaction,account,voucher_type
# Create your views here.

def create_account(request):
    print(request)



def account_transaction_view(request):
    context = {}
    context['form']= create_account_transaction_form()
    print(request)
    if request.method == 'POST':
        instance = request.POST
        #print(instance)
        amount = float(instance["amount"])
        if not instance['narration']:
            desc = None
        else:
            desc = instance['narration']

        vouch_type = voucher_type.objects.get(id=instance["voucher"])
        voucher_id = voucher.objects.create(voucher_type=vouch_type,amount=amount,description=desc)

        acc = account.objects.get(id=instance["selected_account"])
        pay_acc = account.objects.get(id=instance["payment_account"])

        if instance["transaction_type"]:
            acc_bal = acc.balance - amount
            pay_acc_bal = pay_acc.balance + amount
            transaction.objects.create(voucher=voucher_id,account_id=acc,entry_type=True,amount=amount,account_balance = acc_bal)
            transaction.objects.create(voucher=voucher_id,account_id=pay_acc,entry_type=False,amount=amount,account_balance = pay_acc_bal)
            
        else:
            acc_bal = acc.balance + amount
            pay_acc_bal = pay_acc.balance - amount
            transaction.objects.create(voucher=voucher_id,account_id=acc,entry_type=False,amount=amount,account_balance = acc_bal)
            transaction.objects.create(voucher=voucher_id,account_id=pay_acc,entry_type=True,amount=amount,account_balance = pay_acc_bal)

        acc.balance = acc_bal
        acc.save()
        pay_acc.balance = pay_acc_bal
        pay_acc.save()

    return render(request, "account_transactions.html", context)

def account_display_view(request):
    context = {}
    context['form']= create_account_display_form()
    print(request)
    if request.method == 'POST':
        instance = request.POST
        acc = account.objects.get(id=instance["selected_account"])
        start_date = instance["start_date"]
        end_date = instance["end_date"]

        try:
            transactions = transaction.objects.filter(account_id = acc,timestamp__gte = start_date , timestamp__lte = end_date )
            print(transactions)
            for tran in transactions:
                print(tran.voucher.description)
        except Exception as e:
            print(e)
    
    return render(request, "account_display.html", context)