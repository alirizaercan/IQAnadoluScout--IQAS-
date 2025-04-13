# backend/services/match_service.py
from models.league import League
from models.football_team import FootballTeam
from models.match import Match
from models.footballer import Footballer
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from scipy.stats import poisson
import functools
import time

# Cache for predictions to avoid redundant calculations
prediction_cache = {}
# Cache expiration time in seconds (15 minutes)
CACHE_EXPIRATION = 15 * 60

class MatchService:
    def __init__(self, session: Session):
        self.session = session
        self.current_year = datetime.now().year
        self.lookback_matches = 10
        self.n_simulations = 50  # Reduced from 100 to 50 for better performance

    def get_all_leagues(self):
        leagues = self.session.query(League).all()
        return [{"league_id": league.league_id, "league_name": league.league_name, "league_logo_path": league.league_logo_path} for league in leagues]

    def get_teams_by_league(self, league_id):
        teams = self.session.query(FootballTeam).filter_by(league_id=league_id).all()
        return [{"team_id": team.team_id, "team_name": team.team_name, "img_path": team.img_path} for team in teams]

    def get_upcoming_matches(self, team_id):
        today = datetime.now().date()
        end_date = today + timedelta(days=30)  # Next 30 days
        
        # Get both home and away matches
        home_matches = self.session.query(Match).filter(
            Match.home_team_id == team_id,
            Match.date >= today,
            Match.date <= end_date,
            Match.is_played == False
        ).all()
        
        away_matches = self.session.query(Match).filter(
            Match.away_team_id == team_id,
            Match.date >= today,
            Match.date <= end_date,
            Match.is_played == False
        ).all()
        
        return home_matches + away_matches

    def analyze_team_performance(self, team_id, is_home=True):
        today = datetime.now().date()
        
        if is_home:
            matches = self.session.query(Match).filter(
                Match.home_team_id == team_id,
                Match.date < today,
                Match.is_played == True
            ).order_by(Match.date.desc()).limit(self.lookback_matches).all()
        else:
            matches = self.session.query(Match).filter(
                Match.away_team_id == team_id,
                Match.date < today,
                Match.is_played == True
            ).order_by(Match.date.desc()).limit(self.lookback_matches).all()
        
        if not matches:
            return None
        
        goals_scored = []
        goals_conceded = []
        
        for match in matches:
            if is_home:
                goals_scored.append(match.home_goals)
                goals_conceded.append(match.away_goals)
            else:
                goals_scored.append(match.away_goals)
                goals_conceded.append(match.home_goals)
        
        performance = {
            'recent_avg_scored': np.mean(goals_scored),
            'recent_avg_conceded': np.mean(goals_conceded),
            'recent_win_rate': sum(s > c for s, c in zip(goals_scored, goals_conceded)) / len(matches),
            'recent_clean_sheets': sum(c == 0 for c in goals_conceded) / len(matches),
            'recent_failed_to_score': sum(s == 0 for s in goals_scored) / len(matches),
        }
        
        return performance

    def predict_match_scores(self, team_id):
        # Check cache first
        team_id = int(team_id)  # Ensure team_id is an integer
        cache_key = f"prediction_{team_id}"
        current_time = time.time()
        
        if cache_key in prediction_cache:
            cached_data, timestamp = prediction_cache[cache_key]
            # If cache is still valid, return cached data
            if current_time - timestamp < CACHE_EXPIRATION:
                return cached_data
        
        # Get upcoming matches
        matches = self.get_upcoming_matches(team_id)
        
        if not matches:
            return []
        
        # Get only the necessary historical matches for training (limit to recent seasons)
        current_season = matches[0].season if matches else str(self.current_year)
        
        # Fix for season format handling
        try:
            # Try to handle standard format (e.g., "2023/2024")
            if '/' in current_season:
                year_part = current_season.split('/')[0]
                # Check if it's a short year format (e.g., "23/24")
                if len(year_part) == 2:
                    # Assume it's 21st century ("20" + "23")
                    year_part = "20" + year_part
                last_season_year = str(int(year_part) - 1)
                # If it's short format, keep it short
                if len(current_season.split('/')[0]) == 2:
                    last_season_year = last_season_year[-2:]
                last_season = last_season_year + current_season[len(year_part):]
            else:
                # Fallback to original logic if no slash
                last_season = str(int(current_season[:4]) - 1) + current_season[4:]
        except ValueError:
            # If parsing fails, use current year as fallback
            print(f"Warning: Could not parse season format: {current_season}. Using current year.")
            last_season = str(self.current_year - 1)
            current_season = str(self.current_year)
        
        all_matches = self.session.query(Match).filter(
            Match.is_played == True,
            Match.season.in_([current_season, last_season])
        ).limit(1000).all()  # Limit to 1000 matches for performance
        
        # Convert to DataFrame for the model
        df = pd.DataFrame([{
            'match_id': m.match_id,
            'date': m.date,
            'league_id': m.league_id,
            'season': m.season,
            'home_team_id': m.home_team_id,
            'away_team_id': m.away_team_id,
            'home_goals': m.home_goals,
            'away_goals': m.away_goals,
            'is_played': m.is_played
        } for m in all_matches])
        
        # Add performance features to training data more efficiently
        home_performances = {}
        away_performances = {}
        
        # Add performance features
        for index, row in df.iterrows():
            # Get or calculate home team performance
            if row['home_team_id'] not in home_performances:
                home_performances[row['home_team_id']] = self.analyze_team_performance(row['home_team_id'], is_home=True)
            home_perf = home_performances[row['home_team_id']]
            
            # Get or calculate away team performance
            if row['away_team_id'] not in away_performances:
                away_performances[row['away_team_id']] = self.analyze_team_performance(row['away_team_id'], is_home=False)
            away_perf = away_performances[row['away_team_id']]
            
            if home_perf:
                for k, v in home_perf.items():
                    df.at[index, f'home_{k}'] = v
            
            if away_perf:
                for k, v in away_perf.items():
                    df.at[index, f'away_{k}'] = v
        
        # Drop rows with missing performance data
        df = df.dropna(subset=[
            'home_recent_avg_scored', 'home_recent_avg_conceded',
            'away_recent_avg_scored', 'away_recent_avg_conceded'
        ])
        
        if len(df) == 0:
            return []
        
        # Train models
        feature_columns = [
            'league_id_encoded', 'season_encoded',
            'home_recent_avg_scored', 'home_recent_avg_conceded',
            'away_recent_avg_scored', 'away_recent_avg_conceded'
        ]
        
        # Encode categorical variables
        le_league = LabelEncoder()
        le_season = LabelEncoder()
        df['league_id_encoded'] = le_league.fit_transform(df['league_id'])
        df['season_encoded'] = le_season.fit_transform(df['season'])
        
        # Train home goals model with reduced complexity
        home_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=8)
        home_model.fit(df[feature_columns], df['home_goals'])
        
        # Train away goals model with reduced complexity
        away_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=8)
        away_model.fit(df[feature_columns], df['away_goals'])
        
        # Prepare upcoming matches for prediction
        pred_data = []
        for match in matches:
            is_home = match.home_team_id == team_id
            opponent_id = match.away_team_id if is_home else match.home_team_id
            
            # Get or calculate home team performance
            if match.home_team_id not in home_performances:
                home_performances[match.home_team_id] = self.analyze_team_performance(match.home_team_id, is_home=True)
            home_perf = home_performances[match.home_team_id]
            
            # Get or calculate away team performance
            if match.away_team_id not in away_performances:
                away_performances[match.away_team_id] = self.analyze_team_performance(match.away_team_id, is_home=False)
            away_perf = away_performances[match.away_team_id]
            
            features = {
                'match_id': match.match_id,
                'date': match.date,
                'league_id': match.league_id,
                'season': match.season,
                'home_team_id': match.home_team_id,
                'away_team_id': match.away_team_id,
            }
            
            if home_perf:
                for k, v in home_perf.items():
                    features[f'home_{k}'] = v
            
            if away_perf:
                for k, v in away_perf.items():
                    features[f'away_{k}'] = v
            
            pred_data.append(features)
        
        pred_df = pd.DataFrame(pred_data)
        
        # Ensure all required features exist
        for col in feature_columns:
            if col not in pred_df.columns:
                pred_df[col] = 0  # Default value if feature is missing
        
        # Encode categorical variables
        pred_df['league_id_encoded'] = le_league.transform(pred_df['league_id'])
        pred_df['season_encoded'] = le_season.transform(pred_df['season'])
        
        # Fill any remaining missing values
        pred_df = pred_df.fillna(0)
        
        # Make predictions
        pred_df['pred_home_goals'] = home_model.predict(pred_df[feature_columns])
        pred_df['pred_away_goals'] = away_model.predict(pred_df[feature_columns])
        
        # Apply Poisson adjustment
        predictions = self.apply_poisson_adjustment(pred_df)
        
        # Prepare final results
        results = []
        for _, row in predictions.iterrows():
            match = next(m for m in matches if m.match_id == row['match_id'])
            # Get team information
            home_team = self.session.query(FootballTeam).filter_by(team_id=match.home_team_id).first()
            away_team = self.session.query(FootballTeam).filter_by(team_id=match.away_team_id).first()
            
            # Get footballer information
            home_footballer = None
            away_footballer = None
            
            if match.home_footballer_id:
                home_footballer = self.session.query(Footballer).filter_by(footballer_id=match.home_footballer_id).first()
            
            if match.away_footballer_id:
                away_footballer = self.session.query(Footballer).filter_by(footballer_id=match.away_footballer_id).first()
            
            results.append({
                'match_id': match.match_id,
                'week': match.week,
                'date': match.date.strftime('%Y-%m-%d'),
                'home_team_id': match.home_team_id,
                'home_team_name': match.home_team,
                'home_team_logo': home_team.img_path if home_team else None,
                'away_team_id': match.away_team_id,
                'away_team_name': match.away_team,
                'away_team_logo': away_team.img_path if away_team else None,
                'predicted_home_goals': int(round(row['home_goals_pred'])),
                'predicted_away_goals': int(round(row['away_goals_pred'])),
                'confidence': (row['home_confidence'] + row['away_confidence']) / 2,
                'home_footballer_id': match.home_footballer_id,
                'away_footballer_id': match.away_footballer_id,
                'home_footballer_img_path': home_footballer.footballer_img_path if home_footballer else None,
                'away_footballer_img_path': away_footballer.footballer_img_path if away_footballer else None
            })
        
        # Cache the results
        prediction_cache[cache_key] = (results, current_time)
        
        return results

    def train_models(self, df):
        # Prepare training data
        feature_columns = ['league_id_encoded', 'season_encoded', 'home_recent_avg_scored', 
                          'home_recent_avg_conceded', 'away_recent_avg_scored', 'away_recent_avg_conceded']
        
        # Encode categorical variables
        le_league = LabelEncoder()
        le_season = LabelEncoder()
        
        df['league_id_encoded'] = le_league.fit_transform(df['league_id'])
        df['season_encoded'] = le_season.fit_transform(df['season'])
        
        # Train home goals model with reduced complexity
        home_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=8)
        home_model.fit(df[feature_columns], df['home_goals'])
        
        # Train away goals model with reduced complexity
        away_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=8)
        away_model.fit(df[feature_columns], df['away_goals'])
        
        return home_model, away_model, feature_columns, le_league, le_season

    def apply_poisson_adjustment(self, pred_df):
        # Ensure predicted goals are positive and properly shaped
        pred_df['pred_home_goals'] = np.maximum(0.1, pred_df['pred_home_goals'])  # Avoid zero or negative values
        pred_df['pred_away_goals'] = np.maximum(0.1, pred_df['pred_away_goals'])
        
        # Convert to numpy arrays with proper shape
        home_goals = pred_df['pred_home_goals'].values.astype(float)
        away_goals = pred_df['pred_away_goals'].values.astype(float)
        
        # Generate simulations with proper shape handling (reduced simulations for better performance)
        home_sims = np.random.poisson(
            lam=np.tile(home_goals, (self.n_simulations, 1)).T  # Shape: (n_matches, n_simulations)
        )
        away_sims = np.random.poisson(
            lam=np.tile(away_goals, (self.n_simulations, 1)).T
        )
        
        # Calculate adjusted predictions
        pred_df['home_goals_pred'] = np.round(np.mean(home_sims, axis=1))
        pred_df['away_goals_pred'] = np.round(np.mean(away_sims, axis=1))
        
        # Calculate confidence scores
        pred_df['home_confidence'] = np.mean(home_sims == pred_df['home_goals_pred'].values.reshape(-1, 1), axis=1)
        pred_df['away_confidence'] = np.mean(away_sims == pred_df['away_goals_pred'].values.reshape(-1, 1), axis=1)
        
        return pred_df