from sqlalchemy import Column, Integer, String, DateTime 
from base import Base 
class Stats(Base): 
    """ Processing Statistics """ 
 
    __tablename__ = "stats" 
 
    id = Column(Integer, primary_key=True) 
    num_orders = Column(Integer, nullable=False) 
    most_requested_destination = Column(String, nullable=False) 
    mean_passengers = Column(Integer, nullable=False) 
    num_schedules = Column(Integer, nullable=False) 
    most_frequent_arrival = Column(DateTime, nullable=False) 
    last_updated = Column(DateTime, nullable=False) 
 
    def __init__(self, num_orders, most_requested_destination, mean_passengers, 
    num_schedules, most_frequent_arrival,last_updated): 
        """ Initializes a processing statistics objet """ 
        self.num_orders = num_orders 
        self.most_requested_destination = most_requested_destination 
        self.mean_passengers = mean_passengers 
        self.num_schedules = num_schedules 
        self.most_frequent_arrival = most_frequent_arrival 
        self.last_updated = last_updated 
 
    def to_dict(self): 
        """ Dictionary Representation of a statistics """ 
        dict = {} 
        dict['num_orders'] = self.num_orders
        dict['most_frequent_arrival'] = self.most_frequent_arrival 
        dict['most_requested_destination'] = self.most_requested_destination 
        dict['mean_passengers'] = self.mean_passengers 
        dict['num_schedules'] = self.num_schedules 
        dict['most_frequent_arrival'] = self.most_frequent_arrival 
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ") 
 
        return dict
