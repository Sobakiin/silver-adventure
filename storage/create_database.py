import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE ride_order
          (id INTEGER PRIMARY KEY ASC, 
           user_id VARCHAR(250) NOT NULL,
           order_time VARCHAR(250) NOT NULL,
           starting_point VARCHAR(250) NOT NULL,
           destination VARCHAR(250) NOT NULL,
           max_passenger INTEGER NOT NULL,
           trace_id VARCHAR(250) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE schedule_order
          (id INTEGER PRIMARY KEY ASC, 
           user_id VARCHAR(250) NOT NULL,
           order_time VARCHAR(250) NOT NULL,
           interval_start VARCHAR(100) NOT NULL,
           interval_end VARCHAR(100) NOT NULL,
           destination VARCHAR(250) NOT NULL,
           trace_id VARCHAR(250) NOT NULL)
          ''')

conn.commit()
conn.close()
