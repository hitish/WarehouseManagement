import API.database_functions as dbf
import asyncio
import mysql.connector as mysql

async def checking(lot_id):
    lot_id = 5
    try:
       connection = await dbf.create_database_connection()
       cursor = connection.cursor()

    except Exception as e:
        error = 'not connected due to {}'.format(e)
        print(error)
        
    try:
        select_lot_products = "select * from sd_unchecked_stock where lot_id ={}".format(lot_id)
        cursor.execute(select_lot_products)
        selected_products = cursor.fetchall()
        print(selected_products)
    except Exception as e:
        print(e)
        
    

asyncio.run(checking(10))