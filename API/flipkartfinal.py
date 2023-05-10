from selenium import webdriver
import asyncio
import math
from bs4 import BeautifulSoup

async def getProductDetails(productLink):
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
            currentPrice = getPrice(webPage.split('<h1')[1].split(">₹")[1].split("</div>")[0].replace(',', ''))
        except Exception as e:
             error = 'Error for fetching original price for page is {}'.format(e)
             print(error)

        try:
            originalPrice = getPrice(webPage.split('<h1')[1].split(">₹")[2].split("</div>")[0].split('<!-- -->')[0])
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
            brand=soup.find('span', attrs={'class':'G6XhRU'}).text.strip()
        except Exception as e:
             error = 'Error for fetching brand for page is {}'.format(e)
             print(error)

        try:
            size=soup.find('a', attrs={'class':'_1fGeJ5 PP89tw _2UVyXR _31hAvz'}).text.strip()
        except Exception as e:
             error = 'Error for fetching size for page is {}'.format(e)
             print(error)

        try:
            selectedAnchor = soup.find('a', attrs={'class':'kmlXmn PP89tw'})
            color = selectedAnchor.parent()[4].text.strip()
        except Exception as e:
             error = 'Error for fetching color for page is {}'.format(e)
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
        result = {'name': productName, 'current_price': currentPrice, 'original_price': originalPrice,
                  'discount': discountPercentIndicator, 'share_url': productLink, 'rating':rating, 'size':size,
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

def getPrice(price):
    price = price.replace(',', '')
    if len(price) > 1:
        try:
            priceField = price.replace(',', '')
            price = float(priceField)
        except Exception as e:
            price = ''
    return price
