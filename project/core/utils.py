from product.models import Product_details,Product_brand,Product_categories,product_stock
import random
import string
from selenium import webdriver
import asyncio
import math
from bs4 import BeautifulSoup
import numpy as np

def check_product(online_code):
    #print(online_code)
    try:
        product = Product_details.objects.get(product_id = online_code)
    except:
        return False
     
    return product

def check_brand(brand_name):
    try:
         brand_obj = Product_brand.objects.get(brand_name = brand_name)
    except:
        brand_obj = Product_brand.objects.create(brand_name = brand_name)
        return brand_obj
    
    return brand_obj
    
    
def check_category(category_name):
    try:
        cat_obj = Product_categories.objects.get(category_name = category_name)
    except:
        cat_obj = Product_categories.objects.create(category_name = category_name)
        return cat_obj
    
    return cat_obj
    

def create_product_code(row):
    code = ""
    if not row['category']:
        code += ''.join((random.choice(string.ascii_lowercase) for x in range(3)))
    else:
        code += row['category'][0:3]

    if not row['brand']:
        code += ''.join((random.choice(string.ascii_lowercase) for x in range(3)))
    else:
        code += row['brand'][0:3]
        
    code += ''.join((random.choice(string.ascii_lowercase) for x in range(8)))
   
    if not check_product(code):
        return code
    else:
        return create_product_code(row)


def add_product(row):
    brand_obj = check_brand(row['brand'])
    cat_obj = check_category(row['category'])
    response = Product_details.objects.create(product_id=row['online_code'],product_name=row['name'],brand_id=brand_obj,category_id=cat_obj,mrp=row['mrp'])
    if response:
        product_stock.objects.create(product_id=response)

    return response

def update_product_unchecked_stock(product_code,quantity):
    try:
        product =  product_stock.objects.get(product_id=product_code)
        product.unchecked_stock = product.unchecked_stock + quantity
        product.save()
    except:
        product = None

def getProductDetails(productLink):
    result = {}
    try:
        print(productLink)
        driver = webdriver.Chrome() #Set the path to chromedriver
        driver.get(productLink)
        webPage = driver.page_source
        productName = ''
        currentPrice = ''
        #discountPercentIndicator=''
        rating=''
        size=''
        brand=''
        color=''
        model=''
        metadata={}
        additionaldata={}
        productdetail={}
        metadatajoined={}
        soup = BeautifulSoup(webPage)
        
        try:
            productName=soup.find('span', attrs={'id':'productTitle'}).text.strip()
        except Exception as e:
             error = 'Error for fetching product name for page {}'.format(e)
             print(error)

        try:
            currentPrice = soup.find('div', attrs={'id':'corePriceDisplay_desktop_feature_div'}).find('span', attrs={'class':'a-price-whole'}).text.strip()
         
        except Exception as e:
             error = 'Error for fetching current price for page is {}'.format(e)
             currentPrice = 0
             print(error)

        try:
            originalPrice = soup.find('div', attrs={'id':'corePriceDisplay_desktop_feature_div'}).find('span', attrs={'class':'a-price a-text-price'}).find('span', attrs={'class':'a-offscreen'}).text.strip()
        except Exception as e:
             error = 'Error for fetching original price for page is {}'.format(e)
             originalPrice = 0
             print(error)

        try:
            metatable = soup.find('table', attrs={'id':'productDetails_techSpec_section_1'})
            #print(metatable.find_all('tr'))
            for row in metatable.find_all('tr'):
                try:
                    name = row.find(attrs={'class': 'prodDetSectionEntry'}).text.strip()
                    value = row.find(attrs={'class': 'prodDetAttrValue'}).text.strip().replace('\u200e','')
                    metadata[name]=value
                except:
                    continue
        except Exception as e:
             error = 'Error for fetching metadata for page is {}'.format(e)
             print(error)
             
        try:
            additionaldatatable = soup.find('table', attrs={'id':'productDetails_detailBullets_sections1'})
            for row in additionaldatatable.find_all('tr'):
                try:
                    name = row.find(attrs={'class': 'prodDetSectionEntry'}).text.strip()
                    value = row.find(attrs={'class': 'prodDetAttrValue'}).text.strip().replace('\u200e','')
                    metadata[name]=value
                except:
                    continue
        except Exception as e:
             error = 'Error for fetching additionaldata for page is {}'.format(e)
             print(error)
             
        try:
            productdetailtable = soup.find('div', attrs={'id':'detailBullets_feature_div'})
            for row in productdetailtable.find_all('li'):
                try:
                    name = row.find('span',attrs={'class': 'a-text-bold'}).text.strip().replace('\n                                    \u200f\n                                        :\n                                    \u200e','')
                    value = row.find('span',attrs={'class': ''}).text.strip()
                    productdetail[name]=value
                except:
                    continue
        except Exception as e:
             error = 'Error for fetching productdetail for page is {}'.format(e)
             print(error)
       

        if not metadata:
            metadata = productdetail
       
        try:
            rating=soup.find('span', attrs={'id':'acrPopover'}).find('span', attrs={'class':'a-icon-alt'}).text.strip()
        except Exception as e:
             error = 'Error for fetching rating for page is {}'.format(e)
             print(error)

        try:
            #brand=soup.find('  atr', attrs={'class':'po-brand'}).find('span',attrs={'class':'po-break-word'}).text.strip()
            brand = metadata["Brand"]     
            if not brand:
                brand=soup.find('tr', attrs={'class':'po-brand'}).find('span',attrs={'class':'po-break-word'}).text.strip()
           
        except Exception as e:
             error = 'Error for fetching brand for page is {}'.format(e)
             print(error)
             
        try:
            color=soup.find('span', attrs={'id':'inline-twister-expanded-dimension-text-color_name'}).text.strip()
            if not color:
                color = metadata["colour"]
        except Exception as e:
             error = 'Error for fetching color for page is {}'.format(e)
             print(error)

        try:
            size = soup.find('span', attrs={'id':'inline-twister-expanded-dimension-text-size_name'}).text.strip()
            if not size:
                color = metadata["size"]
        except Exception as e:
             error = 'Error for fetching size for page is {}'.format(e)
             print(error)
             
        try:
            model = metadata["Item model number"]
        except Exception as e:
             error = 'Error for fetching model for page is {}'.format(e)
             print(error)
        
        try:
            category = metadata["Generic Name"].replace(';','')
        except Exception as e:
            error = 'Error for fetching additionaldata for page is {}'.format(e)
            print(error)
        
        result = {'name': productName, 'current_price': currentPrice, 'original_price': originalPrice, 'rating':rating,'brand':brand, 'size':size,
                  'color': color,'model':model,'category':category,'metadata':metadata}
    
    except Exception as e:
        error = 'Some error occured while fetching product detail.Error for page {} is {}'.format(productLink, e)
        result = {'error': error}
    finally:
        try:
            page.close()
            browser.close()
        except:
            None
        return result
