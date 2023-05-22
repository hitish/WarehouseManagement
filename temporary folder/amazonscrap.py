from selenium import webdriver
import asyncio
import math
from bs4 import BeautifulSoup
import numpy as np

async def getProductDetails(productLink):
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
            await page.close()
            await browser.close()
        except:
            None
        return result