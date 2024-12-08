from sqlalchemy import Column, Integer, Float, ForeignKey, TIMESTAMP
from utils.database import Base
from datetime import datetime

class Endurance(Base):
    __tablename__ = 'endurance'

    id = Column(Integer, primary_key=True)
    footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=False)
    running_distance = Column(Float, nullable=True)
    average_speed = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    peak_heart_rate = Column(Integer, nullable=True)
    training_intensity = Column(Float, nullable=True)
    session = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    def __init__(self, footballer_id, running_distance=None, average_speed=None, heart_rate=None, 
                 peak_heart_rate=None, training_intensity=None, session=None):
        self.footballer_id = footballer_id
        self.running_distance = running_distance
        self.average_speed = average_speed
        self.heart_rate = heart_rate
        self.peak_heart_rate = peak_heart_rate
        self.training_intensity = training_intensity
        self.session = session
