from sqlite3 import Date
from sqlalchemy import Column, Integer, String, DateTime, null
from base import Base
import datetime


class RideOrder(Base):
    """ ride_order """

    __tablename__ = "ride_order"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    order_time = Column(DateTime, nullable=False)
    starting_point = Column(String(250), nullable=False)
    destination = Column(String(250), nullable=False)
    max_passenger = Column(Integer, nullable=False)
    trace_id = Column(String(250), nullable=False)
    def __init__(self, user_id, starting_point, destination, max_passenger, trace_id):
        """ Initializes an immediate ride order """
        self.user_id = user_id
        self.starting_point = starting_point
        self.order_time = datetime.datetime.now() # Sets the date/time record is created
        self.destination = destination
        self.max_passenger = max_passenger
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a ride order """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['order_time'] = self.order_time
        dict['starting_point'] = self.starting_point
        dict['destination'] = self.destination
        dict['max_passenger'] = self.max_passenger
        dict['trace_id'] = self.trace_id

        return dict
