import connexion
from connexion import NoContent
from flask import jsonify
import yaml
import logging
import logging.config
import json
import datetime
import uuid
from pykafka import KafkaClient 

import requests

MAX_EVENTS= 10
EVENT_FILE= "events.json"

# Your functions here

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def order_ride_immediately(body):
    trace_id=uuid.uuid4()                            
    logger.info(f'Recieved event \"Ride Order\" with a trace id of {trace_id}')
    headers = { "content-type":"application/json"}
    # response = requests.post(app_config["eventstore1"]["url"],
    #                             json=body, headers=headers)
    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer() 
    payload=body
    payload['trace_id']=f"{trace_id}"
    msg = { "type": "ride_order",  
            "datetime" :    
            datetime.datetime.now().strftime( 
                "%Y-%m-%dT%H:%M:%S"),  
            "payload": payload }  
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event \"Ride Order\" response (Id: {trace_id}) with status code 201")

    return NoContent,201

def schedule_ride(body):
    
    request_bio = f'User {body["user_id"]} is scheduling a ride to {body["destination"]} between {body["interval_start"]} and {body["interval_end"]} at {body["order_time"]}.'
    trace_id=uuid.uuid4()                            

    logger.info(f'Recieved event \"Schedule Order\" with a trace id of {trace_id}')
    headers = { "content-type":"application/json"}
    # response = requests.post(app_config["eventstore2"]["url"],
    #                             json=body, headers=headers)
    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer() 
    payload=body
    payload['trace_id']=f"{trace_id}"
    msg = { "type": "ride_schedule",  
            "datetime" :    
            datetime.datetime.now().strftime( 
                "%Y-%m-%dT%H:%M:%S"),  
            "payload": payload } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event \"Schedule Order\" response (Id: {trace_id}) with status code 201")
    return NoContent,201

app = connexion.FlaskApp(__name__,specification_dir='')
app.add_api("BCIT975-RideHail-1.0.0-swagger.yaml",strict_validation=True,validate_responses=True)


if __name__=="__main__":
 
    app.run(port=8080)
