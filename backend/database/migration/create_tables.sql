-- backend/database/migration/create_tables.sql
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    old_password VARCHAR(255),
    wrong_login_attempt INT DEFAULT 0,
    login_attempt INT DEFAULT 0,
    is_now_login VARCHAR(20) DEFAULT 'no',
    role VARCHAR(25),
    club VARCHAR(100),
    team_id INT REFERENCES football_teams(team_id),
    access_key VARCHAR(64) UNIQUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    needs_password_change BOOLEAN DEFAULT FALSE
);

-- NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    message VARCHAR(500) NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LEAGUES TABLE
CREATE TABLE IF NOT EXISTS leagues (
    league_id VARCHAR(10) PRIMARY KEY,
    league_name VARCHAR(100) NOT NULL,
    league_logo_path VARCHAR(250),
    country VARCHAR(50),
    num_teams VARCHAR(25),
    players INT,
    foreign_players INT,
    avg_marketing_val VARCHAR(20),
    avg_age FLOAT,
    most_valuable_player VARCHAR(50),
    total_market_value VARCHAR(20)
);

-- FOOTBALL TEAMS TABLE
CREATE TABLE IF NOT EXISTS football_teams (
    team_id INT PRIMARY KEY,
    league_name VARCHAR(100) NOT NULL,
    league_id VARCHAR(10) NOT NULL REFERENCES leagues(league_id),
    team_name VARCHAR(100) NOT NULL,
    team_info_link VARCHAR(250),
    img_path VARCHAR(250),
    num_players INT,
    avg_age FLOAT,
    num_legionnaires INT,
    avg_marketing_val VARCHAR(20),
    total_squad_value VARCHAR(20)
);

-- FOOTBALLERS TABLE
CREATE TABLE IF NOT EXISTS footballers (
    footballer_id INT PRIMARY KEY,
    league_id VARCHAR(10) NOT NULL REFERENCES leagues(league_id),
    team_id INT NOT NULL REFERENCES football_teams(team_id),
    footballer_name VARCHAR(100) NOT NULL,
    club VARCHAR(100) NOT NULL,
    league_name VARCHAR(100),
    trikot_num VARCHAR(5),
    position VARCHAR(50),
    birthday DATE,
    age INT,
    nationality_img_path VARCHAR(250),
    height VARCHAR(10),
    feet VARCHAR(10),
    contract VARCHAR(50),
    market_value VARCHAR(20),
    footballer_img_path VARCHAR(250)
);

