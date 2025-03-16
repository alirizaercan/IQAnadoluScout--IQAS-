from models.league import League
from models.football_team import FootballTeam
from models.footballer import Footballer
from models.player import Player
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from datetime import datetime

class TransferService:
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
        except Exception as e:
            print(f"Error converting currency: {value}, Error: {e}")
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
    
    def get_market_value_range(self):
        """Get minimum and maximum market values from all footballers"""
        footballers = self.session.query(Footballer).all()
        
        min_value = float('inf')
        max_value = 0
        
        for footballer in footballers:
            if footballer.market_value:
                value = self._convert_currency(footballer.market_value)
                if value:
                    min_value = min(min_value, value)
                    max_value = max(max_value, value)
        
        # If no valid values found, return defaults
        if min_value == float('inf'):
            min_value = 0
            
        return {
            "min_value": min_value,
            "max_value": max_value
        }
    
    def get_players_by_budget(self, budget, limit=200, league_id=None):
        query = self.session.query(Footballer)
        
        # Lig filtresi (sadece league_id belirtilmişse uygula)
        if league_id:
            teams = self.session.query(FootballTeam).filter_by(league_id=league_id).all()
            team_ids = [team.team_id for team in teams]
            query = query.filter(Footballer.team_id.in_(team_ids))
        
        footballers = query.all()
        players_data = []
        
        for footballer in footballers:
            market_value = self._convert_currency(footballer.market_value)
            if market_value is None or market_value > budget:
                continue
                
            player = self.session.query(Player).filter_by(footballer_id=footballer.footballer_id).first()
            if not player:
                continue
                
            team = self.session.query(FootballTeam).filter_by(team_id=footballer.team_id).first()
            league = None
            if team:
                league = self.session.query(League).filter_by(league_id=team.league_id).first()
            
            players_data.append({
                "footballer_id": footballer.footballer_id,
                "footballer_name": footballer.footballer_name,
                "position": footballer.position,
                "position_acronym": player.position_acronym,
                "age": footballer.age,
                "market_value": market_value,
                "rating": player.rating,
                "potential": player.potential,
                "birthday": footballer.birthday.strftime('%d %B %Y') if footballer.birthday else None,
                "footballer_img_path": footballer.footballer_img_path,
                "nationality_img_path": footballer.nationality_img_path,
                "team_name": team.team_name if team else None,
                "team_img_path": team.img_path if team else None,
                "league_name": league.league_name if league else None,
                "league_logo_path": league.league_logo_path if league else None,
                'positioning': player.positioning,
                'acceleration': player.acceleration,
                'passing': player.passing,
                'long_shots': player.long_shots,
                'marking': player.marking,
                'decisions': player.decisions,
                'finishing': player.finishing,
                'leadership': player.leadership,
                'dribbling': player.dribbling,
                'concentration': player.concentration,
                'fitness': player.natural_fitness,
                'tackling': player.tackling,
                'stamina': player.stamina,
                'jumping': player.jumping_reach,
                'heading': player.heading,
                'balance': player.balance
            })
            
            if len(players_data) >= limit:
                break
        
        players_data.sort(key=lambda x: x["market_value"], reverse=True)
        return players_data[:limit]
    
    def get_all_leagues(self):
        """Get all leagues from the database"""
        leagues = self.session.query(League).all()
        return [{"league_id": league.league_id, "league_name": league.league_name, "league_logo_path": league.league_logo_path} for league in leagues]
    
    def get_all_teams(self):
        """Tüm takımları getir"""
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
        return [{"footballer_id": f.footballer_id, "footballer_name": f.footballer_name, "footballer_img_path": f.footballer_img_path, "nationality_img_path": f.nationality_img_path, "birthday": f.birthday.strftime('%d %B %Y') if f.birthday else None} for f in footballers]
    
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
                    'positioning': player.positioning,
                    'acceleration': player.acceleration,
                    'passing': player.passing,
                    'long_shots': player.long_shots,
                    'marking': player.marking,
                    'decisions': player.decisions,
                    'finishing': player.finishing,
                    'leadership': player.leadership,
                    'dribbling': player.dribbling,
                    'concentration': player.concentration,
                    'fitness': player.natural_fitness,
                    'tackling': player.tackling,
                    'stamina': player.stamina,
                    'jumping': player.jumping_reach,
                    'heading': player.heading,
                    'balance': player.balance,
                    "footballer_img_path": footballer.footballer_img_path,
                    "nationality_img_path": footballer.nationality_img_path,
                    "birthday": footballer.birthday.strftime('%d %B %Y') if footballer.birthday else None
                })
        
        return players_data
    
    def calculate_player_age(self, player):
        """Calculate a player's age from birthday"""
        # First, get the footballer associated with the player
        footballer = None
        
        # If player has footballer_id, fetch the footballer
        if hasattr(player, 'footballer_id'):
            footballer = self.session.query(Footballer).filter_by(footballer_id=player.footballer_id).first()
        
        # Try to get birthday from footballer
        if footballer and hasattr(footballer, 'birthday') and footballer.birthday is not None:
            try:
                birth_date = footballer.birthday
                today = datetime.now()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                return age
            except Exception as e:
                # Log error or handle exception
                pass
        
        # If age is directly available in player object, use it
        if hasattr(player, 'age') and player.age is not None:
            return player.age
            
        # If age is directly available in footballer object, use it
        if footballer and hasattr(footballer, 'age') and footballer.age is not None:
            return footballer.age
        
        # If no birthday or age available, estimate from potential and rating
        if hasattr(player, 'potential') and hasattr(player, 'rating') and player.potential and player.rating:
            age_estimate = 35 - ((player.potential - player.rating) / 2)
            return max(17, min(40, age_estimate))  # Keep age between 17-40
        
        return 25  # Default age if no other method works
    
    def get_filtered_players(self, budget=None, position=None, league_id=None, min_age=None, max_age=None, min_rating=None, limit=200, value_tolerance=0.1):
        query = self.session.query(Footballer)
        
        # Lig filtresi (sadece league_id belirtilmişse uygula)
        if league_id:
            teams = self.session.query(FootballTeam).filter_by(league_id=league_id).all()
            team_ids = [team.team_id for team in teams]
            query = query.filter(Footballer.team_id.in_(team_ids))
            print(f"Filtering players from league_id: {league_id}, teams: {team_ids}")
        
        footballers = query.all()
        players_data = []
        
        for footballer in footballers:
            market_value = self._convert_currency(footballer.market_value)
            print(f"Footballer: {footballer.footballer_name}, Market Value: {market_value}, League: {footballer.team.league.league_name if footballer.team else 'Unknown'}")
            
            # Market value filtresi
            if budget:
                if market_value is None:
                    continue
                # Minimum değer 0, maksimum değer kullanıcının girdiği bütçe + tolerans
                if not (0 <= market_value <= budget * (1 + value_tolerance)):
                    continue
                
            player = self.session.query(Player).filter_by(footballer_id=footballer.footballer_id).first()
            if not player:
                continue
                
            # Pozisyon filtresi
            if position and player.position_acronym:
                if position not in player.position_acronym.split(','):
                    continue
            
            # Yaş filtresi
            age = footballer.age if footballer.age else self.calculate_player_age(player)
            if min_age and age < min_age:
                continue
            if max_age and age > max_age:
                continue
            
            # Rating filtresi
            if min_rating and (not player.rating or player.rating < min_rating):
                continue
            
            # Takım ve lig bilgileri
            team = self.session.query(FootballTeam).filter_by(team_id=footballer.team_id).first()
            league = None
            if team:
                league = self.session.query(League).filter_by(league_id=team.league_id).first()
            
            players_data.append({
                "footballer_id": footballer.footballer_id,
                "footballer_name": footballer.footballer_name,
                "position": footballer.position,
                "position_acronym": player.position_acronym,
                "age": age,
                "market_value": market_value,
                "rating": player.rating,
                "potential": player.potential,
                'positioning': player.positioning,
                'acceleration': player.acceleration,
                'passing': player.passing,
                'long_shots': player.long_shots,
                'marking': player.marking,
                'decisions': player.decisions,
                'finishing': player.finishing,
                'leadership': player.leadership,
                'dribbling': player.dribbling,
                'concentration': player.concentration,
                'fitness': player.natural_fitness,
                'tackling': player.tackling,
                'stamina': player.stamina,
                'jumping': player.jumping_reach,
                'heading': player.heading,
                'balance': player.balance,
                "birthday": footballer.birthday.strftime('%d %B %Y') if footballer.birthday else None,
                "footballer_img_path": footballer.footballer_img_path,
                "nationality_img_path": footballer.nationality_img_path,
                "team_name": team.team_name if team else None,
                "team_img_path": team.img_path if team else None,
                "league_name": league.league_name if league else None,
                "league_logo_path": league.league_logo_path if league else None
            })
            
            if len(players_data) >= limit:
                break
        
        players_data.sort(key=lambda x: x["market_value"], reverse=True)
        return players_data[:limit]
    
    def get_transfer_dashboard_data(self):
        """Get data for the transfer dashboard"""
        # Get market value range
        market_value_range = self.get_market_value_range()
        
        # Get all leagues for filtering
        leagues = self.get_all_leagues()
        
        # Get position options
        positions = list(self.position_mapping.values())
        positions = sorted(list(set(positions)))  # Remove duplicates and sort
        
        return {
            "market_value_range": market_value_range,
            "leagues": leagues,
            "positions": positions
        }
    
    def get_player_details(self, footballer_id):
        """Get detailed information about a player"""
        footballer = self.session.query(Footballer).filter_by(footballer_id=footballer_id).first()
        if not footballer:
            return None
        
        player = self.session.query(Player).filter_by(footballer_id=footballer_id).first()
        if not player:
            return None
        
        team = self.session.query(FootballTeam).filter_by(team_id=footballer.team_id).first()
        league = None
        if team:
            league = self.session.query(League).filter_by(league_id=team.league_id).first()
        
        # Combine all data
        player_details = {
            "footballer_id": footballer.footballer_id,
            "footballer_name": footballer.footballer_name,
            "position": footballer.position,
            "position_acronym": player.position_acronym,
            "age": footballer.age if footballer.age else self.calculate_player_age(player),
            "height": footballer.height,
            "feet": footballer.feet,
            "market_value": self._convert_currency(footballer.market_value),
            "rating": player.rating,
            "potential": player.potential,
            'positioning': player.positioning,
            'acceleration': player.acceleration,
            'passing': player.passing,
            'long_shots': player.long_shots,
            'marking': player.marking,
            'decisions': player.decisions,
            'finishing': player.finishing,
            'leadership': player.leadership,
            'dribbling': player.dribbling,
            'concentration': player.concentration,
            'fitness': player.natural_fitness,
            'tackling': player.tackling,
            'stamina': player.stamina,
            'jumping': player.jumping_reach,
            'heading': player.heading,
            'balance': player.balance,
            "footballer_img_path": footballer.footballer_img_path,
            "nationality_img_path": footballer.nationality_img_path,
            "birthday": footballer.birthday.strftime('%d %B %Y') if footballer.birthday else None,
            "team_name": team.team_name if team else None,
            "team_id": team.team_id if team else None,
            "team_img_path": team.img_path if team else None,
            "league_name": league.league_name if league else None,
            "league_id": league.league_id if league else None,
            "league_logo_path": league.league_logo_path if league else None
        }
        
        # Add all player attributes
        for attr in dir(player):
            if not attr.startswith('_') and attr not in ['footballer_id', 'player_id', 'position_acronym']:
                player_details[attr] = getattr(player, attr)
        
        return player_details

    def get_similar_players(self, footballer_id, limit=10):
        """Find similar players based on attributes"""
        # Get the target player
        target_footballer = self.session.query(Footballer).filter_by(footballer_id=footballer_id).first()
        if not target_footballer:
            return []
        
        target_player = self.session.query(Player).filter_by(footballer_id=footballer_id).first()
        if not target_player:
            return []
        
        # Get target player position
        if not target_player.position_acronym:
            return []
        
        # Get primary position
        primary_position = target_player.position_acronym.split(',')[0].strip()
        
        # Get important attributes for this position
        key_attributes = self.position_features.get(primary_position, [])
        
        # If no specific attributes found, use general ones
        if not key_attributes:
            key_attributes = ['passing', 'tackling', 'finishing', 'dribbling', 'acceleration']
        
        # Get all players with the same primary position
        all_players = self.session.query(Player).all()
        similar_players = []
        
        for player in all_players:
            # Skip the target player
            if player.footballer_id == footballer_id:
                continue
            
            # Skip players with no position
            if not player.position_acronym:
                continue
            
            # Check if positions overlap
            player_positions = player.position_acronym.split(',')
            if primary_position not in player_positions:
                continue
            
            # Get footballer data
            footballer = self.session.query(Footballer).filter_by(footballer_id=player.footballer_id).first()
            if not footballer:
                continue
            
            # Calculate similarity score
            similarity_score = 0
            total_attributes = 0
            
            for attr in key_attributes:
                if hasattr(target_player, attr) and hasattr(player, attr):
                    target_val = getattr(target_player, attr)
                    player_val = getattr(player, attr)
                    
                    if target_val is not None and player_val is not None:
                        # Calculate similarity (0-100 scale)
                        similarity = 100 - abs(target_val - player_val)
                        similarity_score += similarity
                        total_attributes += 1
            
            # Add rating similarity
            if target_player.rating and player.rating:
                rating_similarity = 100 - abs(target_player.rating - player.rating)
                similarity_score += rating_similarity * 2  # Give more weight to rating
                total_attributes += 2
            
            # Calculate overall similarity
            if total_attributes > 0:
                overall_similarity = similarity_score / total_attributes
            else:
                overall_similarity = 0
            
            # Get team data
            team = self.session.query(FootballTeam).filter_by(team_id=footballer.team_id).first()
            league = None
            if team:
                league = self.session.query(League).filter_by(league_id=team.league_id).first()
            
            # Add to similar players list if similarity is good enough
            if overall_similarity > 70:  # Only include players with good similarity
                similar_players.append({
                    "footballer_id": footballer.footballer_id,
                    "footballer_name": footballer.footballer_name,
                    "position": footballer.position,
                    "position_acronym": player.position_acronym,
                    "age": footballer.age if footballer.age else self.calculate_player_age(player),
                    "market_value": self._convert_currency(footballer.market_value),
                    "rating": player.rating,
                    "potential": player.potential,
                    'positioning': player.positioning,
                    'acceleration': player.acceleration,
                    'passing': player.passing,
                    'long_shots': player.long_shots,
                    'marking': player.marking,
                    'decisions': player.decisions,
                    'finishing': player.finishing,
                    'leadership': player.leadership,
                    'dribbling': player.dribbling,
                    'concentration': player.concentration,
                    'fitness': player.natural_fitness,
                    'tackling': player.tackling,
                    'stamina': player.stamina,
                    'jumping': player.jumping_reach,
                    'heading': player.heading,
                    'balance': player.balance,
                    "similarity_score": round(overall_similarity, 2),
                    "footballer_img_path": footballer.footballer_img_path,
                    "nationality_img_path": footballer.nationality_img_path,
                    "team_name": team.team_name if team else None,
                    "team_img_path": team.img_path if team else None,
                    "league_name": league.league_name if league else None,
                    "league_logo_path": league.league_logo_path if league else None
                })
        
        # Sort by similarity score
        similar_players.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return similar_players[:limit]