from django.shortcuts import render
from django.db.models import Q,F
from .models import sale_bill,product_sold
from accounts.models import account,voucher,transaction,voucher_type
from product.models import checked_stock,product_stock
import core.utils as utils

# Create your views here.

def store_sale_view(request):
    context = {}
    context['checked_stock'] = checked_stock.objects.filter(quantity__gt = F("sold_quantity"))
    criterion1 = ~Q(group = 3)
    context['accounts'] = account.objects.filter( Q(is_active=True) & criterion1)
    criterion2 = Q(group = 3)
    context['pay_accounts'] = account.objects.filter( Q(is_active=True) & criterion2)
    context['success'] = False

    if request.method == 'POST':
        instance = request.POST
        product_count = int(instance["product_count"])
        prod_sold = []
        total_qty = 0
        total_bill = 0
        
        #print(instance)
        if not instance['account_id']:
            account_id = utils.create_account(instance['account_name'],instance['phone'],instance['address'])
        else:
            account_id = account.objects.get(id=instance['account_id'])

        for count in range(int(instance["product_count"])):
            item_num = str(count)
            product = instance["selected_product"+ item_num]
            qty = int(instance["qty"+ item_num])
            total_qty += qty
            priceperpiece = float(instance["priceperpiece"+ item_num])
            total_bill += qty * priceperpiece
            prod_sold.append([product,qty,priceperpiece])
        
     
        if product_count > 0:
            bill_id = sale_bill.objects.create(account_id=account_id,bill_amount=total_bill,product_qty=total_qty)

        if bill_id:
            for prod in prod_sold:
                #reduce stock at checked stock, product_Stock and product sold
                checked_Stock_ele = checked_stock.objects.get(id=prod[0])                
                product_sold.objects.create(sale_bill_id=bill_id,checked_stock_id=checked_Stock_ele,qty=prod[1],price_per_piece=prod[2])
                checked_Stock_ele.sold_quantity = checked_Stock_ele.sold_quantity + prod[1]
                checked_Stock_ele.save()
                product_stock_ele = product_stock.objects.get(product_id = checked_Stock_ele.product_id)
                product_stock_ele.checked_stock = product_stock_ele.checked_stock - prod[1]
                product_stock_ele.save()

            voucher__type = voucher_type.objects.get(id=2)
            desc = "Sales transaction for id " + str(bill_id.id) + " " + instance["reference-detail"]
            voucher_id = voucher.objects.create(voucher_type=voucher__type,voucher_object_id=bill_id,description=desc,amount=total_bill)

            if voucher_id:
                new_acc_bal = account_id.balance + total_bill
                account_id.balance = new_acc_bal
                account_id.save()
                transaction.objects.create(voucher=voucher_id,account_id=account_id,entry_type=False,amount=total_bill,account_balance=new_acc_bal)

                if not instance["payment-option"] == "-2":
                    paid_amount= float(instance["amount_paid"])
                    pay_voucher__type = voucher_type.objects.get(id=5)
                    pay_voucher_id = voucher.objects.create(voucher_type=pay_voucher__type,voucher_object_id=bill_id,description=desc,amount=paid_amount)

                    if pay_voucher_id:
                        new_acc_bal = account_id.balance - paid_amount
                        transaction.objects.create(voucher=pay_voucher_id,account_id=account_id,entry_type=False,amount=paid_amount,account_balance=new_acc_bal)
                        account_id.balance = new_acc_bal
                        account_id.save()

                        pay_acc_id = account.objects.get(id = instance["payment-option"])
                        pay_acc_bal = pay_acc_id.balance + paid_amount
                        transaction.objects.create(voucher=pay_voucher_id,account_id=pay_acc_id,entry_type=True,amount=paid_amount,account_balance=pay_acc_bal)
                        pay_acc_id.balance = pay_acc_bal
                        pay_acc_id.save()

                        context['success'] = True
                    

         
    return render(request, "store_sale.html", context=context)