import API.flipkartfinal as flipkart
from selenium import webdriver
import asyncio
import pdb

async def main(link):
    result = await flipkart.getProductDetails(link)
    print(result)
    try:
        print('Product Name : '+result["name"])
        print('Current Price : '+str(result["current_price"]))
        print('Original Price : '+str(result["original_price"]))
        print('Discount : '+result["discount"])
        print('Share URL : '+result["share_url"])
    except Exception as e:
        print(result)
        error = 'Some error occured while fetching product detail.Error for page {} is {}'.format(link, e)
        print(error)
    finally:
        print(br)
        check = input('Check out other product? (Y/N)')
        if check == 'y' or check == 'Y':
            inputData = askInput()
            await main(inputData[0], inputData[1])
        else:
            exit()


br = '___________________________________________________________'

print('=> flipkart-product-stock <=')
print('=> Flipkart Product Stock Details in a specific pincode <=')


def askInput():
    print(br)
    link = input("Input link of product : ")
    print(br)
    return [link]


inputData = askInput()
asyncio.run(main(inputData[0]))
