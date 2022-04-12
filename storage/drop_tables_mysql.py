import mysql.connector


db_conn = mysql.connector.connect(host="serviceapp-will.westus3.cloudapp.azure.com",user="user",password="password",database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  DROP TABLE ride_order, schedule_order
                  ''')

db_conn.commit()
db_conn.close()
