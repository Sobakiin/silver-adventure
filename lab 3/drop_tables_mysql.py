import mysql.connector


db_conn = mysql.connector.connect(host="ec2-35-182-22-87.ca-central-1.compute.amazonaws.com",user="user",password="password",database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  DROP TABLE ride_order, schedule_order
                  ''')

db_conn.commit()
db_conn.close()