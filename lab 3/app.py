from unittest import result
import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from ride_order import RideOrder
from schedule_ride import RideSchedule
import datetime
import yaml
import logging
import logging.config
import json

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread


# MAX_EVENTS= 10
# EVENT_FILE= "events.json"

# Your functions here

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# DB_ENGINE = create_engine("sqlite:///readings.sqlite")
DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f'Connecting to DB. Hostname:{app_config["datastore"]["hostname"]}, Port:{app_config["datastore"]["port"]}')

'''
def order_ride_immediately(body):
    #print(body)
    # request_bio = f'User {body["user_id"]} requested a {body["max_passenger"]} ride from {body["starting_point"]} to {body["destination"]} at {body["order_time"]}.'
    # json_write(request_bio)

    session = DB_SESSION()

    ro = RideOrder(body['user_id'],
                    body['starting_point'],
                    body['destination'],
                    body['max_passenger'],
                    body['trace_id'])

    session.add(ro)

    session.commit()
    session.close()
    logger.debug(f'Stored event order_ride_immediately request with a trace id of {body["trace_id"]} ')
    return NoContent,201

def schedule_ride(body):
    #print(body)    
    # request_bio = f'User {body["user_id"]} is scheduling a ride to {body["destination"]} between {body["interval_start"]} and {body["interval_end"]} at {body["order_time"]}.'
    # json_write(request_bio)
    session = DB_SESSION()

    rs = RideSchedule(body['user_id'],
                    body['interval_start'],
                    body['interval_end'],
                    body['destination'],
                    body['trace_id'])

    session.add(rs)

    session.commit()
    session.close()
    logger.debug(f'Stored event schedule_ride request with a trace id of {body["trace_id"]} ')
    
    return NoContent,201
'''

def get_order_ride(timestamp):
    """Gets ride orders after the timestamp"""

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

    orders = session.query(RideOrder).filter(RideOrder.order_time >= timestamp_datetime)

    results_list = []

    for order in orders:
        results_list.append(order.to_dict())

    session.close()

    logger.info("Query for Rides Ordered after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def get_schedule_ride(timestamp):
    """Gets ride orders after the timestamp"""

    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

    orders = session.query(RideSchedule).filter(RideSchedule.order_time >= timestamp_datetime)

    results_list = []

    for order in orders:
        results_list.append(order.to_dict())

    session.close()

    logger.info("Query for scheduled rides made after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def process_messages(): 
    """ Process event messages """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],   
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
     
    # Create a consume on a consumer group, that only reads new messages  
    # (uncommitted messages) when the service re-starts (i.e., it doesn't  
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False, 
                                         auto_offset_reset=OffsetType.LATEST) 
 
    # This is blocking - it will wait for a new message 
    for msg in consumer: 
        msg_str = msg.value.decode('utf-8') 
        msg = json.loads(msg_str) 
        logger.info("Message: %s" % msg) 
 
        payload = msg["payload"] 
        print(payload)
        if msg["type"] == "ride_order": # Change this to your event type 
            # Store the event1 (i.e., the payload) to the DB
            session = DB_SESSION()
            body = msg["payload"]
            ro = RideOrder(body['user_id'],
                            body['starting_point'],
                            body['destination'],
                            body['max_passenger'],
                            body['trace_id'])
            session.add(ro)
            session.commit()
            session.close()
        elif msg["type"] == "ride_schedule": # Change this to your event type 
            # Store the event2 (i.e., the payload) to the DB 
            session = DB_SESSION()
            body = msg["payload"]
            rs = RideSchedule(body['user_id'],
                            body['interval_start'],
                            body['interval_end'],
                            body['destination'],
                            body['trace_id'])
            session.add(rs)
            session.commit()
            session.close()
        # Commit the new message as being read 
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__,specification_dir='')
app.add_api("BCIT975-RideHail-1.0.0-swagger.yaml",strict_validation=True,validate_responses=True)


if __name__=="__main__":
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True) 
    t1.start()
    app.run(port=8090)