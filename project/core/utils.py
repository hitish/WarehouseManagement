from product.models import Product_details,Product_brand,Product_categories,product_stock,unchecked_stock
import random,json,string,math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio
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
    if is_null(brand_name) or brand_name == "":
        try:
            brand_obj = Product_brand.objects.get(brand_name = brand_name)
        except:
            brand_obj = Product_brand.objects.create(brand_name = brand_name)
            return brand_obj
    else:
        brand_obj = None

    return brand_obj
    

def check_category(category_name):
    if is_null(category_name) or category_name == "":
        try:
            cat_obj = Product_categories.objects.get(category_name = category_name)
        except:
            cat_obj = Product_categories.objects.create(category_name = category_name)
            return cat_obj
    else:
        cat_obj = None
    return cat_obj
    
def is_null(element):
    if element != element:
        return True
    else:
        return False

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
    if not 'rating' in row.keys():
        rating = None
    else:
        rating = row['rating']

    if not 'metadata' in row.keys():
        metadata = None
    else:
        metadata = json.loads(row['metadata'])

    if not 'color' in row.keys():
        color = None
    else:
        color = row['color']

    if not 'size' in row.keys():
        size = None
    else:
        size = row['size']

    if not 'model' in row.keys():
        model = None
    else:
        model = row['model']
    
    if is_null(row['mrp']) or row['mrp'] == "":
        mrp = None
    else:
        mrp = row['mrp']
               
    
    response = Product_details.objects.create(product_id=row['online_code'],product_name=row['name'],brand_id=brand_obj,category_id=cat_obj,mrp=mrp,rating=rating,color=color,size=size,model=model,metadata=metadata)
    if response:
        product_stock.objects.create(product_id=response,checked_stock=0,unchecked_stock=0)

    return response

def update_product_unchecked_stock(product_id,quantity):
    try:
        product =  product_stock.objects.get(product_id=product_id)
        product.unchecked_stock = product.unchecked_stock + int(quantity)
        product.save()
    except Exception as e:
        error = 'Error adding stock {}'.format(e)
        print(error)

def update_product_checked_stock(product_id,quantity):
    try:
        product =  product_stock.objects.get(product_id=product_id)
        product.checked_stock = product.checked_stock + int(quantity)
        product.save()
    except Exception as e:
        error = 'Error adding stock {}'.format(e)
        print(error)

def update_product_stock_cheking(unchecked_id,quantity,checked=bool):
    try:
        unchecked = unchecked_stock.objects.get(id=unchecked_id)
        product = unchecked.online_code.product_stock
        quantity = int(quantity)
        
        if checked :
            diff = unchecked.quantity-unchecked.checked_quantity
            if diff>quantity:
              unchecked.checked_quantity = unchecked.checked_quantity + quantity
              product.checked_stock = product.checked_stock + quantity
              product.unchecked_stock = product.unchecked_stock - quantity
            else:
                error = "Quantity cannot be more than {}".format(diff)
                raise ValueError(error)
        else:
            unchecked.checked_quantity = unchecked.checked_quantity - quantity
            product.checked_stock = product.checked_stock - quantity
            product.unchecked_stock = product.unchecked_stock + quantity
      
        unchecked.save()
        product.save()
    except Exception as e:
        error = 'Error updating stock {}'.format(e)
        print(error)



async def getAmazonProductDetails(productLink):
    result = {}
    try:
        opts = Options()
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
        opts.page_load_strategy = 'eager'
        driver = webdriver.Chrome(chrome_options=opts) #Set the path to chromedriver

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
        category=''
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
            currentPrice = currentPrice.replace(",","").replace("\u20B9","")
        except Exception as e:
             error = 'Error for fetching current price for page is {}'.format(e)
             currentPrice = 0
             print(error)

        try:
            originalPrice = soup.find('div', attrs={'id':'corePriceDisplay_desktop_feature_div'}).find('span', attrs={'class':'a-price a-text-price'}).find('span', attrs={'class':'a-offscreen'}).text.strip()

            originalPrice = originalPrice.replace(",","").replace("\u20B9","")
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
            rating = rating[0:3]
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
            if 'Item model number' in metadata:
                model = metadata["Item model number"]
        except Exception as e:
             error = 'Error for fetching model for page is {}'.format(e)
             print(error)
        
        try:
            if 'Generic Name' in metadata:
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
            await page.close()
            await browser.close()
        except:
            None
        return result

