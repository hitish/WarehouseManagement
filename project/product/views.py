from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.template.loader import get_template
from product.forms import Purchase_order_form,po_stock_check_form,sales_form,product_row_formset
from .models import Purchase_order,unchecked_stock,checked_stock,Product_brand,Product_categories,product_qc_status
from accounts.models import account
from django.db.models import Q
import pandas as pd
import math
from django.core.files.storage import FileSystemStorage
import core.utils as utils
from io import BytesIO
from barcode import EAN13,Code128,UPCA,Code39
from barcode.writer import SVGWriter

#from django.views.decorators.csrf import csrf_exempt


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
                    product_code = utils.create_product_code(row)
                else:
                    product_code = row['online_code']

                product = utils.check_product(product_code)
                if not product:
                    product = utils.add_product(row,product_code)
                
                utils.update_product_unchecked_stock(product_code,row['quantity'])                

                box_no = row['box_id']
                if box_no:
                    try:
                       float(box_no)
                       box_no = math.trunc(float(box_no)) 
                    except ValueError:
                        pass

                    box_no = str(box_no)

                obj = unchecked_stock.objects.create(purchase_id=po_added,box_id=box_no, online_code=product,
                                            quantity=row['quantity'], sosp=row['sosp'])           
                obj.save()
                i = i + 1
            form = Purchase_order_form()
        else:
            form = Purchase_order_form(instance)
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
    context["product_saved"] = 0
    if request.method == 'POST':
        instance = request.POST
        if not instance['online_code']:
            product_code = utils.create_product_code(instance)
        else:
            product_code = instance['online_code']

        product = utils.check_product(product_code)
        if not product:
            product = utils.add_product(instance,product_code)

        qc_status = product_qc_status.objects.get(id=instance['qc_status'])
        
        if utils.is_null(instance['cosp']) or instance['cosp'] == "":
            cosp = None
        else:
            cosp = instance['cosp']  

        

        obj = checked_stock.objects.create(product_id=product,quantity=instance['quantity'], cosp=cosp,mbp=instance['mbp'],qc_status=qc_status)    
        
        if obj:
            try:
                utils.update_product_checked_stock(product_code,instance['quantity'])
                    
                #  rv = BytesIO()
                upc_code = "MB" + qc_status.qc_code
                for i in range(6 - len(str(obj.id))):
                    upc_code = upc_code + "0"
                upc_code = upc_code + str(obj.id)
                # Code128(upc_code, writer=SVGWriter()).write(rv)
                filename = "static/barcode/" + upc_code + ".svg"
                with open(filename, "wb") as f:
                    writr = SVGWriter()
                    writr.set_options({"module_width":0.35, "module_height":10, "font_size": 18, "text_distance": 1, "quiet_zone": 3})
                    Code128(upc_code, writer=writr).write(f)
                obj.barcode = upc_code
                context["product_saved"] = obj
                # context["barcode_byte"] = rv.read()
                context["product_name"] = product.product_name
                context["mrp"] = int(float(product.mrp))
                context["message"] = "Product Saved Successfully"
                obj.save()
            except Exception as e:
                error = 'Error updating stock {}'.format(e)
                print(error)
                context["message"] = error
                context["product_saved"] = False
              
        
        
    else:
        context["message"] = "Product Not Saved"
        context["product_saved"] = False
        


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

async def web_scrap_product_data(request, product_id):

    length = len(product_id)
    if length == 10:
        link = 'https://www.amazon.in/dp/{}'.format(product_id)
        result = await utils.getAmazonProductDetails(link)
    elif length==16:
        link = 'https://www.flipkart.com/product/p/item?pid={}&marketplace=FLIPKART&sattr[]=color&sattr[]=size&st=size'.format(product_id)
        result =await utils.getFlipkartProductDetails(link)
    else:
        return "Code not Valid"
    # return json for the js caller
    return JsonResponse(result, content_type="application/json")


def po_stock_check_view(request):
    context = {}
    context['brands']= Product_brand.objects.all()
    context['categories']= Product_categories.objects.all()
    context['qc_status_list'] = product_qc_status.objects.all()
    context['products'] = {}
    form_purchase_order = po_stock_check_form()
   
    if request.method == 'GET':
        instance = request.GET
        if 'Purchase_order' in instance.keys():
            products = {}
            po_id = int(instance['Purchase_order'])
            selected_purchase_order = Purchase_order.objects.get(id=instance['Purchase_order'])
            try: 
                if 'Box_no' in instance.keys():
                    if not instance['Box_no'] == "":
                        box_no = instance['Box_no']
                        products = unchecked_stock.objects.filter(purchase_id_id=po_id,box_id="13")
                    else:
                        products = unchecked_stock.objects.filter(purchase_id_id =po_id)
                else:
                    products = unchecked_stock.objects.filter(purchase_id_id =34)
            except Exception as e:
                print(e)

            context['products'] = products
            form_purchase_order = po_stock_check_form(instance)
            
    if request.method == 'POST':
        instance = request.POST
        form_purchase_order = po_stock_check_form()
        
        product = utils.check_product(instance['online_code'])
        qc_status = product_qc_status.objects.get(id=instance['qc_status'])
        
        if utils.is_null(instance['cosp']) or instance['cosp'] == "":
            cosp = None
        else:
            cosp = instance['cosp']

        obj = checked_stock.objects.create(product_id=product,quantity=instance['quantity'], cosp=cosp,mbp=instance['mbp'],qc_status=qc_status)


        if obj:
            try:
                utils.update_product_stock_cheking(instance['unchecked_id'],instance['quantity'],True)
                
                 # length = 12- len(str(obj.id))
              #  rv = BytesIO()
                upc_code = "MB" + qc_status.qc_code
                for i in range(6 - len(str(obj.id))):
                    upc_code = upc_code + "0"
                upc_code = upc_code + str(obj.id)
               # Code128(upc_code, writer=SVGWriter()).write(rv)
                filename = "static/barcode/" + upc_code + ".svg"
                with open(filename, "wb") as f:
                    writr = SVGWriter()
                    writr.set_options({"module_width":0.35, "module_height":10, "font_size": 18, "text_distance": 1, "quiet_zone": 3})
                    Code128(upc_code, writer=writr).write(f)
                obj.barcode = upc_code
                context["product_saved"] = obj
               # context["barcode_byte"] = rv.read()
                context["product_name"] = product.product_name
                context["mrp"] = int(float(product.mrp))
                context["message"] = "Product Saved Successfully"

            except Exception as e:
                error = 'Error updating stock {}'.format(e)
                print(error)
                context["message"] = error
                context["product_saved"] = False

        obj.save()


    context['form_purchase_order']  = form_purchase_order

    return render(request, "po_stock_check.html", context=context)