-- PHYSICAL TABLE
CREATE TABLE IF NOT EXISTS physical (
    id SERIAL PRIMARY KEY,
    footballer_id INT NOT NULL REFERENCES footballers(footballer_id),
    muscle_mass FLOAT,
    muscle_strength FLOAT,
    muscle_endurance FLOAT,
    flexibility FLOAT,
    weight FLOAT,
    body_fat_percentage FLOAT,
    heights VARCHAR(10),
    thigh_circumference FLOAT,
    shoulder_circumference FLOAT,
    arm_circumference FLOAT,
    chest_circumference FLOAT,
    back_circumference FLOAT,
    waist_circumference FLOAT,
    leg_circumference FLOAT,
    calf_circumference FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CONDITIONAL TABLE
CREATE TABLE IF NOT EXISTS conditional (
    id SERIAL PRIMARY KEY,
    footballer_id INT NOT NULL REFERENCES footballers(footballer_id),
    vo2_max FLOAT,
    lactate_levels FLOAT,
    training_intensity FLOAT,
    recovery_times FLOAT,
    current_VO2_max FLOAT,
    current_lactate_levels FLOAT,
    current_muscle_strength FLOAT,
    target_VO2_max FLOAT,
    target_lactate_level FLOAT,
    target_muscle_strength FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ENDURANCE TABLE
CREATE TABLE IF NOT EXISTS endurance (
    id SERIAL PRIMARY KEY,
    footballer_id INT NOT NULL REFERENCES footballers(footballer_id),
    running_distance FLOAT,
    average_speed FLOAT,
    heart_rate INT,
    peak_heart_rate INT,
    training_intensity FLOAT,
    session INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players Tablosu
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    footballer_id INT NOT NULL,
    footballer_name VARCHAR(100),
    rating INT,
    potential FLOAT,
    position_acronym VARCHAR(25),
    goalkeeping INT,
    mental INT,
    physical INT,
    technical INT,
    aerial_reach INT,
    command_of_area INT,
    communication INT,
    eccentricity INT,
    first_touch INT,
    handling INT,
    kicking INT,
    one_on_ones INT,
    passing INT,
    punching_tendency INT,
    reflexes INT,
    rushing_out_tendency INT,
    throwing INT,
    aggression INT,
    anticipation INT,
    bravery INT,
    composure INT,
    concentration INT,
    decisions INT,
    determination INT,
    flair INT,
    leadership INT,
    off_the_ball INT,
    positioning INT,
    teamwork INT,
    vision INT,
    work_rate INT,
    acceleration INT,
    agility INT,
    balance INT,
    jumping_reach INT,
    natural_fitness INT,
    pace INT,
    stamina INT,
    strength INT,
    free_kick_taking INT,
    penalty_taking INT,
    technique INT,
    corners INT,
    crossing INT,
    dribbling INT,
    finishing INT,
    heading INT,
    long_shots INT,
    long_throws INT,
    marking INT,
    tackling INT,
    CONSTRAINT fk_footballer FOREIGN KEY (footballer_id) REFERENCES footballers(footballer_id)
);

-- Players Sofascore Performance Table
CREATE TABLE IF NOT EXISTS performance (
    player_id SERIAL PRIMARY KEY,
    footballer_id INT NOT NULL,
    footballer_name VARCHAR(100),
    total_played FLOAT,
    started FLOAT,
    minutes_per_game FLOAT,
    total_minutes_played FLOAT,
    team_of_the_week FLOAT,
    goals_conceded_per_game FLOAT,
    penalties_saved FLOAT,
    saves_per_game FLOAT,
    succ_runs_out_per_game FLOAT,
    goals_conceded FLOAT,
    conceded_from_inside_box FLOAT,
    conceded_from_outside_box FLOAT,
    saves_made FLOAT,
    goals_prevented FLOAT,
    saves_from_inside_box FLOAT,
    saves_from_outside_box FLOAT,
    saves_caught FLOAT,
    saves_parried FLOAT,
    goals FLOAT,
    scoring_frequency FLOAT,
    goals_per_game FLOAT,
    shots_per_game FLOAT,
    shots_on_target_per_game FLOAT,
    big_chances_missed FLOAT,
    goal_conversion FLOAT,
    penalty_goals FLOAT,
    penalty_conversion FLOAT,
    free_kick_goals FLOAT,
    free_kick_conversion FLOAT,
    goals_from_inside_the_box FLOAT,
    goals_from_outside_the_box FLOAT,
    headed_goals FLOAT,
    left_foot_goals FLOAT,
    right_foot_goals FLOAT,
    penalty_won FLOAT,
    assists FLOAT,
    expected_assists_xa FLOAT,
    touches_per_game FLOAT,
    big_chances_created FLOAT,
    key_passes_per_game FLOAT,
    accurate_per_game FLOAT,
    acc_own_half FLOAT,
    acc_opposition_half FLOAT,
    acc_long_balls FLOAT,
    acc_chipped_passes FLOAT,
    acc_crosses FLOAT,
    clean_sheets FLOAT,
    interceptions_per_game FLOAT,
    tackles_per_game FLOAT,
    possession_won_final_third FLOAT,
    balls_recovered_per_game FLOAT,
    dribbled_past_per_game FLOAT,
    clearances_per_game FLOAT,
    errors_leading_to_shot FLOAT,
    errors_leading_to_goal FLOAT,
    penalties_committed FLOAT,
    succ_dribbles FLOAT,
    total_duels_won FLOAT,
    ground_duels_won FLOAT,
    aerial_duels_won FLOAT,
    possession_lost FLOAT,
    fouls FLOAT,
    was_fouled FLOAT,
    offsides FLOAT,
    goal_kicks_per_game FLOAT,
    yellow FLOAT,
    yellow_red FLOAT,
    red_cards FLOAT,
    average_sofascore_rating FLOAT,
    CONSTRAINT fk_footballer FOREIGN KEY (footballer_id) REFERENCES footballers(footballer_id)
);

-- Matches Scores Table
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    league_id VARCHAR(10) NOT NULL REFERENCES leagues(league_id),
    week VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    home_team_id INT NOT NULL REFERENCES football_teams(team_id),
    home_team VARCHAR(50) NOT NULL,
    home_goals INT,
    away_team_id INT NOT NULL REFERENCES football_teams(team_id),
    away_team VARCHAR(50) NOT NULL,
    away_goals INT,
    season VARCHAR(10) NOT NULL,
    home_footballer_id INT REFERENCES footballers(footballer_id),
    away_footballer_id INT REFERENCES footballers(footballer_id),
    is_played BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX idx_matches_league_id ON matches(league_id);
CREATE INDEX idx_matches_home_team_id ON matches(home_team_id);
CREATE INDEX idx_matches_away_team_id ON matches(away_team_id);
CREATE INDEX idx_matches_home_footballer_id ON matches(home_footballer_id);
CREATE INDEX idx_matches_away_footballer_id ON matches(away_footballer_id);

-- Match Analysis Table
-- Match Analysis Table
CREATE TABLE IF NOT EXISTS match_analysis (
    id SERIAL PRIMARY KEY,
    match_date DATE NOT NULL,
    home_team_id INTEGER REFERENCES football_teams(team_id),
    home_team_name VARCHAR(100) NOT NULL,
    away_team_id INTEGER REFERENCES football_teams(team_id),
    away_team_name VARCHAR(100) NOT NULL,
    video_path VARCHAR(255) NOT NULL,
    processed_video_path VARCHAR(255),
    
    -- Team possession statistics
    home_possession_percentage FLOAT,
    away_possession_percentage FLOAT,
    home_attack_phases INTEGER,
    away_attack_phases INTEGER,
    
    -- Formation analysis
    home_formation VARCHAR(20),
    away_formation VARCHAR(20),
    home_avg_player_positions JSONB,
    away_avg_player_positions JSONB,
    
    -- Ball control statistics
    home_ball_control_time FLOAT,
    away_ball_control_time FLOAT,
    
    -- Player speed/distance
    home_avg_speed FLOAT,
    away_avg_speed FLOAT,
    home_total_distance FLOAT,
    away_total_distance FLOAT,
    
    -- Team colors
    home_team_color VARCHAR(20),
    away_team_color VARCHAR(20),
    
    -- Tactical heatmaps
    home_heatmap JSONB,
    away_heatmap JSONB,
    
    -- Key moments analysis
    key_moments JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_match_analysis_home_team_id ON match_analysis(home_team_id);
CREATE INDEX IF NOT EXISTS idx_match_analysis_away_team_id ON match_analysis(away_team_id);
CREATE INDEX IF NOT EXISTS idx_match_analysis_match_date ON match_analysis(match_date);
