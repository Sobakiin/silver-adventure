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
from flask_cors import CORS, cross_origin
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


def populate_stats():
    logger.info(f'Start periodic processing')
    current_stats = get_status()[0]
    current_time  = datetime.datetime.now()
    
    #Timestamps to check only new entries
    response_ride= requests.get(f'{app_config["eventstore"]["url"]}/ride-order',params={'start_timestamp':current_stats["last_updated"], "end_timestamp":datetime.datetime.now()})
    response_schedule= requests.get(f'{app_config["eventstore"]["url"]}/schedule-order',params={'start_timestamp':current_stats["last_updated"], "end_timestamp":datetime.datetime.now()})
    if(response_ride.status_code == 200 & response_schedule.status_code==200):
        logger.info(f'Recieved code 200')
    else:
        logger.error(f'Recieved codes {response_ride.status_code} and {response_schedule.status_code}')
    print(response_ride.json())
    print(response_schedule.json())
    if(len(response_ride.json())!=0 or len(response_schedule.json())!=0):  
        #testing timestamps, to make sure it gets something when testing. 
        # response_ride= requests.get(f'{app_config["eventstore"]["url"]}/ride-order',params={'timestamp':"2016-08-29T09:12:33"})
        # response_schedule= requests.get(f'{app_config["eventstore"]["url"]}/schedule-order',params={'timestamp':"2016-08-29T09:12:33"})
        
        if(len(response_ride.json())!=0):
            destinations=[]
            passengers=[]
            for i in response_ride.json():
                print(i)
                logger.debug(f'Processed event trace id: {i["trace_id"]}')
                destinations.append(i["destination"])
                passengers.append(i["max_passenger"])
            
            num_orders=current_stats["num_orders"] + len(response_ride.json())
            most_req_dest=statistics.mode(destinations)
            mean_passengers= statistics.mean(passengers)
        else:
            num_orders=current_stats['num_orders']
            most_req_dest="N/A"
            mean_passengers="N/A"
        if(len(response_schedule.json())!=0):
            arrival=[]
            for j in response_schedule.json():
                logger.debug(f'Processed event trace id: {j["trace_id"]}')
                arrival.append(j["interval_end"])        
            
            num_schedules=current_stats["num_schedules"]+len(response_schedule.json())
            most_frequent_arrival=datetime.datetime.strptime(statistics.mode(arrival),"%Y-%m-%dT%H:%M:%S.%fZ")
            print(arrival)
        else:
            num_schedules=current_stats["num_schedules"]
            most_frequent_arrival="N/A"
        new_stats = Stats(num_orders,most_req_dest,mean_passengers,num_schedules,most_frequent_arrival,current_time)
      
        session = DB_SESSION()
        session.add(new_stats)
        session.commit()

        logger.debug(f'Logged staistics of last five seconds as Stats object: {new_stats.to_dict()}')
        session.close()
    else:
        logger.debug('Not enough new data since last logged.')
    

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
CORS(app.app)
app.app.config['CORS_HEADERS']='Content-Type'
app.add_api("RideStatsAPI.yaml",strict_validation=True,validate_responses=True)


if __name__=="__main__":
    init_scheduler()
    app.run(port=8100)
