from sqlalchemy import Column, Integer, Float, ForeignKey, TIMESTAMP
from utils.database import Base
from datetime import datetime

class Conditional(Base):
    __tablename__ = 'conditional'

    id = Column(Integer, primary_key=True)
    footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=False)
    vo2_max = Column(Float, nullable=True)
    lactate_levels = Column(Float, nullable=True)
    training_intensity = Column(Float, nullable=True)
    recovery_times = Column(Float, nullable=True)
    current_vo2_max = Column(Float, nullable=True)
    current_lactate_levels = Column(Float, nullable=True)
    current_muscle_strength = Column(Float, nullable=True)
    target_vo2_max = Column(Float, nullable=True)
    target_lactate_level = Column(Float, nullable=True)
    target_muscle_strength = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    def __init__(self, footballer_id, vo2_max=None, lactate_levels=None, training_intensity=None, recovery_times=None,
                 current_vo2_max=None, current_lactate_levels=None, current_muscle_strength=None, 
                 target_vo2_max=None, target_lactate_level=None, target_muscle_strength=None):
        self.footballer_id = footballer_id
        self.vo2_max = vo2_max
        self.lactate_levels = lactate_levels
        self.training_intensity = training_intensity
        self.recovery_times = recovery_times
        self.current_vo2_max = current_vo2_max
        self.current_lactate_levels = current_lactate_levels
        self.current_muscle_strength = current_muscle_strength
        self.target_vo2_max = target_vo2_max
        self.target_lactate_level = target_lactate_level
        self.target_muscle_strength = target_muscle_strength
