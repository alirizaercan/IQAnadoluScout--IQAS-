# backend/services/video_analysis_service.py
import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import json
from datetime import datetime
import os
from models.match_analysis import MatchAnalysis
from models.football_team import FootballTeam
from utils.database import Database

class VideoAnalysisService:
    def __init__(self):
        # Load YOLOv8 model (football-specific custom model would be better)
        self.model = YOLO('yolov8s.pt')  # Can replace with custom trained model
        self.db = Database()
        
        # Football-specific class IDs (assuming custom model)
        self.class_ids = {
            'player': 0,
            'ball': 1,
            'referee': 2,
            'goalpost': 3
        }
        
    def analyze_video(self, video_path, home_team_name, away_team_name, match_date):
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        # Initialize analysis variables
        frame_count = 0
        home_possession_frames = 0
        away_possession_frames = 0
        home_players = defaultdict(list)
        away_players = defaultdict(list)
        ball_positions = []
        formations = {
            'home': defaultdict(int),
            'away': defaultdict(int)
        }
        current_possession = None
        
        # Process video frame by frame (sample every nth frame for performance)
        sample_rate = max(1, int(fps / 2))  # Sample 2 frames per second
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            if frame_count % sample_rate != 0:
                continue
                
            # Detect objects in frame
            results = self.model(frame, verbose=False)
            
            # Process detections
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                
                # Separate players, ball, etc.
                players = []
                ball = None
                
                for box, cls, conf in zip(boxes, classes, confidences):
                    if cls == self.class_ids['ball'] and conf > 0.5:
                        ball = box
                    elif cls == self.class_ids['player'] and conf > 0.7:
                        players.append(box)
                
                # Track ball possession
                if ball is not None:
                    possession = self.determine_possession(ball, players, frame.shape)
                    if possession == 'home':
                        home_possession_frames += 1
                    elif possession == 'away':
                        away_possession_frames += 1
                    
                    current_possession = possession
                
                # Track player positions for heatmap and formation
                if len(players) >= 20:  # Minimum players for analysis
                    home_formation, away_formation = self.analyze_formations(players, frame.shape)
                    
                    if home_formation:
                        formations['home'][home_formation] += 1
                    if away_formation:
                        formations['away'][away_formation] += 1
                
                # Store ball positions for pass analysis
                if ball is not None:
                    ball_positions.append({
                        'frame': frame_count,
                        'time': frame_count / fps,
                        'x': (ball[0] + ball[2]) / 2 / frame.shape[1],
                        'y': (ball[1] + ball[3]) / 2 / frame.shape[0],
                        'possession': current_possession
                    })
        
        cap.release()
        
        # Calculate possession percentages
        total_possession_frames = home_possession_frames + away_possession_frames
        if total_possession_frames > 0:
            home_possession = (home_possession_frames / total_possession_frames) * 100
            away_possession = (away_possession_frames / total_possession_frames) * 100
        else:
            home_possession = 50
            away_possession = 50
        
        # Determine most common formations
        home_most_common = max(formations['home'].items(), key=lambda x: x[1], default=('4-4-2', 0))
        away_most_common = max(formations['away'].items(), key=lambda x: x[1], default=('4-4-2', 0))
        
        # Count formation changes
        home_formation_changes = len(formations['home']) - 1
        away_formation_changes = len(formations['away']) - 1
        
        # Create heatmaps (simplified for this example)
        home_heatmap = self.generate_heatmap(home_players, frame.shape)
        away_heatmap = self.generate_heatmap(away_players, frame.shape)
        
        # Create match analysis record
        analysis = MatchAnalysis(
            home_team_id=self.get_team_id(home_team_name),
            away_team_id=self.get_team_id(away_team_name),
            match_date=match_date,
            video_path=video_path,
            home_possession_percentage=home_possession,
            away_possession_percentage=away_possession,
            home_formation=home_most_common[0],
            away_formation=away_most_common[0],
            home_formation_changes=home_formation_changes,
            away_formation_changes=away_formation_changes,
            home_heatmap=json.dumps(home_heatmap),
            away_heatmap=json.dumps(away_heatmap),
            possession_timeline=json.dumps(self.generate_possession_timeline(ball_positions)),
            formation_changes=json.dumps({
                'home': dict(formations['home']),
                'away': dict(formations['away'])
            })
        )
        
        # Save to database
        session = self.db.connect()
        try:
            session.add(analysis)
            session.commit()
            return analysis
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self.db.close(session)
    
    def determine_possession(self, ball_box, player_boxes, frame_shape):
        """Determine which team has possession based on ball proximity to players"""
        ball_center = ((ball_box[0] + ball_box[2]) / 2, (ball_box[1] + ball_box[3]) / 2)
        
        # Simple heuristic: team with more players near the ball has possession
        home_near = 0
        away_near = 0
        
        for player_box in player_boxes:
            player_center = ((player_box[0] + player_box[2]) / 2, (player_box[1] + player_box[3]) / 2)
            distance = np.sqrt((ball_center[0] - player_center[0])**2 + (ball_center[1] - player_center[1])**2)
            
            # Determine if player is home or away (simplified - would need team detection)
            # This is a placeholder - in reality you'd need team classification
            if player_center[0] < frame_shape[1] / 2:
                home_near += 1 if distance < 100 else 0
            else:
                away_near += 1 if distance < 100 else 0
        
        if home_near > away_near:
            return 'home'
        elif away_near > home_near:
            return 'away'
        return None
    
    def analyze_formations(self, player_boxes, frame_shape):
        """Analyze team formations based on player positions"""
        # Split players into home and away teams (simplified)
        home_players = [box for box in player_boxes if box[0] < frame_shape[1] / 2]
        away_players = [box for box in player_boxes if box[0] >= frame_shape[1] / 2]
        
        # Analyze formations (simplified)
        home_formation = self.detect_formation(home_players, frame_shape)
        away_formation = self.detect_formation(away_players, frame_shape)
        
        return home_formation, away_formation
    
    def detect_formation(self, player_boxes, frame_shape):
        """Detect football formation from player positions"""
        if len(player_boxes) < 10:
            return None
            
        # Get player y-coordinates (vertical positions)
        y_positions = [(box[1] + box[3]) / 2 for box in player_boxes]
        y_positions.sort()
        
        # Simple formation detection based on player distribution
        # This is a placeholder - real implementation would be more sophisticated
        quarter = len(y_positions) // 4
        defenders = sum(1 for y in y_positions if y < frame_shape[0] * 0.4)
        midfielders = sum(1 for y in y_positions if frame_shape[0] * 0.4 <= y < frame_shape[0] * 0.7)
        attackers = sum(1 for y in y_positions if y >= frame_shape[0] * 0.7)
        
        # Common formations
        if defenders == 4 and midfielders == 4 and attackers == 2:
            return "4-4-2"
        elif defenders == 4 and midfielders == 3 and attackers == 3:
            return "4-3-3"
        elif defenders == 3 and midfielders == 5 and attackers == 2:
            return "3-5-2"
        elif defenders == 5 and midfielders == 3 and attackers == 2:
            return "5-3-2"
        else:
            return "Unknown"
    
    def generate_heatmap(self, player_positions, frame_shape):
        """Generate simplified heatmap of player positions"""
        heatmap = np.zeros((10, 10))  # 10x10 grid
        
        for positions in player_positions.values():
            for x, y in positions:
                grid_x = min(int(x * 10), 9)
                grid_y = min(int(y * 10), 9)
                heatmap[grid_y, grid_x] += 1
                
        return heatmap.tolist()
    
    def generate_possession_timeline(self, ball_positions):
        """Generate timeline of possession changes"""
        timeline = []
        current_possession = None
        
        for pos in ball_positions:
            if pos['possession'] != current_possession:
                timeline.append({
                    'time': pos['time'],
                    'possession': pos['possession']
                })
                current_possession = pos['possession']
                
        return timeline
    
    def get_team_id(self, team_name):
        """Get team ID from database by name"""
        session = self.db.connect()
        try:
            team = session.query(FootballTeam).filter(FootballTeam.team_name.ilike(f'%{team_name}%')).first()
            return team.team_id if team else None
        finally:
            self.db.close(session)