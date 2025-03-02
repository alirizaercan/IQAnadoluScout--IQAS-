# backend/models/player.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Player(Base):
    __tablename__ = 'players'
    
    player_id = Column(Integer, primary_key=True)
    footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=False)
    footballer_name = Column(String(100))
    rating = Column(Integer)
    potential = Column(Float)
    position_acronym = Column(String(25))
    goalkeeping = Column(Integer)
    mental = Column(Integer)
    physical = Column(Integer)
    technical = Column(Integer)
    aerial_reach = Column(Integer)
    command_of_area = Column(Integer)
    communication = Column(Integer)
    eccentricity = Column(Integer)
    first_touch = Column(Integer)
    handling = Column(Integer)
    kicking = Column(Integer)
    one_on_ones = Column(Integer)
    passing = Column(Integer)
    punching_tendency = Column(Integer)
    reflexes = Column(Integer)
    rushing_out_tendency = Column(Integer)
    throwing = Column(Integer)
    aggression = Column(Integer)
    anticipation = Column(Integer)
    bravery = Column(Integer)
    composure = Column(Integer)
    concentration = Column(Integer)
    decisions = Column(Integer)
    determination = Column(Integer)
    flair = Column(Integer)
    leadership = Column(Integer)
    off_the_ball = Column(Integer)
    positioning = Column(Integer)
    teamwork = Column(Integer)
    vision = Column(Integer)
    work_rate = Column(Integer)
    acceleration = Column(Integer)
    agility = Column(Integer)
    balance = Column(Integer)
    jumping_reach = Column(Integer)
    natural_fitness = Column(Integer)
    pace = Column(Integer)
    stamina = Column(Integer)
    strength = Column(Integer)
    free_kick_taking = Column(Integer)
    penalty_taking = Column(Integer)
    technique = Column(Integer)
    corners = Column(Integer)
    crossing = Column(Integer)
    dribbling = Column(Integer)
    finishing = Column(Integer)
    heading = Column(Integer)
    long_shots = Column(Integer)
    long_throws = Column(Integer)
    marking = Column(Integer)
    tackling = Column(Integer)
    
    # İlişkiler
    footballer = relationship('Footballer', back_populates='players')
    
    def __init__(self, footballer_id, footballer_name=None, rating=None, potential=None,
                 position_acronym=None, goalkeeping=None, mental=None, physical=None, technical=None,
                 aerial_reach=None, command_of_area=None, communication=None, eccentricity=None,
                 first_touch=None, handling=None, kicking=None, one_on_ones=None, passing=None,
                 punching_tendency=None, reflexes=None, rushing_out_tendency=None, throwing=None,
                 aggression=None, anticipation=None, bravery=None, composure=None, concentration=None,
                 decisions=None, determination=None, flair=None, leadership=None, off_the_ball=None,
                 positioning=None, teamwork=None, vision=None, work_rate=None, acceleration=None,
                 agility=None, balance=None, jumping_reach=None, natural_fitness=None, pace=None,
                 stamina=None, strength=None, free_kick_taking=None, penalty_taking=None,
                 technique=None, corners=None, crossing=None, dribbling=None, finishing=None,
                 heading=None, long_shots=None, long_throws=None, marking=None, tackling=None):
        
        self.footballer_id = footballer_id
        self.footballer_name = footballer_name
        self.rating = rating
        self.potential = potential
        self.position_acronym = position_acronym
        self.goalkeeping = goalkeeping
        self.mental = mental
        self.physical = physical
        self.technical = technical
        self.aerial_reach = aerial_reach
        self.command_of_area = command_of_area
        self.communication = communication
        self.eccentricity = eccentricity
        self.first_touch = first_touch
        self.handling = handling
        self.kicking = kicking
        self.one_on_ones = one_on_ones
        self.passing = passing
        self.punching_tendency = punching_tendency
        self.reflexes = reflexes
        self.rushing_out_tendency = rushing_out_tendency
        self.throwing = throwing
        self.aggression = aggression
        self.anticipation = anticipation
        self.bravery = bravery
        self.composure = composure
        self.concentration = concentration
        self.decisions = decisions
        self.determination = determination
        self.flair = flair
        self.leadership = leadership
        self.off_the_ball = off_the_ball
        self.positioning = positioning
        self.teamwork = teamwork
        self.vision = vision
        self.work_rate = work_rate
        self.acceleration = acceleration
        self.agility = agility
        self.balance = balance
        self.jumping_reach = jumping_reach
        self.natural_fitness = natural_fitness
        self.pace = pace
        self.stamina = stamina
        self.strength = strength
        self.free_kick_taking = free_kick_taking
        self.penalty_taking = penalty_taking
        self.technique = technique
        self.corners = corners
        self.crossing = crossing
        self.dribbling = dribbling
        self.finishing = finishing
        self.heading = heading
        self.long_shots = long_shots
        self.long_throws = long_throws
        self.marking = marking
        self.tackling = tackling