import pymysql
import mysql.connector

db_conn = mysql.connector.connect(host="serviceapp-will.westus3.cloudapp.azure.com",user="user",password="password", database="events")

db_cursor= db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE ride_order
          (id INT NOT NULL AUTO_INCREMENT, 
           user_id VARCHAR(250) NOT NULL,
           order_time VARCHAR(250) NOT NULL,
           starting_point VARCHAR(250) NOT NULL,
           destination VARCHAR(250) NOT NULL,
           max_passenger INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           CONSTRAINT ride_order_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE schedule_order
          (id INT NOT NULL AUTO_INCREMENT, 
           user_id VARCHAR(250) NOT NULL,
           order_time VARCHAR(250) NOT NULL,
           interval_start VARCHAR(100) NOT NULL,
           interval_end VARCHAR(100) NOT NULL,
           destination VARCHAR(250) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           CONSTRAINT schedule_order_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