async def getFlipkartProductDetails(productLink):
    result = {}
    try:
        print(productLink)
        driver = webdriver.Chrome() #Set the path to chromedriver
        driver.get(productLink)
        webPage = driver.page_source
        productName = ''
        currentPrice = ''
        discountPercentIndicator=''
        rating=''
        size=''
        brand=''
        color=''
        metadata={}
        soup = BeautifulSoup(webPage)
        try:
            productName=soup.find('span', attrs={'class':'B_NuCI'}).text.strip()
        except Exception as e:
             error = 'Error for fetching product name for page {}'.format(e)
             print(error)

        try:
            currentPrice = webPage.split('<h1')[1].split(">₹")[1].split("</div>")[0].replace(',', '')
        except Exception as e:
             error = 'Error for fetching original price for page is {}'.format(e)
             print(error)

        try:
            originalPrice = webPage.split('<h1')[1].split(">₹")[2].split("</div>")[0].split('<!-- -->')[0].replace(',', '')
        except Exception as e:
             error = 'Error for fetching original price for page is {}'.format(e)
             print(error)

        try:
            discount = originalPrice-currentPrice
            discountPercent = math.floor(discount/originalPrice * 100)
            discountPercentIndicator = str(discountPercent) + '% off'
        except Exception as e:
             error = 'Error for fetching discount for page is {}'.format(e)
             print(error)

        try:
            rating=soup.find('div', attrs={'class':'_3LWZlK'}).text.strip()
        except Exception as e:
             error = 'Error for fetching rating for page is {}'.format(e)
             print(error)

        try:
            size=soup.find('a', attrs={'class':'_1fGeJ5 PP89tw _2UVyXR _31hAvz'}).text.strip()
        except Exception as e:
             error = 'Error for fetching size for page is {}'.format(e)
             print(error)

        try:
            metaDataDiv = soup.find('div', attrs={'class':'X3BRps _13swYk'})
            allDivs = metaDataDiv.findAll(attrs={'class': 'row'})
            for div in allDivs:
                try:
                    name = div.find(attrs={'class': 'col col-3-12 _2H87wv'}).text.strip()
                    value = div.find(attrs={'class': 'col col-9-12 _2vZqPX'}).text.strip()
                    metadata[name]=value
                except:
                     continue
        except Exception as e:
             error = 'Error for fetching metadata for page is {}'.format(e)
             print(error)
        try:
            allmetaDataDivs = soup.findAll('div', attrs={'class':'_3k-BhJ'})
            for div in allmetaDataDivs:
                tableMetadata = div.find(attrs={'class': '_14cfVK'})
                tableRows = tableMetadata.findAll(attrs={'class': '_1s_Smc row'})
                for tableRow in tableRows:
                    try:
                        name = tableRow.find(attrs={'class': '_1hKmbr col col-3-12'}).text.strip()
                        value = tableRow.find(attrs={'class': '_21lJbe'}).text.strip()
                        metadata[name]=value
                    except:
                         continue
        except Exception as e:
             error = 'Error for fetching metadata for page is {}'.format(e)
             print(error)
       
        try:
            brand=soup.find('span', attrs={'class':'G6XhRU'}).text.strip()
            if not brand:
                brand = metadata["Brand"]
        except Exception as e:
             error = 'Error for fetching brand for page is {}'.format(e)
             print(error)
       
        try:
            selectedAnchor = soup.find('a', attrs={'class':'kmlXmn PP89tw'})
            color = selectedAnchor.parent()[4].text.strip()
            if not color:
                color = metadata["Color"]
        except Exception as e:
             error = 'Error for fetching color for page is {}'.format(e)
             print(error)
        
        try:
            model = metadata["Model Name"]
        except Exception as e:
             error = 'Error for fetching model for page is {}'.format(e)
             print(error)
       
        result = {'name': productName, 'current_price': currentPrice, 'original_price': originalPrice,
                  'discount': discountPercentIndicator, 'share_url': productLink, 'rating':rating,'model':model, 'size':size,
                  'color': color, 'brand':brand,'metadata':metadata}
    except Exception as e:
        error = 'Some error occured while fetching product detail.Error for page {} is {}'.format(productLink, e)
        result = {'error': error}
    finally:
        try:
            await page.close()
            await browser.close()
        except:
            None
        return result