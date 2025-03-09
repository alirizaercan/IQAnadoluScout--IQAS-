from models.league import League
from models.football_team import FootballTeam
from models.footballer import Footballer
from models.player import Player
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from datetime import datetime

class PlayerService:
    def __init__(self, session: Session):
        self.session = session
        
        # Position feature mapping for player recommendations
        self.position_features = {
            'GK': ['reflexes', 'handling', 'kicking', 'one_on_ones', 'throwing'],
            'CB': ['marking', 'tackling', 'positioning', 'jumping_reach', 'strength'],
            'LB': ['crossing', 'tackling', 'acceleration', 'pace', 'stamina'],
            'RB': ['crossing', 'tackling', 'acceleration', 'pace', 'stamina'],
            'DM': ['passing', 'positioning', 'tackling', 'work_rate', 'aggression'],
            'CM': ['passing', 'vision', 'dribbling', 'work_rate', 'teamwork'],
            'AM': ['passing', 'dribbling', 'flair', 'long_shots', 'vision'],
            'LW': ['dribbling', 'acceleration', 'flair', 'pace', 'crossing'],
            'RW': ['dribbling', 'acceleration', 'flair', 'pace', 'crossing'],
            'CF': ['finishing', 'off_the_ball', 'composure', 'heading', 'long_shots'],
            'SS': ['passing', 'finishing', 'off_the_ball', 'dribbling', 'vision'],
            'ST': ['finishing', 'composure', 'off_the_ball', 'pace', 'strength']
        }
        
        # Position mapping for standardization
        self.position_mapping = {
            'Goalkeeper': 'GK',
            'Centre-Back': 'CB',
            'Left-Back': 'LB',
            'Right-Back': 'RB',
            'Defensive Midfield': 'DM',
            'Central Midfield': 'CM',
            'Left Winger': 'LW',
            'Right Winger': 'RW',
            'Second Striker': 'SS',
            'Centre-Forward': 'CF',
            'Attacking Midfield': 'AM',
            'Left Midfield': 'LM',
            'Right Midfield': 'RM',
            'Midfielder': 'MID',
            'Defender': 'DEF',
            'Striker': 'ST'
        }
        
        # Ideal position distribution for team balance
        self.ideal_position_distribution = {
            'GK': 2,
            'CB': 4,
            'LB': 2,
            'RB': 2,
            'DM': 2,
            'CM': 4,
            'AM': 2,
            'LW': 2,
            'RW': 2,
            'OFF': 3  # Combined offensive group: CF, SS, ST
        }

    def _convert_currency(self, value):
        """Convert currency string to numeric value"""
        if not value:
            return None
            
        try:
            # Remove currency symbol and spaces
            value = value.replace("€", "").strip()
            
            # Replace 'm' with 'e6' for millions and 'K' with 'e3' for thousands
            value = value.replace("m", "e6").replace("M", "e6").replace("K", "e3").replace("k", "e3")
            
            # Convert to float
            return float(eval(value))
        except:
            return None
    
    def _format_position(self, position):
        """Format position to standardized acronym"""
        if not position:
            return None
            
        # Handle multiple positions
        positions = [pos.strip() for pos in position.split(',')]
        formatted_positions = []
        
        for pos in positions:
            formatted_pos = self.position_mapping.get(pos, pos)
            formatted_positions.append(formatted_pos)
            
        return ','.join(formatted_positions)
        
    def get_all_leagues(self):
        """Get all leagues from the database"""
        leagues = self.session.query(League).all()
        return [{"league_id": league.league_id, "league_name": league.league_name, "league_logo_path": league.league_logo_path} for league in leagues]
    
    def get_all_teams(self):
        """Get all teams from the database"""
        teams = self.session.query(FootballTeam).all()
        return [{"team_id": team.team_id, "team_name": team.team_name, "img_path": team.img_path} for team in teams]

    def get_team_by_id(self, team_id):
        """Get team details by team_id"""
        team = self.session.query(FootballTeam).filter_by(team_id=team_id).first()
        if not team:
            return None
            
        # Convert string values to appropriate types
        avg_marketing_val = self._convert_currency(team.avg_marketing_val)
        total_squad_value = self._convert_currency(team.total_squad_value)
            
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "league_id": team.league_id,
            "league_name": team.league_name,
            "avg_marketing_val": avg_marketing_val,
            "total_squad_value": total_squad_value,
            "avg_age": team.avg_age,
            "num_players": team.num_players,
            "img_path": team.img_path
        }

    def get_teams_by_league(self, league_id):
        """Get all teams in a specific league"""
        teams = self.session.query(FootballTeam).filter_by(league_id=league_id).all()
        return [{"team_id": team.team_id, "team_name": team.team_name, "img_path": team.img_path} for team in teams]

    def get_footballers_by_team(self, team_id):
        """Get all footballers in a specific team"""
        footballers = self.session.query(Footballer).filter_by(team_id=team_id).all()
        return [{"footballer_id": f.footballer_id, "footballer_name": f.footballer_name, "footballer_img_path": f.footballer_img_path, "nationality_img_path": f.nationality_img_path, "birthday": f.birthday} for f in footballers]

    def get_player_by_id(self, player_id):
        """Get player details by player_id"""
        player = self.session.query(Player).filter_by(player_id=player_id).first()
        return player

    def get_players_by_footballer_id(self, footballer_id):
        """Get all player records for a specific footballer"""
        players = self.session.query(Player).filter_by(footballer_id=footballer_id).all()
        return players

    def get_team_players_data(self, team_id):
        """Get all player data for a specific team"""
        # Fetch footballers for the team
        footballers = self.session.query(Footballer).filter_by(team_id=team_id).all()
        
        # Get player details
        players_data = []
        for footballer in footballers:
            # Get player attributes
            player = self.session.query(Player).filter_by(footballer_id=footballer.footballer_id).first()
            
            if player:
                players_data.append({
                    "footballer_id": footballer.footballer_id,
                    "footballer_name": footballer.footballer_name,
                    "position": footballer.position,
                    "position_acronym": player.position_acronym,
                    "age": footballer.age,
                    "height": footballer.height,
                    "feet": footballer.feet,
                    "market_value": self._convert_currency(footballer.market_value),
                    "rating": player.rating,
                    "potential": player.potential,
                    "footballer_img_path": footballer.footballer_img_path,
                    "nationality_img_path": footballer.nationality_img_path,
                    "birthday": footballer.birthday
                })
        
        return players_data

    def get_player_positions(self, team_id):
        """Get position distribution for a specific team"""
        # Get footballers in the team
        footballers = self.session.query(Footballer).filter_by(team_id=team_id).all()
        footballer_ids = [f.footballer_id for f in footballers]
        
        # Get player data for these footballers
        players = self.session.query(Player).filter(Player.footballer_id.in_(footballer_ids)).all()
        
        # Create a DataFrame for position analysis
        positions_data = []
        for player in players:
            # Skip if position information is missing
            if not player.position_acronym:
                continue
                
            # Split multiple positions if applicable
            positions = [pos.strip() for pos in player.position_acronym.split(',')]
            for pos in positions:
                positions_data.append({
                    'footballer_id': player.footballer_id,
                    'footballer_name': player.footballer_name,
                    'position_acronym': pos,
                    'rating': player.rating,
                    'potential': player.potential
                })
        
        # Convert to DataFrame
        if not positions_data:
            return []  # Return empty list if no position data available
            
        df = pd.DataFrame(positions_data)
        
        # Group by position to get counts
        position_counts = df.groupby('position_acronym').size().reset_index(name='count')
        
        return position_counts.to_dict('records')

    def analyze_team_positions(self, team_id):
        """Analyze position distribution for a team"""
        # Get all players for the team
        players_data = self.get_team_players_data(team_id)
        
        if not players_data:
            return []
            
        # Create DataFrame for analysis
        df = pd.DataFrame(players_data)
        
        # Explode position_acronym if it contains multiple positions
        df["position_acronym_list"] = df["position_acronym"].apply(
            lambda x: [pos.strip() for pos in x.split(',')] if isinstance(x, str) else []
        )
        df = df.explode("position_acronym_list")
        
        # Group by position
        position_stats = df.groupby("position_acronym_list").agg(
            player_count=("position_acronym_list", "count"),
            total_market_value=("market_value", "sum"),
            average_market_value=("market_value", "mean"),
            total_age=("age", "sum")
        ).reset_index()
        
        # Convert to dictionary for easy serialization
        return position_stats.rename(columns={"position_acronym_list": "position"}).to_dict("records")

    def calculate_player_age(self, player):
        """Bir oyuncunun yaşını hesapla"""
        # Player modelinde birthday alanı varsa kullan
        if hasattr(player, 'birthday') and player.birthday:
            try:
                birth_date = player.birthday
                today = datetime.now()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                return age
            except:
                pass
        
        # Footballer tablosundan futbolcu bilgilerini al
        footballer = self.session.query(Footballer).filter_by(footballer_id=player.footballer_id).first()
        if footballer and hasattr(footballer, 'birthday') and footballer.birthday:
            try:
                birth_date = footballer.birthday
                today = datetime.now()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                return age
            except:
                pass
        
        # Yaş bilgisi bulunamazsa oyuncunun potansiyel ve reytingine göre tahmini yaş
        if hasattr(player, 'potential') and hasattr(player, 'rating') and player.potential and player.rating:
            age_estimate = 35 - ((player.potential - player.rating) / 2)
            return max(17, min(40, age_estimate))  # 17-40 yaş aralığında sınırla
        
        return 25  # Varsayılan yaş

    def calculate_market_value(self, player):
        """Bir oyuncunun market değerini hesapla/tahmin et"""
        # Player modelinde market_value alanı varsa kullan
        if hasattr(player, 'market_value') and player.market_value:
            return self._convert_currency(player.market_value)
        
        # Footballer tablosundan market değerini al
        footballer = self.session.query(Footballer).filter_by(footballer_id=player.footballer_id).first()
        if footballer and hasattr(footballer, 'market_value') and footballer.market_value:
            return self._convert_currency(footballer.market_value)
        
        # Market değeri yoksa rating ve potential'e göre hesapla
        base_value = 500000  # Baz değer
        
        if hasattr(player, 'rating') and player.rating:
            rating_factor = (player.rating / 70) ** 2
            base_value *= rating_factor
            
        if hasattr(player, 'potential') and player.potential:
            potential_factor = (player.potential / 70) ** 1.5
            base_value *= potential_factor
            
        # Yaşa göre düzelt
        age = self.calculate_player_age(player)
        if age < 23:
            base_value *= 1.5  # Genç oyuncular için değer artışı
        elif age > 30:
            base_value *= max(0.2, 1 - ((age - 30) * 0.1))  # Yaşlı oyuncular için değer azalışı
            
        return max(100000, min(100000000, base_value))  # 100k - 100M arasında sınırla

    def find_critical_positions(self, team_id):
        """Find critical positions that need reinforcement for a team"""
        # İlk olarak pozisyon analizini yap
        position_stats = self.analyze_team_positions(team_id)
        
        if not position_stats:
            # Alternatif olarak daha basit pozisyon analizini kullan
            footballers = self.session.query(Footballer).filter_by(team_id=team_id).all()
            footballer_ids = [f.footballer_id for f in footballers]
            players = self.session.query(Player).filter(Player.footballer_id.in_(footballer_ids)).all()
            
            # Pozisyon analizi için veri yapısı oluştur
            position_stats = {}
            
            for player in players:
                # Pozisyon bilgisi yoksa atla
                if not player.position_acronym:
                    continue
                    
                # Birden fazla pozisyon varsa ayır
                positions = [pos.strip() for pos in player.position_acronym.split(',')]
                for pos in positions:
                    if pos not in position_stats:
                        position_stats[pos] = {
                            'player_count': 0,
                            'total_age': 0,
                            'average_market_value': 0,
                            'position': pos
                        }
                    
                    # Oyuncu yaşını hesapla
                    age = self.calculate_player_age(player)
                    
                    # Market değerini hesapla
                    market_value = self.calculate_market_value(player)
                    
                    position_stats[pos]['player_count'] += 1
                    position_stats[pos]['total_age'] += age
                    position_stats[pos]['average_market_value'] = ((position_stats[pos]['average_market_value'] * 
                                                                   (position_stats[pos]['player_count'] - 1)) + 
                                                                   market_value) / position_stats[pos]['player_count']
            
            # Dictionary'i listeye çevir
            position_stats = [stats for pos, stats in position_stats.items()]
        
        # Offensive positions (CF, SS, ST) as a group
        offensive_positions = ['CF', 'SS', 'ST']
        offensive_data = [p for p in position_stats if p.get('position') in offensive_positions]
        offensive_count = sum(p.get('player_count', 0) for p in offensive_data)
        total_offensive_age = sum(p.get('total_age', 0) for p in offensive_data)
        avg_offensive_market_value = np.mean([p.get('average_market_value', 0) for p in offensive_data]) if offensive_data else 0
        
        # Missing positions dictionary
        missing = {}
        
        # Evaluate offensive group as a whole
        if offensive_count < self.ideal_position_distribution['OFF']:
            age_factor = (total_offensive_age / offensive_count) if offensive_count > 0 else 100
            need_score = (self.ideal_position_distribution['OFF'] - offensive_count) * 1.5
            need_score += (age_factor / 30)
            need_score += (1 / (avg_offensive_market_value + 1)) * 1000000  # Market değeri etkisini ayarla
            missing['OFF'] = need_score
        
        # Add all positions to missing with a default score if they don't exist at all
        existing_positions = [p.get('position') for p in position_stats]
        for position in self.ideal_position_distribution.keys():
            if position == 'OFF':
                continue  # Skip offensive group here since it's already handled
            
            # Check if position exists in position_stats
            if position not in existing_positions:
                missing[position] = self.ideal_position_distribution[position] * 2  # High need score for completely missing positions
        
        # Evaluate existing positions individually
        for position, ideal_count in self.ideal_position_distribution.items():
            if position == 'OFF' or position in missing:
                continue  # Skip already handled positions
                
            pos_data = next((p for p in position_stats if p.get('position') == position), None)
            if not pos_data:
                continue
                
            current_count = pos_data.get('player_count', 0)
            total_age = pos_data.get('total_age', 0)
            avg_market_value = pos_data.get('average_market_value', 0)
            
            if current_count < ideal_count:
                age_factor = (total_age / current_count) if current_count > 0 else 100
                need_score = (ideal_count - current_count) * 1.5
                need_score += (age_factor / 30)
                need_score += (1 / (avg_market_value + 1)) * 1000000  # Market değeri etkisini ayarla
                missing[position] = need_score
        
        # Sort positions by need score
        sorted_missing = sorted(missing.items(), key=lambda x: x[1], reverse=True)
        
        # Format for API response
        result = []
        for pos, score in sorted_missing[:3]:  # Get top 3 critical positions
            position_label = "Offensive Group (CF, SS, ST)" if pos == 'OFF' else pos
            result.append({
                "position": pos,
                "position_label": position_label,
                "need_score": round(score, 2)
            })
            
        return result

    def calculate_player_score(self, player_data, position):
        """Calculate a player's score for a specific position"""
        # Get relevant features for the position
        features = self.position_features.get(position, [])
        
        # Initialize feature score
        feature_score = 0
        
        # Handle different types of player_data (dictionary or object)
        if isinstance(player_data, dict):
            # Calculate score from dictionary data
            for feature in features:
                snake_case_feature = feature.replace('-', '_')
                if snake_case_feature in player_data and player_data[snake_case_feature]:
                    feature_score += player_data[snake_case_feature] * 0.15
            
            # Age score - younger players get higher scores
            age = player_data.get('age')
            age_score = 0.3 / (age + 1) if age else 0
            
            # Rating and potential scores
            rating_score = player_data.get('rating', 0) * 0.3 if player_data.get('rating') else 0
            potential_score = player_data.get('potential', 0) * 0.4 if player_data.get('potential') else 0
        else:
            # Calculate score from object data
            for feature in features:
                snake_case_feature = feature.replace('-', '_')
                if hasattr(player_data, snake_case_feature) and getattr(player_data, snake_case_feature) is not None:
                    feature_score += getattr(player_data, snake_case_feature) * 0.15
            
            # Age score calculation
            age = self.calculate_player_age(player_data)
            age_score = 0.3 / (age + 1) if age else 0
            
            # Rating and potential scores
            rating_score = player_data.rating * 0.3 if hasattr(player_data, 'rating') and player_data.rating else 0
            potential_score = player_data.potential * 0.4 if hasattr(player_data, 'potential') and player_data.potential else 0
        
        # Calculate total score
        total_score = feature_score + age_score + rating_score + potential_score
        return total_score

    def recommend_players(self, team_id, position):
        """Recommend players from other teams for a specific position based on selected team's needs"""
        # Get the selected team to establish baseline
        team = self.get_team_by_id(team_id)
        if not team:
            return []
            
        # Define which positions to look for
        target_positions = []
        if position == 'OFF':
            target_positions = ['CF', 'SS', 'ST']
        else:
            target_positions = [position]
        
        # Get all footballers from the selected team
        team_footballers = self.session.query(Footballer).filter_by(team_id=team_id).all()
        team_footballer_ids = [f.footballer_id for f in team_footballers]
        
        # Get player data for the selected team
        team_players = self.session.query(Player).filter(Player.footballer_id.in_(team_footballer_ids)).all()
        
        # Calculate average rating of the selected team
        team_ratings = [p.rating for p in team_players if p.rating is not None]
        avg_team_rating = sum(team_ratings) / len(team_ratings) if team_ratings else 70  # Default if no ratings
        
        # Maximum market value cap based on team's average
        max_market_value = team.get('avg_marketing_val', 1000000) * 1.5 if team.get('avg_marketing_val') else 1000000
        
        # Get all footballers from OTHER teams (explicitly exclude the selected team)
        other_team_footballers = self.session.query(Footballer).filter(Footballer.team_id != team_id).all()
        other_footballer_ids = [f.footballer_id for f in other_team_footballers]
        
        # Get player data for other teams' footballers
        other_team_players = self.session.query(Player).filter(
            Player.footballer_id.in_(other_footballer_ids)
        ).all()
        
        # Filter players by position
        matches = []
        for player in other_team_players:
            # Skip if no position data
            if not player.position_acronym:
                continue
                
            # Check if player plays in any target position
            player_positions = [pos.strip() for pos in player.position_acronym.split(',')]
            
            matching_positions = [pos for pos in player_positions if pos in target_positions]
            if not matching_positions:
                continue
                
            # Use the first matching position for calculations
            calc_position = matching_positions[0]
            
            # Get footballer for this player
            footballer = self.session.query(Footballer).filter_by(footballer_id=player.footballer_id).first()
            if not footballer:
                continue
                
            # Check market value constraint
            player_market_value = self.calculate_market_value(player)
            if player_market_value and player_market_value > max_market_value:
                continue
                
            # Check age constraint (prefer younger players)
            age = self.calculate_player_age(player)
            if age and age >= 30:
                continue
                
            # Check rating constraint
            if player.rating and player.rating > (avg_team_rating + 15):
                continue
            
            # Calculate player score for this position
            player_score = self.calculate_player_score(player, calc_position)
            
            # Get player's current team
            player_team = self.session.query(FootballTeam).filter_by(team_id=footballer.team_id).first()
            if not player_team:
                continue
                
            # Add to matches if score is good enough
            if player_score >= avg_team_rating * 0.85:
                matches.append({
                    'footballer_id': player.footballer_id,
                    'footballer_name': player.footballer_name,
                    'position': calc_position,
                    'current_team': player_team.team_name,
                    'current_team_img': player_team.img_path,
                    'rating': player.rating,
                    'potential': player.potential,
                    'age': age,
                    'market_value': player_market_value,
                    'player_score': player_score,
                    'footballer_img_path': footballer.footballer_img_path,
                    'nationality_img_path': footballer.nationality_img_path
                })
        
        # Sort by player score in descending order
        recommendations = sorted(matches, key=lambda x: x['player_score'], reverse=True)
        
        # Return top 10 recommendations
        return recommendations[:24]

    def recommend_players_by_team_needs(self, team_id):
        """Recommend players based on team's critical position needs"""
        # Önce kritik mevkileri bul
        critical_positions = self.find_critical_positions(team_id)
        
        if not critical_positions:
            return {
                "critical_positions": [],
                "recommendations": []
            }
        
        # Tüm kritik mevkiler için öneriler hazırla
        recommendations = []
        for critical_pos in critical_positions:
            position = critical_pos["position"]
            
            # Bu mevki için oyuncu önerisi yap
            recommended_players = self.recommend_players(team_id, position)
            
            recommendations.append({
                "position": position,
                "position_label": critical_pos["position_label"],
                "need_score": critical_pos["need_score"],
                "recommended_players": recommended_players
            })
        
        return {
            "critical_positions": critical_positions,
            "recommendations": recommendations
        }
    
    def get_team_recommendation_summary(self, team_id):
        """Get a summary of team needs and player recommendations"""
        team = self.get_team_by_id(team_id)
        if not team:
            return {
                "status": "error",
                "message": "Team not found"
            }
        
        # Takım analizlerini yap
        position_analysis = self.analyze_team_positions(team_id)
        critical_positions = self.find_critical_positions(team_id)
        recommendations = self.recommend_players_by_team_needs(team_id)
        
        return {
            "team": team,
            "position_analysis": position_analysis,
            "critical_positions": critical_positions,
            "player_recommendations": recommendations
        }