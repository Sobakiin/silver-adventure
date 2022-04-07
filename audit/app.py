from itertools import count
import connexion
import swagger_ui_bundle

import json
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_ride_order(index): 
    """ Get ordered ride in History """ 
    print("1")
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    print("2")

    topic = client.topics[str.encode(app_config["events"]["topic"])] 
    print("3")
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=10000) 
 
    logger.info("Retrieving order at index %d" % index) 
    print(consumer)
    try: 
        counter=0
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 

            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
            if msg["type"]=='ride_order':
                if counter==index:
                    return {"message":msg_str},200
                counter+=1

    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find BP at index %d" % index) 
    return { "message": "Not Found"}, 404

def get_ride_schedule(index): 
    """ Get scheduled ride in History """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 

    topic = client.topics[str.encode(app_config["events"]["topic"])] 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
    print(consumer)
    logger.info("Retrieving schedule at index %d" % index) 
    try: 
        counter=0
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
            if msg["type"]=='ride_schedule':
                if counter==index:
                    return {"message":msg_str},200
                counter+=1
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find BP at index %d" % index) 
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__,specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS']='Content-Type'
app.add_api("openapi.yml", strict_validation=True,validate_responses=True)

if __name__=="__main__":
    app.run(port=8110)
