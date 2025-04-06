# backend/services/match_service.py
from models.league import League
from models.football_team import FootballTeam
from models.match import Match
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from scipy.stats import poisson

class MatchService:
    def __init__(self, session: Session):
        self.session = session
        self.current_year = datetime.now().year
        self.lookback_matches = 10
        self.n_simulations = 100

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
        # Get upcoming matches
        matches = self.get_upcoming_matches(team_id)
        
        if not matches:
            return []
        
        # Get all historical matches for training
        all_matches = self.session.query(Match).filter(Match.is_played == True).all()
        
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
        
        # Train models
        home_model, away_model, feature_columns, le_league, le_season = self.train_models(df)
        
        # Prepare upcoming matches for prediction
        pred_data = []
        for match in matches:
            is_home = match.home_team_id == team_id
            opponent_id = match.away_team_id if is_home else match.home_team_id
            
            home_perf = self.analyze_team_performance(team_id if is_home else opponent_id, is_home=True)
            away_perf = self.analyze_team_performance(opponent_id if is_home else team_id, is_home=False)
            
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
        
        # Encode categorical variables
        pred_df['league_id_encoded'] = le_league.transform(pred_df['league_id'])
        pred_df['season_encoded'] = le_season.transform(pred_df['season'])
        
        # Fill missing values
        pred_df = pred_df.fillna(pred_df.mean())
        
        # Make predictions
        pred_df['pred_home_goals'] = home_model.predict(pred_df[feature_columns])
        pred_df['pred_away_goals'] = away_model.predict(pred_df[feature_columns])
        
        # Apply Poisson adjustment
        predictions = self.apply_poisson_adjustment(pred_df)
        
        # Prepare final results
        results = []
        for _, row in predictions.iterrows():
            match = next(m for m in matches if m.match_id == row['match_id'])
            results.append({
                'match_id': match.match_id,
                'date': match.date.strftime('%Y-%m-%d'),
                'home_team_id': match.home_team_id,
                'home_team_name': match.home_team,
                'away_team_id': match.away_team_id,
                'away_team_name': match.away_team,
                'predicted_home_goals': int(round(row['home_goals_pred'])),
                'predicted_away_goals': int(round(row['away_goals_pred'])),
                'confidence': (row['home_confidence'] + row['away_confidence']) / 2
            })
        
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
        
        # Train home goals model
        home_model = RandomForestRegressor(n_estimators=100, random_state=42)
        home_model.fit(df[feature_columns], df['home_goals'])
        
        # Train away goals model
        away_model = RandomForestRegressor(n_estimators=100, random_state=42)
        away_model.fit(df[feature_columns], df['away_goals'])
        
        return home_model, away_model, feature_columns, le_league, le_season

    def apply_poisson_adjustment(self, pred_df):
        home_sims = np.random.poisson(pred_df['pred_home_goals'], size=(len(pred_df), self.n_simulations))
        away_sims = np.random.poisson(pred_df['pred_away_goals'], size=(len(pred_df), self.n_simulations))
        
        pred_df['home_goals_pred'] = np.round(np.mean(home_sims, axis=1))
        pred_df['away_goals_pred'] = np.round(np.mean(away_sims, axis=1))
        
        pred_df['home_confidence'] = np.mean(home_sims == pred_df['home_goals_pred'].values.reshape(-1, 1), axis=1)
        pred_df['away_confidence'] = np.mean(away_sims == pred_df['away_goals_pred'].values.reshape(-1, 1), axis=1)
        
        return pred_df
    