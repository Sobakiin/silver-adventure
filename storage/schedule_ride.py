from sqlite3 import Date
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class RideSchedule(Base):
    """ Ride schedule """

    __tablename__ = "schedule_order"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    order_time = Column(DateTime, nullable=False)
    interval_start = Column(String(250), nullable=False)
    interval_end = Column(String(250), nullable=False)
    destination = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)

    def __init__(self, user_id, interval_start, interval_end, destination, trace_id):
        """ Initializes a scheduled ride """
        self.user_id = user_id
        self.order_time = datetime.datetime.now() # Sets the date/time record is created
        self.interval_start = interval_start
        self.interval_end=interval_end
        self.destination = destination
        self.trace_id = trace_id
        

    def to_dict(self):
        """ Dictionary Representation of a scheduled ride """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['order_time'] = self.order_time
        dict['interval_start'] = self.interval_start
        dict['interval_end'] = self.interval_end
        dict['destination'] = self.destination
        dict['trace_id'] = self.trace_id

        return dict
