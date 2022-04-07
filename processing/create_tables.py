import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE stats
          (id INTEGER PRIMARY KEY ASC, 
           num_orders INTEGER NOT NULL,
           most_requested_destination VARCHAR(250) NOT NULL,
           mean_passengers INTEGER NOT NULL,
           num_schedules INTEGER NOT NULL,
           most_frequent_arrival VARCHAR(250) NOT NULL,
           last_updated VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()