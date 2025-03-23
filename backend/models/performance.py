# backend/models/performance.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Performance(Base):
    __tablename__ = 'performance'

    player_id = Column(Integer, primary_key=True)
    footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=False)
    footballer_name = Column(String(100))
    total_played = Column(Float)
    started = Column(Float)
    minutes_per_game = Column(Float)
    total_minutes_played = Column(Float)
    team_of_the_week = Column(Float)
    goals_conceded_per_game = Column(Float)
    penalties_saved = Column(Float)
    saves_per_game = Column(Float)
    succ_runs_out_per_game = Column(Float)
    goals_conceded = Column(Float)
    conceded_from_inside_box = Column(Float)
    conceded_from_outside_box = Column(Float)
    saves_made = Column(Float)
    goals_prevented = Column(Float)
    saves_from_inside_box = Column(Float)
    saves_from_outside_box = Column(Float)
    saves_caught = Column(Float)
    saves_parried = Column(Float)
    goals = Column(Float)
    scoring_frequency = Column(String(50))
    goals_per_game = Column(Float)
    shots_per_game = Column(Float)
    shots_on_target_per_game = Column(Float)
    big_chances_missed = Column(Float)
    goal_conversion = Column(Float)
    penalty_goals = Column(Float)
    penalty_conversion = Column(Float)
    free_kick_goals = Column(Float)
    free_kick_conversion = Column(Float)
    goals_from_inside_the_box = Column(Float)
    goals_from_outside_the_box = Column(Float)
    headed_goals = Column(Float)
    left_foot_goals = Column(Float)
    right_foot_goals = Column(Float)
    penalty_won = Column(Float)
    assists = Column(Float)
    expected_assists_xa = Column(Float)
    touches_per_game = Column(Float)
    big_chances_created = Column(Float)
    key_passes_per_game = Column(Float)
    accurate_per_game = Column(Float)
    acc_own_half = Column(Float)
    acc_opposition_half = Column(Float)
    acc_long_balls = Column(Float)
    acc_chipped_passes = Column(Float)
    acc_crosses = Column(Float)
    clean_sheets = Column(Float)
    interceptions_per_game = Column(Float)
    tackles_per_game = Column(Float)
    possession_won_final_third = Column(Float)
    balls_recovered_per_game = Column(Float)
    dribbled_past_per_game = Column(Float)
    clearances_per_game = Column(Float)
    errors_leading_to_shot = Column(Float)
    errors_leading_to_goal = Column(Float)
    penalties_committed = Column(Float)
    succ_dribbles = Column(Float)
    total_duels_won = Column(Float)
    ground_duels_won = Column(Float)
    aerial_duels_won = Column(Float)
    possession_lost = Column(Float)
    fouls = Column(Float)
    was_fouled = Column(Float)
    offsides = Column(Float)
    goal_kicks_per_game = Column(Float)
    yellow = Column(Float)
    yellow_red = Column(Float)
    red_cards = Column(Float)
    average_sofascore_rating = Column(Float)

    # Relationship (if applicable)
    footballer = relationship('Footballer', back_populates='performances')

    def __init__(
        self, footballer_id, footballer_name=None, total_played=None, started=None,
        minutes_per_game=None, total_minutes_played=None, team_of_the_week=None,
        goals_conceded_per_game=None, penalties_saved=None, saves_per_game=None,
        succ_runs_out_per_game=None, goals_conceded=None, conceded_from_inside_box=None,
        conceded_from_outside_box=None, saves_made=None, goals_prevented=None,
        saves_from_inside_box=None, saves_from_outside_box=None, saves_caught=None,
        saves_parried=None, goals=None, scoring_frequency=None, goals_per_game=None,
        shots_per_game=None, shots_on_target_per_game=None, big_chances_missed=None,
        goal_conversion=None, penalty_goals=None, penalty_conversion=None,
        free_kick_goals=None, free_kick_conversion=None, goals_from_inside_the_box=None,
        goals_from_outside_the_box=None, headed_goals=None, left_foot_goals=None,
        right_foot_goals=None, penalty_won=None, assists=None, expected_assists_xa=None,
        touches_per_game=None, big_chances_created=None, key_passes_per_game=None,
        accurate_per_game=None, acc_own_half=None, acc_opposition_half=None,
        acc_long_balls=None, acc_chipped_passes=None, acc_crosses=None,
        clean_sheets=None, interceptions_per_game=None, tackles_per_game=None,
        possession_won_final_third=None, balls_recovered_per_game=None,
        dribbled_past_per_game=None, clearances_per_game=None, errors_leading_to_shot=None,
        errors_leading_to_goal=None, penalties_committed=None, succ_dribbles=None,
        total_duels_won=None, ground_duels_won=None, aerial_duels_won=None,
        possession_lost=None, fouls=None, was_fouled=None, offsides=None,
        goal_kicks_per_game=None, yellow=None, yellow_red=None, red_cards=None,
        average_sofascore_rating=None
    ):
        self.footballer_id = footballer_id
        self.footballer_name = footballer_name
        self.total_played = total_played
        self.started = started
        self.minutes_per_game = minutes_per_game
        self.total_minutes_played = total_minutes_played
        self.team_of_the_week = team_of_the_week
        self.goals_conceded_per_game = goals_conceded_per_game
        self.penalties_saved = penalties_saved
        self.saves_per_game = saves_per_game
        self.succ_runs_out_per_game = succ_runs_out_per_game
        self.goals_conceded = goals_conceded
        self.conceded_from_inside_box = conceded_from_inside_box
        self.conceded_from_outside_box = conceded_from_outside_box
        self.saves_made = saves_made
        self.goals_prevented = goals_prevented
        self.saves_from_inside_box = saves_from_inside_box
        self.saves_from_outside_box = saves_from_outside_box
        self.saves_caught = saves_caught
        self.saves_parried = saves_parried
        self.goals = goals
        self.scoring_frequency = scoring_frequency
        self.goals_per_game = goals_per_game
        self.shots_per_game = shots_per_game
        self.shots_on_target_per_game = shots_on_target_per_game
        self.big_chances_missed = big_chances_missed
        self.goal_conversion = goal_conversion
        self.penalty_goals = penalty_goals
        self.penalty_conversion = penalty_conversion
        self.free_kick_goals = free_kick_goals
        self.free_kick_conversion = free_kick_conversion
        self.goals_from_inside_the_box = goals_from_inside_the_box
        self.goals_from_outside_the_box = goals_from_outside_the_box
        self.headed_goals = headed_goals
        self.left_foot_goals = left_foot_goals
        self.right_foot_goals = right_foot_goals
        self.penalty_won = penalty_won
        self.assists = assists
        self.expected_assists_xa = expected_assists_xa
        self.touches_per_game = touches_per_game
        self.big_chances_created = big_chances_created
        self.key_passes_per_game = key_passes_per_game
        self.accurate_per_game = accurate_per_game
        self.acc_own_half = acc_own_half
        self.acc_opposition_half = acc_opposition_half
        self.acc_long_balls = acc_long_balls
        self.acc_chipped_passes = acc_chipped_passes
        self.acc_crosses = acc_crosses
        self.clean_sheets = clean_sheets
        self.interceptions_per_game = interceptions_per_game
        self.tackles_per_game = tackles_per_game
        self.possession_won_final_third = possession_won_final_third
        self.balls_recovered_per_game = balls_recovered_per_game
        self.dribbled_past_per_game = dribbled_past_per_game
        self.clearances_per_game = clearances_per_game
        self.errors_leading_to_shot = errors_leading_to_shot
        self.errors_leading_to_goal = errors_leading_to_goal
        self.penalties_committed = penalties_committed
        self.succ_dribbles = succ_dribbles
        self.total_duels_won = total_duels_won
        self.ground_duels_won = ground_duels_won
        self.aerial_duels_won = aerial_duels_won
        self.possession_lost = possession_lost
        self.fouls = fouls
        self.was_fouled = was_fouled
        self.offsides = offsides
        self.goal_kicks_per_game = goal_kicks_per_game
        self.yellow = yellow
        self.yellow_red = yellow_red
        self.red_cards = red_cards
        self.average_sofascore_rating = average_sofascore_rating