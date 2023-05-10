from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from .forms import Purchase_order_form
from .models import Purchase_order,unchecked_stock,checked_stock,Product_brand,Product_categories,product_qc_status
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
import core.utils as utils
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_purchase_order_view(request):
    
    if request.method == 'POST' and request.FILES['order_detail_file']:
        instance = request.POST
        po_added = Purchase_order.objects.create(purchase_details=instance['purchase_details'],order_detail_file=request.FILES['order_detail_file'],quantity=instance['quantity'],value=instance['value'])
        
        if po_added:
            myfile = request.FILES['order_detail_file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)              
            exceldata = pd.read_excel(filename)         
            dbframe = exceldata
            i=0
            product= {}
            for df in dbframe.iterrows():
                
                row = changeNaNtoNone(dbframe,i) 
                
                if not row['online_code']:
                    row['online_code'] = utils.create_product_code(row)

                if not utils.check_product(row['online_code']):
                    utils.add_product(row)
                
                utils.update_product_unchecked_stock(row['online_code'],row['quantity'])                

                obj = unchecked_stock.objects.create(purchase_id=po_added,box_id=row['box_id'], online_code=row['online_code'],
                                            quantity=row['quantity'], sosp=row['sosp'])           
                obj.save()
                i = i + 1
            return HttpResponse("/thanks/")
        else:
            form = Purchase_order_form()
    else:
        form = Purchase_order_form()

    tmpl = get_template("add_purchase_order.html")
    tmpl_string = tmpl.render({"form": form})

    return HttpResponse(tmpl_string)


def add_checked_stock_view(request):
    context = {}
    context['brands']= Product_brand.objects.all()
    context['categories']= Product_categories.objects.all()
    context['qc_status_list'] = product_qc_status.objects.all()
   
    if request.method == 'POST':
        instance = request.POST
        if not instance['product_id']:
            instance['product_id'] = utils.create_product_code(instance)

        if not utils.check_product(instance['product_id']):
            utils.add_product(instance)

        utils.update_product_checked_stock(instance['product_id'],instance['quantity'])

        obj = checked_stock.objects.create(product_id=instance['product_id'],quantity=instance['quantity'], sosp=instance['sosp'])           


        obj.save()


    #tmpl = get_template("add_checked_stock.html")
    #tmpl_string = tmpl.render({"form": form})

    #    return HttpResponse(tmpl_string)
    return render(request, "add_checked_stock.html", context)


def changeNaNtoNone(dbframe,row):
    returnrow = {}
    colm = list(dbframe)
            
    for x in colm:
        if dbframe[x][row] != dbframe[x][row]:
            returnrow[x] = None
        else:
            returnrow[x] = dbframe[x][row]
    
    return returnrow

def web_scrap_product_data(request, product_id):
    # query the db, or get the results from a global / readonly dict?
    link = 'https://www.amazon.in/dp/{}'.format(product_id)
    result = utils.getProductDetails(link)
    # return json for the js caller
    return JsonResponse(result, content_type="application/json")