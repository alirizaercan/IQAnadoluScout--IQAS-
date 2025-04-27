# backend/services/video_analysis_service.py
import os
import cv2
import numpy as np
import json
import pickle
from datetime import datetime
from sqlalchemy.orm import Session

# Video analysis model imports
from ultralytics import YOLO

# Import our custom modules
from football_analysis_model.utils.video_utils import read_video, save_video
from football_analysis_model.trackers.tracker import Tracker
from football_analysis_model.team_assigner.team_assigner import TeamAssigner
from football_analysis_model.player_ball_assigner.player_ball_assigner import PlayerBallAssigner
from football_analysis_model.camera_movement_estimator.camera_movement_estimator import CameraMovementEstimator
from football_analysis_model.view_transformer.view_transformer import ViewTransformer
from football_analysis_model.speed_and_distance_estimator.speed_and_distance_estimator import SpeedAndDistance_Estimator
from football_analysis_model.utils.bbox_utils import get_center_of_bbox, get_bbox_width, get_foot_position

from models.match_analysis import MatchAnalysis
from models.football_team import FootballTeam

class VideoAnalysisService:
    def __init__(self, session=Session):
        self.session = session
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Model path
        self.model_path = os.path.normpath(
            os.path.join(current_dir, '..', 'football_analysis_model', 'models', 'best.pt')
        )
        
        # Output directory - ensure it's in the correct location
        self.output_dir = os.path.normpath(
            os.path.join(current_dir, '..', 'uploads', 'processed_videos')
        )
        
        # Create directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Processed videos will be saved to: {self.output_dir}")
        
    def analyze_video(self, video_path, home_team_name, away_team_name, match_date):
        """
        Analyze football match video and store results in database
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Read video
            print(f"Reading video from {video_path}")
            video_frames = read_video(video_path)
            
            # Initialize tracker with YOLO model
            tracker = Tracker(self.model_path)
            
            # Get object tracks (with positions)
            tracks = tracker.get_object_tracks(video_frames, read_from_stub=False)
            tracker.add_position_to_tracks(tracks)
            
            # Estimate camera movement
            camera_movement_estimator = CameraMovementEstimator(video_frames[0])
            camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames, read_from_stub=False)
            camera_movement_estimator.add_adjust_positions_to_tracks(tracks, camera_movement_per_frame)
            
            # Transform view to field coordinates
            view_transformer = ViewTransformer()
            view_transformer.add_transformed_position_to_tracks(tracks)
            
            # Interpolate ball positions for missing frames
            tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
            
            # Calculate player speeds and distances
            speed_distance_estimator = SpeedAndDistance_Estimator()
            speed_distance_estimator.add_speed_and_distance_to_tracks(tracks)
            
            # Assign teams and colors
            team_assigner = TeamAssigner()
            team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
            
            # Process all frames and assign teams
            for frame_num, player_track in enumerate(tracks['players']):
                for player_id, track in player_track.items():
                    team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
                    tracks['players'][frame_num][player_id]['team'] = int(team)  # Ensure team is int
                    tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
            
            # Ball possession analysis
            player_assigner = PlayerBallAssigner()
            team_ball_control = []
            
            for frame_num, player_track in enumerate(tracks['players']):
                if len(tracks['ball']) > frame_num and 1 in tracks['ball'][frame_num]:
                    ball_bbox = tracks['ball'][frame_num][1]['bbox']
                    assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)
                    
                    if assigned_player != -1:
                        tracks['players'][frame_num][assigned_player]['has_ball'] = True
                        team_ball_control.append(int(tracks['players'][frame_num][assigned_player]['team']))  # Ensure int
                    else:
                        team_ball_control.append(team_ball_control[-1] if team_ball_control else 1)
                else:
                    team_ball_control.append(team_ball_control[-1] if team_ball_control else 1)
            
            team_ball_control = np.array(team_ball_control)
            
            # Generate processed video with annotations
            output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)
            output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames, camera_movement_per_frame)
            speed_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)
            
            # Save processed video as MP4 instead of AVI
            processed_video_filename = f"processed_{os.path.basename(video_path)}"
            # Ensure it has .mp4 extension
            if not processed_video_filename.lower().endswith('.mp4'):
                processed_video_filename = os.path.splitext(processed_video_filename)[0] + '.mp4'
            processed_video_path = os.path.join(self.output_dir, processed_video_filename)
            
            try:
                # Save video with MP4 codec
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # MP4 codec
                height, width = output_video_frames[0].shape[:2]
                fps = 24
                processed_video_path = os.path.join(self.output_dir, f"processed_{timestamp}.mp4")

                out = cv2.VideoWriter(processed_video_path, fourcc, fps, (width, height))
                for frame in output_video_frames:
                    out.write(frame)
                out.release()
                print(f"Successfully saved processed video to: {processed_video_path}")
            except Exception as e:
                print(f"Failed to save processed video: {str(e)}")
                raise
            
            # Calculate match statistics
            stats = self.calculate_match_statistics(tracks, team_ball_control, len(video_frames))
            
            # Get team colors
            team_colors = {
                'home_team_color': self._rgb_to_hex(team_assigner.team_colors[1]),
                'away_team_color': self._rgb_to_hex(team_assigner.team_colors[2])
            }
            
            # Get team IDs from database if they exist
            home_team = self.session.query(FootballTeam).filter(FootballTeam.team_name.ilike(f"%{home_team_name}%")).first()
            away_team = self.session.query(FootballTeam).filter(FootballTeam.team_name.ilike(f"%{away_team_name}%")).first()
            
            # Create match_analysis object with the current path
            match_analysis = MatchAnalysis(
                match_date=match_date,
                home_team_id=home_team.team_id if home_team else None,
                home_team_name=home_team_name,
                away_team_id=away_team.team_id if away_team else None,
                away_team_name=away_team_name,
                video_path=video_path,
                processed_video_path=processed_video_path,
                **stats,
                **team_colors
            )

            # Add and commit to get the ID
            self.session.add(match_analysis)
            self.session.commit()

            # If you want to rename the file with the ID now that we have it:
            if match_analysis.id:
                new_filename = f"processed_{match_analysis.id}.mp4"
                new_path = os.path.join(self.output_dir, new_filename)
                try:
                    # Rename the file
                    os.rename(processed_video_path, new_path)
                    # Update the path in the database
                    match_analysis.processed_video_path = new_path
                    self.session.commit()
                    processed_video_path = new_path
                    print(f"Renamed video file to include analysis ID: {new_path}")
                except Exception as e:
                    print(f"Warning: Could not rename video file: {str(e)}")
                    # Keep using the original path, no need to fail the whole process

            return match_analysis
                    
        except Exception as e:
            self.session.rollback()
            print(f"Error analyzing video: {str(e)}")
            raise

    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_numpy_types(x) for x in obj]
        return obj
    
    def _rgb_to_hex(self, rgb_color):
        """Convert RGB array to hex color string"""
        rgb = np.round(rgb_color).astype(int)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def calculate_match_statistics(self, tracks, team_ball_control, total_frames):
        """Calculate match statistics from video analysis with division by zero protection"""
        # Convert numpy types to native Python types
        team_ball_control = [int(x) for x in team_ball_control]
        
        # Calculate possession percentages with robust zero handling
        home_possession = sum(1 for x in team_ball_control if x == 1)
        away_possession = sum(1 for x in team_ball_control if x == 2)
        total_possession = home_possession + away_possession

        # Handle cases where no possession was detected
        if total_possession == 0:
            stats = {
                'home_possession_percentage': 0.0,
                'away_possession_percentage': 0.0,
                'home_ball_control_time': 0.0,
                'away_ball_control_time': 0.0,
            }
        else:
            stats = {
                'home_possession_percentage': float((home_possession / total_possession) * 100),
                'away_possession_percentage': float((away_possession / total_possession) * 100),
                'home_ball_control_time': float(home_possession / 24),  # Assuming 24 fps
                'away_ball_control_time': float(away_possession / 24),
            }
        
        # Calculate formations and average positions with protection
        home_positions, away_positions = self.calculate_team_positions(tracks)
        
        # Convert positions to serializable format
        home_positions_serializable = {str(k): [float(x) for x in v] for k, v in home_positions.items()} if home_positions else {}
        away_positions_serializable = {str(k): [float(x) for x in v] for k, v in away_positions.items()} if away_positions else {}
        
        stats.update({
            'home_formation': self.detect_formation(home_positions),
            'away_formation': self.detect_formation(away_positions),
            'home_avg_player_positions': json.dumps(home_positions_serializable),
            'away_avg_player_positions': json.dumps(away_positions_serializable),
        })
        
        # Improved detection of attack phases with better sensitivity
        home_attack_phases = int(self.detect_attack_phases(tracks, team_id=1)) if tracks.get('players') else 0
        away_attack_phases = int(self.detect_attack_phases(tracks, team_id=2)) if tracks.get('players') else 0
        
        stats.update({
            'home_attack_phases': home_attack_phases,
            'away_attack_phases': away_attack_phases,
        })
        
        # Process player speeds and distances with protection
        # Track all player distances for proper total calculation
        home_speeds, away_speeds = [], []
        home_player_distances = {}  # Track per-player total distance
        away_player_distances = {}  # Track per-player total distance
        
        if tracks.get('players'):
            for frame_num in range(min(total_frames, len(tracks['players']))):
                for player_id, player in tracks['players'][frame_num].items():
                    if 'speed' in player:
                        if player.get('team') == 1:
                            home_speeds.append(float(player['speed']))
                            
                            # Track distance per player
                            if 'distance' in player:
                                if player_id not in home_player_distances:
                                    home_player_distances[player_id] = 0.0
                                
                                # Update with latest distance
                                current_distance = float(player['distance'])
                                if current_distance > home_player_distances[player_id]:
                                    home_player_distances[player_id] = current_distance
                                    
                        elif player.get('team') == 2:
                            away_speeds.append(float(player['speed']))
                            
                            # Track distance per player
                            if 'distance' in player:
                                if player_id not in away_player_distances:
                                    away_player_distances[player_id] = 0.0
                                
                                # Update with latest distance
                                current_distance = float(player['distance'])
                                if current_distance > away_player_distances[player_id]:
                                    away_player_distances[player_id] = current_distance
        
        # Calculate team total distance by summing individual player distances
        home_total_distance = sum(home_player_distances.values())
        away_total_distance = sum(away_player_distances.values())
        
        # Update stats with corrected calculations
        stats.update({
            'home_avg_speed': float(np.mean(home_speeds)) if home_speeds else 0.0,
            'away_avg_speed': float(np.mean(away_speeds)) if away_speeds else 0.0,
            'home_total_distance': home_total_distance,  # Sum of all players' distances
            'away_total_distance': away_total_distance,  # Sum of all players' distances
        })
        
        # Generate heatmaps with protection
        stats.update({
            'home_heatmap': json.dumps(self.generate_heatmap(tracks, team_id=1)) if tracks.get('players') else json.dumps({}),
            'away_heatmap': json.dumps(self.generate_heatmap(tracks, team_id=2)) if tracks.get('players') else json.dumps({}),
        })
        
        # Identify key moments with protection
        key_moments = self.identify_key_moments(tracks, team_ball_control) if tracks.get('players') else []
        stats.update({
            'key_moments': json.dumps(key_moments),
        })
        
        return stats
    
    def calculate_team_positions(self, tracks):
        """Calculate average player positions for formation detection"""
        home_player_positions = {}
        away_player_positions = {}
        
        for frame_num in range(len(tracks['players'])):
            for player_id, player in tracks['players'][frame_num].items():
                # Skip if no transformed position or not a player
                if ('position_transformed' not in player or 
                    not player['position_transformed'] or
                    'team' not in player):
                    continue
                
                # Only include players, not referees
                if player['team'] == 1:  # Home team
                    if player_id not in home_player_positions:
                        home_player_positions[player_id] = []
                    home_player_positions[player_id].append(player['position_transformed'])
                elif player['team'] == 2:  # Away team
                    if player_id not in away_player_positions:
                        away_player_positions[player_id] = []
                    away_player_positions[player_id].append(player['position_transformed'])
        
        # Calculate average positions
        home_avg_positions = {}
        away_avg_positions = {}
        
        for player_id, positions in home_player_positions.items():
            if positions:  # Only if we have some positions
                home_avg_positions[player_id] = np.mean(positions, axis=0)
        
        for player_id, positions in away_player_positions.items():
            if positions:  # Only if we have some positions
                away_avg_positions[player_id] = np.mean(positions, axis=0)
        
        return home_avg_positions, away_avg_positions
    
    def detect_formation(self, player_positions):
        """Detect team formation based on player positions with robust error handling"""
        if not player_positions or len(player_positions) < 2:  # Need at least 2 players
            return "Unknown"
        
        try:
            # Convert positions dict to array for cluster analysis
            positions = np.array(list(player_positions.values()))
            
            # We should have around 11 players per team
            # If we detect too many or too few, set a reasonable limit
            if len(positions) < 5:  # Not enough players detected
                return "Unknown"
            elif len(positions) > 15:  # Too many detections
                positions = positions[:11]  # Take first 11
                
            # Field dimensions
            field_length = 23.32  # from ViewTransformer
            
            # Football field has roughly 3 zones - defense, midfield, attack
            defense_threshold = field_length / 3
            attack_threshold = 2 * field_length / 3
            
            # Sort positions by x (field depth)
            positions = positions[positions[:, 0].argsort()]
            
            # Count players in each zone (exclude goalkeepers)
            outfield_players = min(len(positions) - 1, 10)  # Assume 1 goalkeeper
            
            # Count players in each zone
            n_defense = sum(1 for pos in positions[1:] if pos[0] < defense_threshold)
            n_attack = sum(1 for pos in positions[1:] if pos[0] > attack_threshold)
            n_midfield = outfield_players - n_defense - n_attack
            
            # Make sure the numbers are reasonable
            n_defense = max(2, min(5, n_defense))
            n_midfield = max(2, min(6, n_midfield))
            n_attack = max(1, min(4, n_attack))
            
            # Adjust to total 10 outfield players
            while n_defense + n_midfield + n_attack > 10:
                if n_midfield > 3:
                    n_midfield -= 1
                elif n_defense > 3:
                    n_defense -= 1
                elif n_attack > 1:
                    n_attack -= 1
            
            while n_defense + n_midfield + n_attack < 10:
                if n_midfield < 5:
                    n_midfield += 1
                elif n_defense < 4:
                    n_defense += 1
                else:
                    n_attack += 1
            
            # Return formation in the correct order: defense-midfield-attack
            return f"{n_defense}-{n_midfield}-{n_attack}"
        except Exception as e:
            print(f"Error detecting formation: {str(e)}")
            return "Unknown"

    
    def detect_attack_phases(self, tracks, team_id):
        """Detect number of attack phases for a team with improved accuracy"""
        attack_phases = 0
        in_attack_phase = False
        
        field_length = 23.32  # from ViewTransformer
        attack_threshold = 2 * field_length / 3
        
        # Keep track of continuous possession frames for more robust detection
        possession_frames = 0
        min_possession_frames = 8  # Minimum frames for a valid attack phase (about 1/3 second at 24fps)
        
        for frame_num in range(len(tracks['players'])):
            # Check for ball possession by this team
            team_has_ball = False
            team_in_attack_zone = False
            
            for player_id, player in tracks['players'][frame_num].items():
                if player.get('team') == team_id:
                    # Check if this player has the ball
                    if player.get('has_ball', False):
                        team_has_ball = True
                        
                        # Check if in attacking third
                        position = player.get('position_transformed')
                        if position and position[0] > attack_threshold:
                            team_in_attack_zone = True
            
            # If team has ball in attack zone, count for potential attack phase
            if team_has_ball and team_in_attack_zone:
                possession_frames += 1
                
                # If not already in attack phase and we've had sufficient frames, start new phase
                if not in_attack_phase and possession_frames >= min_possession_frames:
                    in_attack_phase = True
                    attack_phases += 1
            else:
                # Reset counter if possession lost or not in attack zone
                possession_frames = 0
                in_attack_phase = False
        
        return attack_phases
    
    def generate_heatmap(self, tracks, team_id):
        """Generate a heatmap of player positions for a team"""
        heatmap = {}
        
        for frame_num in range(len(tracks['players'])):
            for player_id, player in tracks['players'][frame_num].items():
                if player.get('team') == team_id and 'position_transformed' in player and player['position_transformed']:
                    pos = tuple(float(round(x, 1)) for x in player['position_transformed'])
                    pos_key = f"{pos[0]},{pos[1]}"
                    heatmap[pos_key] = heatmap.get(pos_key, 0) + 1
        
        return heatmap
    
    def identify_key_moments(self, tracks, team_ball_control):
        """Identify key moments in the match"""
        key_moments = []
        
        # Detect possession changes
        for i in range(1, len(team_ball_control)):
            if team_ball_control[i] != team_ball_control[i-1]:
                key_moments.append({
                    'frame': int(i),
                    'type': 'possession_change',
                    'from_team': int(team_ball_control[i-1]),
                    'to_team': int(team_ball_control[i])
                })
        
        # Detect high speed moments
        for frame_num in range(len(tracks['players'])):
            for player_id, player in tracks['players'][frame_num].items():
                if 'speed' in player and player['speed'] > 25:  # 25 km/h threshold
                    key_moments.append({
                        'frame': int(frame_num),
                        'type': 'high_speed',
                        'player_id': int(player_id),
                        'team': int(player.get('team', 0)),
                        'speed': float(player['speed'])
                    })
        
        return key_moments
    
    def get_analysis_by_id(self, analysis_id):
        """Get match analysis by ID"""
        return self.session.query(MatchAnalysis).filter_by(id=analysis_id).first()