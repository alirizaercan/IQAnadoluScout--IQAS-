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

