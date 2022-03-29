from unittest import result
from urllib import response
from wsgiref import headers
import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from ride_order import RideOrder
from schedule_ride import RideSchedule
from stats import Stats
import datetime
import yaml
import logging
import logging.config
import swagger_ui_bundle
import requests
import sqlalchemy
import statistics
# import apscheduler_bundle
from apscheduler.schedulers.background import BackgroundScheduler


# MAX_EVENTS= 10
# EVENT_FILE= "events.json"

# Your functions here

with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yaml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f'sqlite:///{app_config["datastore"]["filename"]}')
# DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


'''
# def order_ride_immediately(body):
#     #print(body)
#     # request_bio = f'User {body["user_id"]} requested a {body["max_passenger"]} ride from {body["starting_point"]} to {body["destination"]} at {body["order_time"]}.'
#     # json_write(request_bio)

#     session = DB_SESSION()

#     ro = RideOrder(body['user_id'],
#                     body['starting_point'],
#                     body['destination'],
#                     body['max_passenger'],
#                     body['trace_id'])

#     session.add(ro)

#     session.commit()
#     session.close()
#     logger.debug(f'Stored event order_ride_immediately request with a trace id of {body["trace_id"]} ')
#     return NoContent,201

# def schedule_ride(body):
#     #print(body)    
#     # request_bio = f'User {body["user_id"]} is scheduling a ride to {body["destination"]} between {body["interval_start"]} and {body["interval_end"]} at {body["order_time"]}.'
#     # json_write(request_bio)
#     session = DB_SESSION()

#     rs = RideSchedule(body['user_id'],
#                     body['interval_start'],
#                     body['interval_end'],
#                     body['destination'],
#                     body['trace_id'])

#     session.add(rs)

#     session.commit()
#     session.close()
#     logger.debug(f'Stored event schedule_ride request with a trace id of {body["trace_id"]} ')
    
#     return NoContent,201

# def get_order_ride(timestamp):
#     """Gets ride orders after the timestamp"""

#     session = DB_SESSION()

#     timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

#     orders = session.query(RideOrder).filter(RideOrder.order_time >= timestamp_datetime)

#     results_list = []

#     for order in orders:
#         results_list.append(order.to_dict())

#     session.close()

#     logger.info("Query for Rides Ordered after %s returns %d results" % (timestamp, len(results_list)))

#     return results_list, 200

# def get_schedule_ride(timestamp):
#     """Gets ride orders after the timestamp"""

#     session = DB_SESSION()

#     timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

#     orders = session.query(RideSchedule).filter(RideSchedule.order_time >= timestamp_datetime)

#     results_list = []

#     for order in orders:
#         results_list.append(order.to_dict())

#     session.close()

#     logger.info("Query for scheduled rides made after %s returns %d results" % (timestamp, len(results_list)))

#     return results_list, 200
'''

def populate_stats():
    logger.info(f'Start periodic processing')
    current_stats = get_status()[0]
    current_time  = datetime.datetime.now()

    #Timestamps to check only new entries
    response_ride= requests.get(f'{app_config["eventstore"]["url"]}/ride-order',params={'timestamp':current_stats["last_updated"]})
    response_schedule= requests.get(f'{app_config["eventstore"]["url"]}/schedule-order',params={'timestamp':current_stats["last_updated"]})
    
    #testing timestamps, to make sure it gets something when testing. 
    # response_ride= requests.get(f'{app_config["eventstore"]["url"]}/ride-order',params={'timestamp':"2016-08-29T09:12:33"})
    # response_schedule= requests.get(f'{app_config["eventstore"]["url"]}/schedule-order',params={'timestamp':"2016-08-29T09:12:33"})
    
    if(response_ride.status_code == 200 & response_schedule.status_code==200):
        logger.info(f'Recieved code 200')
    else:
        logger.error(f'Recieved codes {response_ride.status_code} and {response_schedule.status_code}')

    for i in response_ride.json() + response_schedule.json():
        logger.debug(f'Processed event trace id: {i["trace_id"]}')

    destinations=[]
    passengers=[]
    for i in response_ride.json():
        destinations.append(i["destination"])
        passengers.append(i["max_passenger"])
    arrival=[]
    for j in response_schedule.json():
        arrival.append(j["interval_end"])
    
    
    num_orders=current_stats["num_orders"] + len(response_ride.json())
    most_req_dest=statistics.mode(destinations)
    mean_passengers= statistics.mean(passengers)
    num_schedules=current_stats["num_schedules"]+len(response_schedule.json())
    
     
    most_frequent_arrival=datetime.datetime.strptime(statistics.mode(arrival),"%Y-%m-%dT%H:%M:%S")

    new_stats = Stats(num_orders,most_req_dest,mean_passengers,num_schedules,most_frequent_arrival,current_time)

    session = DB_SESSION()
    session.add(new_stats)
    session.commit()

    logger.debug(f'Logged staistics of last five seconds as Stats object: {new_stats.to_dict()}')
    session.close()

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()

def most_recent_stats():
    session = DB_SESSION()

    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()
    
    return results

def get_status():
    logger.info(f'Beginning request')
    
    latest_stats=most_recent_stats()
    if latest_stats == None:
        logger.error('No stats to pull, sending defaults')
        latest_stats= Stats(0,'123 Street Ave','2',0,datetime.datetime.now(),datetime.datetime.now())
    
    content = latest_stats.to_dict()
    logger.debug(f'Current statistics are: {content}')
    logger.info('Request completed')
    return content, 200


app = connexion.FlaskApp(__name__,specification_dir='')
app.add_api("RideStatsAPI.yaml",strict_validation=True,validate_responses=True)


if __name__=="__main__":
    init_scheduler()
    app.run(port=8100)