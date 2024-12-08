# backend/models/physical.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey, TIMESTAMP
from utils.database import Base
from datetime import datetime

class Physical(Base):
    __tablename__ = 'physical'

    id = Column(Integer, primary_key=True)
    footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=False)
    muscle_mass = Column(Float, nullable=True)
    muscle_strength = Column(Float, nullable=True)
    muscle_endurance = Column(Float, nullable=True)
    flexibility = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    heights = Column(String(10), nullable=True)
    thigh_circumference = Column(Float, nullable=True)
    shoulder_circumference = Column(Float, nullable=True)
    arm_circumference = Column(Float, nullable=True)
    chest_circumference = Column(Float, nullable=True)
    back_circumference = Column(Float, nullable=True)
    waist_circumference = Column(Float, nullable=True)
    leg_circumference = Column(Float, nullable=True)
    calf_circumference = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    def __init__(self, footballer_id, muscle_mass=None, muscle_strength=None, muscle_endurance=None, flexibility=None, 
                 weight=None, body_fat_percentage=None, heights=None, thigh_circumference=None, 
                 shoulder_circumference=None, arm_circumference=None, chest_circumference=None, 
                 back_circumference=None, waist_circumference=None, leg_circumference=None, 
                 calf_circumference=None):
        self.footballer_id = footballer_id
        self.muscle_mass = muscle_mass
        self.muscle_strength = muscle_strength
        self.muscle_endurance = muscle_endurance
        self.flexibility = flexibility
        self.weight = weight
        self.body_fat_percentage = body_fat_percentage
        self.heights = heights
        self.thigh_circumference = thigh_circumference
        self.shoulder_circumference = shoulder_circumference
        self.arm_circumference = arm_circumference
        self.chest_circumference = chest_circumference
        self.back_circumference = back_circumference
        self.waist_circumference = waist_circumference
        self.leg_circumference = leg_circumference
        self.calf_circumference = calf_circumference
