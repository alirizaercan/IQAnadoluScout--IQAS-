import os
from flask import Blueprint, request, jsonify, current_app
from services.performance_service import PerformanceService
from utils.database import Database
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import Patch, Circle, Rectangle
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec

performance_bp = Blueprint('performance', __name__)
db = Database()

@performance_bp.route('/leagues', methods=['GET'])
def get_leagues():
    """Get all leagues."""
    print("GET request received at /api/physical-development/leagues")  # Debugging line
    session = db.connect()
    try:
        service = PerformanceService(session)
        leagues = service.get_all_leagues()
        if not leagues:
            return jsonify({'message': 'No leagues found'}), 404  # Return a clear message if no leagues found
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@performance_bp.route('/teams/<league_id>', methods=['GET'])
def get_teams(league_id):
    """Get teams by league_id."""
    session = db.connect()
    try:
        service = PerformanceService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@performance_bp.route('/footballers/<team_id>', methods=['GET'])
def get_footballers(team_id):
    """Get footballers by team_id."""
    session = db.connect()
    try:
        service = PerformanceService(session)
        footballers = service.get_footballers_by_team(team_id)
        return jsonify(footballers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)
        
@performance_bp.route('/performance-data', methods=['POST'])
def get_performance_data():
    """Get performance data for a footballer."""
    session = db.connect()
    data = request.json
    try:
        footballer_id = data.get('footballer_id')
        graph_type = data.get('graph_type')
        service = PerformanceService(session)
        graph_data = service.get_footballer_performance_data(footballer_id, graph_type)
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@performance_bp.route('/generate-graph', methods=['POST'])
def generate_performance_graph():
    """Generate graph based on selected type."""
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import os
    
    data = request.json
    graph_type = data.get('graph_type')
    footballer_id = data.get('footballer_id')
    
    session = db.connect()
    
    try:
        service = PerformanceService(session)
        performance_data = service.get_footballer_performance_data(footballer_id, graph_type)
        
        if not performance_data:
            return jsonify({'error': 'No data available for the selected criteria'}), 404
        
        # Set professional styling
        plt.style.use('ggplot')
        team_color = '#E30A17'  # Turkish red color as default
        secondary_color = '#FFFFFF'
        
        # Process the data - handle single-row data
        performance_data = performance_data[0] if len(performance_data) == 1 else performance_data
        
        # Standardize figure size for all graphs
        fig_width = 8
        fig_height = 6
        
        if graph_type == "Goals and Assists Analysis":
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            # Check if we have single row or multiple rows
            if isinstance(performance_data, dict):
                # Single footballer data
                labels = ['Goals', 'Assists']
                values = [performance_data.get('goals', 0), performance_data.get('assists', 0)]
                
                # Create a modern color scheme
                modern_colors = ['#1A535C', '#4ECDC4']
                
                # Create more modern bar chart with gradient effect
                bars = ax.bar(
                    labels, 
                    values, 
                    color=modern_colors, 
                    alpha=0.9, 
                    width=0.6,
                    edgecolor='white',
                    linewidth=1
                )
                
                # Add value labels with better styling
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2., 
                        height + 0.1,
                        f'{height:.1f}', 
                        ha='center', 
                        va='bottom', 
                        fontweight='bold',
                        fontsize=10
                    )
                
                # Calculate contribution ratio
                total = sum(values)
                if total > 0:
                    goal_ratio = values[0] / total * 100
                    assist_ratio = values[1] / total * 100
                    
                    # Add contribution percentages
                    ax.text(
                        0, 
                        values[0]/2, 
                        f"{goal_ratio:.1f}%", 
                        ha='center', 
                        va='center', 
                        color='white', 
                        fontweight='bold'
                    )
                    ax.text(
                        1, 
                        values[1]/2, 
                        f"{assist_ratio:.1f}%", 
                        ha='center', 
                        va='center', 
                        color='white', 
                        fontweight='bold'
                    )
                
                # Set a good y-limit
                max_val = max(values) if max(values) > 0 else 1
                ax.set_ylim(0, max_val * 1.3)
                
                # Professional title styling
                plt.title(
                    "Goals and Assists Analysis", 
                    fontsize=14, 
                    fontweight='bold',
                    pad=15
                )
                
                # Add a subtle annotation about total contribution
                ax.annotate(
                    f"Total Contribution: {total:.0f}",
                    xy=(0.5, 0.95),
                    xycoords='axes fraction',
                    ha='center',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc='#F7F7F7', ec="black", alpha=0.7)
                )
                
                # Add horizontal grid lines with better styling
                ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#888888')
                ax.set_axisbelow(True)
                
                # Remove top and right spines for cleaner look
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#CCCCCC')
                ax.spines['left'].set_color('#CCCCCC')
                
                # Add subtle labels
                ax.set_ylabel("Count", fontsize=10, color='#555555')
            else:
                # This should handle multiple matches data if available
                pass
                
        elif graph_type == "Shooting Accuracy Analysis":
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Create data for pie chart
                shots = performance_data.get('shots_per_game', 0)
                on_target = performance_data.get('shots_on_target_per_game', 0)
                
                # Ensure we don't divide by zero
                if shots > 0:
                    on_target_pct = (on_target / shots) * 100
                    off_target_pct = 100 - on_target_pct
                    
                    # Use more professional color scheme
                    colors = ['#2C8C99', '#42464B']  # Professional blue for on target, gray for off target
                    
                    # Create pie chart for shot accuracy with modern styling
                    labels = [f'On Target', f'Off Target']
                    sizes = [on_target_pct, off_target_pct]
                    explode = (0.1, 0)  # Explode on target slice
                    
                    # Create pie chart with subtle shadow and better styling
                    wedges, texts, autotexts = ax.pie(
                        sizes, 
                        explode=explode, 
                        labels=labels, 
                        autopct='%1.1f%%', 
                        colors=colors,
                        shadow=True, 
                        startangle=90, 
                        textprops={'fontsize': 11},
                        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
                    )
                    
                    # Style the percentage text
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(10)
                    
                    # Style the labels
                    for text in texts:
                        text.set_fontweight('bold')
                    
                    # Add informative, well-positioned title and subtitle
                    plt.title(
                        "Shooting Accuracy Analysis", 
                        fontsize=14, 
                        fontweight='bold',
                        pad=15
                    )
                    
                    # Add shooting stats in an annotation box
                    ax.annotate(
                        f"Total Shots Per Game: {shots:.1f}\nOn Target Per Game: {on_target:.1f}",
                        xy=(0.5, -0.1),
                        xycoords='axes fraction',
                        ha='center',
                        fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", fc='#F7F7F7', ec="gray", alpha=0.7)
                    )
                    
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                else:
                    # No shots data
                    ax.text(0.5, 0.5, "No shooting data available", ha='center', fontsize=12, fontweight='bold')
                    ax.axis('off')
                    
        elif graph_type == "Defensive Performance Analysis":
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Get defensive stats
                tackles = performance_data.get('tackles_per_game', 0)
                interceptions = performance_data.get('interceptions_per_game', 0)
                clearances = performance_data.get('clearances_per_game', 0)
                
                # Create radar chart with better styling
                categories = ['Tackles', 'Interceptions', 'Clearances']
                values = [tackles, interceptions, clearances]
                
                # Calculate angles for each category
                N = len(categories)
                angles = [n / float(N) * 2 * np.pi for n in range(N)]
                angles += angles[:1]  # Close the loop
                
                # Add the values (repeat first value to close the loop)
                values += values[:1]
                
                # Draw the plot with improved styling
                ax = plt.subplot(111, polar=True)
                
                # Plot data
                ax.fill(angles, values, '#3A86FF', alpha=0.25)
                ax.plot(angles, values, color='#3A86FF', linewidth=2.5, marker='o', markersize=8)
                
                # Add value annotations with better styling
                for i, val in enumerate(values[:-1]):  # Skip the last duplicate value
                    angle = angles[i]
                    ax.annotate(
                        f"{val:.1f}", 
                        xy=(angle, val), 
                        xytext=(angle, val + 0.5),
                        fontweight='bold', 
                        ha='center',
                        fontsize=10,
                        color='#333333',
                        bbox=dict(boxstyle="round,pad=0.2", fc='white', ec="gray", alpha=0.7)
                    )
                
                # Set radar chart background styling
                ax.set_facecolor('#F7F7F7')
                
                # Create concentric circles with subtle styling
                ax.grid(True, color='gray', alpha=0.3, linestyle='--')
                
                # Set category labels with better styling
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(
                    categories, 
                    fontsize=11, 
                    fontweight='bold',
                    color='#333333'
                )
                
                # Set y-ticks to be invisible but keep grid
                ax.set_yticks([])
                
                # Make y-axis values larger to fit annotations
                max_val = max(values)
                ax.set_ylim(0, max_val * 1.3)
                
                # Add professional title
                plt.title(
                    "Defensive Performance Analysis", 
                    fontsize=14, 
                    fontweight='bold',
                    pad=15,
                    y=1.1
                )
                
                # Add defensive stats summary
                plt.figtext(
                    0.5, 
                    0.01, 
                    f"Total Defensive Actions Per Game: {sum(values[:-1]):.1f}",
                    ha='center',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc='#F7F7F7', ec="gray", alpha=0.7)
                )
                
        elif graph_type == "Passing Accuracy Analysis":
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Get passing stats
                total_passes = performance_data.get('accurate_per_game', 0)
                long_balls = performance_data.get('acc_long_balls', 0)
                crosses = performance_data.get('acc_crosses', 0)
                
                # Create stacked bar for passing composition with modern colors
                labels = ['Passing Composition']
                short_passes = total_passes - (long_balls + crosses)
                
                # Ensure no negative values
                short_passes = max(0, short_passes)
                
                # Use a professional color palette
                modern_colors = ['#4D908E', '#277DA1', '#577590']
                
                # Create the stacked bar with better styling
                ax.bar(
                    labels, 
                    short_passes, 
                    label='Short/Medium Passes', 
                    color=modern_colors[0],
                    edgecolor='white',
                    linewidth=0.5
                )
                ax.bar(
                    labels, 
                    long_balls, 
                    bottom=short_passes, 
                    label='Long Balls', 
                    color=modern_colors[1],
                    edgecolor='white',
                    linewidth=0.5
                )
                ax.bar(
                    labels, 
                    crosses, 
                    bottom=short_passes+long_balls, 
                    label='Crosses', 
                    color=modern_colors[2],
                    edgecolor='white',
                    linewidth=0.5
                )
                
                # Add total passes text with better styling
                ax.text(
                    0, 
                    total_passes + 1, 
                    f"Total: {total_passes:.1f}", 
                    ha='center', 
                    va='bottom', 
                    fontweight='bold', 
                    fontsize=11,
                    bbox=dict(boxstyle="round,pad=0.2", fc='white', ec="gray", alpha=0.8)
                )
                
                # Add percentages inside or next to each segment with better styling
                if total_passes > 0:
                    short_pct = (short_passes / total_passes) * 100
                    long_pct = (long_balls / total_passes) * 100
                    cross_pct = (crosses / total_passes) * 100
                    
                    # Only show percentage text if the segment is big enough
                    if short_passes > total_passes * 0.05:
                        ax.text(
                            0, 
                            short_passes/2, 
                            f"{short_pct:.1f}%", 
                            ha='center', 
                            va='center', 
                            color='white', 
                            fontweight='bold',
                            fontsize=10
                        )
                    
                    if long_balls > total_passes * 0.05:
                        ax.text(
                            0, 
                            short_passes + long_balls/2, 
                            f"{long_pct:.1f}%", 
                            ha='center', 
                            va='center', 
                            color='white', 
                            fontweight='bold',
                            fontsize=10
                        )
                    
                    if crosses > total_passes * 0.05:
                        ax.text(
                            0, 
                            short_passes + long_balls + crosses/2, 
                            f"{cross_pct:.1f}%", 
                            ha='center', 
                            va='center', 
                            color='white', 
                            fontweight='bold',
                            fontsize=10
                        )
                
                # Add a professional title with padding
                plt.title(
                    "Passing Composition Analysis", 
                    fontsize=14, 
                    fontweight='bold',
                    pad=15
                )
                
                # Add professional axis labels
                plt.ylabel(
                    "Number of Passes Per Game", 
                    fontsize=11,
                    color='#555555'
                )
                
                # Set limits with room for annotations
                ax.set_ylim(0, total_passes * 1.25)
                
                # Add a professionally styled legend
                legend = plt.legend(
                    loc='upper right', 
                    fontsize=9,
                    framealpha=0.9,
                    edgecolor='#CCCCCC'
                )
                
                # Remove top and right spines for cleaner look
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#CCCCCC')
                ax.spines['left'].set_color('#CCCCCC')
                
                # Add horizontal grid lines with better styling
                ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#CCCCCC')
                ax.set_axisbelow(True)
                
        elif graph_type == "Dribbling Success Analysis":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height), gridspec_kw={'width_ratios': [1.5, 1]})
            
            if isinstance(performance_data, dict):
                # Extract data
                succ_dribbles = performance_data.get('succ_dribbles', 0)
                dribbled_past = performance_data.get('dribbled_past_per_game', 0)
                matches_played = performance_data.get('total_played', 0)
                possession_lost = performance_data.get('possession_lost', 0)
                possession_won_final_third = performance_data.get('possession_won_final_third', 0)
                
                # Left chart: Dribbling comparison
                labels = ['Successful\nDribbles', 'Times\nDribbled Past']
                values = [succ_dribbles, dribbled_past]
                
                # Create a more professional color palette
                success_color = '#4CAF50'  # Professional green
                negative_color = '#F44336'  # Professional red
                
                # Create bars with gradient effect
                bars = ax1.bar(
                    labels, 
                    values, 
                    color=[success_color, negative_color],
                    edgecolor='black',
                    linewidth=0.5,
                    width=0.6
                )
                
                # Add data labels with professional styling
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + max(values) * 0.02,
                        f'{height:.1f}',
                        ha='center',
                        va='bottom',
                        fontsize=10,
                        fontweight='bold'
                    )
                
                # Calculate dribbling metrics
                if matches_played > 0:
                    dribbles_per_match = succ_dribbles / matches_played if matches_played > 0 else 0
                    
                    # Add dribbling frequency text
                    ax1.text(
                        0, 
                        max(values) * 1.15,
                        f"Dribbles per match: {dribbles_per_match:.2f}",
                        ha='center',
                        fontsize=9,
                        fontstyle='italic'
                    )
                
                # Calculate net dribbling index
                dribbling_index = succ_dribbles - dribbled_past
                score_color = success_color if dribbling_index >= 0 else negative_color
                
                # Add net dribbling score with professional styling
                ax1.text(
                    0.5, 
                    max(values) * 1.25,
                    f"Dribbling Index: {dribbling_index:+.1f}",
                    ha='center',
                    fontsize=11,
                    fontweight='bold',
                    color=score_color,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor=score_color, boxstyle='round,pad=0.5')
                )
                
                # Configure first chart professionally
                ax1.set_title("Dribbling Metrics", fontsize=12, fontweight='bold')
                ax1.set_ylim(0, max(values) * 1.35)  # Allow room for labels and metrics
                ax1.yaxis.grid(True, linestyle='--', alpha=0.3)
                ax1.set_axisbelow(True)
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                
                # Right chart: Possession efficiency gauge
                ax2.clear()
                ax2.axis('off')
                
                # Create possession efficiency visual
                # Preparing data for a gauge-style visualization
                if possession_lost > 0 or possession_won_final_third > 0:
                    # Calculate possession efficiency ratio
                    total_possession_actions = possession_lost + possession_won_final_third
                    efficiency_pct = (possession_won_final_third / total_possession_actions * 100) if total_possession_actions > 0 else 0
                    
                    import numpy as np
                    
                    # Create a semicircular gauge
                    theta = np.linspace(-np.pi, 0, 100)  # Semicircle
                    r = 0.8
                    
                    # Draw gauge background
                    ax2.plot(r*np.cos(theta), r*np.sin(theta), color='lightgray', linewidth=8)
                    
                    # Draw gauge indicator based on efficiency percentage
                    if efficiency_pct > 0:
                        efficiency_radians = -np.pi + (efficiency_pct / 100 * np.pi)
                        theta_efficiency = np.linspace(-np.pi, efficiency_radians, 100)
                        
                        # Dynamic color based on efficiency
                        if efficiency_pct < 33:
                            gauge_color = negative_color
                        elif efficiency_pct < 66:
                            gauge_color = '#FFC107'  # Amber
                        else:
                            gauge_color = success_color
                            
                        ax2.plot(r*np.cos(theta_efficiency), r*np.sin(theta_efficiency), color=gauge_color, linewidth=8)
                    
                    # Add central metrics
                    ax2.text(0, -0.2, f"{efficiency_pct:.1f}%", ha='center', va='center', fontsize=16, fontweight='bold')
                    ax2.text(0, -0.4, "Possession\nEfficiency", ha='center', va='center', fontsize=10)
                    
                    # Add possession metrics
                    ax2.text(-0.7, -0.6, f"Lost: {possession_lost:.0f}", ha='left', va='center', fontsize=9, color=negative_color)
                    ax2.text(0.7, -0.6, f"Won: {possession_won_final_third:.0f}", ha='right', va='center', fontsize=9, color=success_color)
                    
                    # Configure gauge chart boundaries
                    ax2.set_xlim(-1, 1)
                    ax2.set_ylim(-1, 0.2)
                    
                    # Add title
                    ax2.set_title("Possession Efficiency", fontsize=12, fontweight='bold')
                else:
                    # No possession data
                    ax2.text(0, 0, "No possession\ndata available", ha='center', va='center', fontweight='bold')
                
                # Professional title for the whole figure
                plt.suptitle("Dribbling & Possession Analysis", fontsize=14, fontweight='bold', y=0.98)
                
                # Professional layout adjustments
                plt.subplots_adjust(wspace=0.3)
                fig.patch.set_facecolor('white')
                
        elif graph_type == "Playing Time Analysis":
            # Create a figure with appropriate dimensions
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Extract data
                total_played = performance_data.get('total_played', 0)
                started = performance_data.get('started', 0)
                sub_appearances = total_played - started if total_played >= started else 0
                minutes_per_game = performance_data.get('minutes_per_game', 0)
                total_minutes = performance_data.get('total_minutes_played', 0)
                
                # First chart: Appearances breakdown (starts vs sub)
                if total_played > 0:
                    # First chart: Starts vs Substitute appearances
                    appearance_labels = ['Started', 'As Substitute']
                    appearance_values = [started, sub_appearances]
                    colors = [team_color, 'lightskyblue']
                    
                    ax1.bar(appearance_labels, appearance_values, color=colors, width=0.6)
                    
                    # Add data labels
                    for i, v in enumerate(appearance_values):
                        ax1.text(i, v + 0.1, f"{v:.0f}", ha='center', fontweight='bold')
                        
                    # Add appearance percentage on started matches
                    start_percentage = (started / total_played * 100) if total_played > 0 else 0
                    ax1.text(0, appearance_values[0]/2, f"{start_percentage:.1f}%", 
                            ha='center', va='center', fontweight='bold', color='white')
                    
                    # Configure first chart
                    ax1.set_title("Appearance Distribution", fontsize=12, fontweight='bold')
                    ax1.set_ylim(0, max(appearance_values) * 1.2)
                    ax1.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    # Second chart: Minutes distribution (90-minute equivalent)
                    full_matches = total_minutes / 90 if total_minutes else 0
                    ax2.clear()
                    
                    # Create a gauge-like visualization for minutes played
                    import numpy as np
                    theta = np.linspace(0, 2*np.pi, 100)
                    r = 0.8  # Radius of circle
                    
                    # Draw circle
                    ax2.plot(r*np.cos(theta), r*np.sin(theta), color='lightgray', linewidth=4)
                    
                    # Calculate minutes as percentage of maximum possible (assuming all games are starts and full 90 min)
                    max_possible_minutes = total_played * 90
                    minutes_percentage = min(1.0, total_minutes / max_possible_minutes) if max_possible_minutes > 0 else 0
                    
                    # Draw filled arc for minutes played percentage
                    if minutes_percentage > 0:
                        theta_fill = np.linspace(0, minutes_percentage * 2*np.pi, 100)
                        ax2.plot(r*np.cos(theta_fill), r*np.sin(theta_fill), color=team_color, linewidth=8)
                    
                    # Add text in center
                    ax2.text(0, 0.2, f"{total_minutes:.0f}", ha='center', va='center', fontsize=18, fontweight='bold')
                    ax2.text(0, 0, "Minutes", ha='center', va='center', fontsize=10)
                    ax2.text(0, -0.2, f"({full_matches:.1f} full matches)", ha='center', va='center', fontsize=10)
                    
                    # Add minutes per game below
                    ax2.text(0, -0.5, f"Avg: {minutes_per_game:.1f} min/game", ha='center', fontsize=11, fontweight='bold')
                    
                    # Configure second chart
                    ax2.set_title("Minutes Played", fontsize=12, fontweight='bold')
                    ax2.set_xlim(-1, 1)
                    ax2.set_ylim(-1, 1)
                    ax2.axis('off')  # Hide axis for cleaner look
                else:
                    # No data available
                    ax1.text(0.5, 0.5, "No appearance\ndata available", 
                            ha='center', va='center', fontweight='bold', transform=ax1.transAxes)
                    ax1.axis('off')
                    
                    ax2.text(0.5, 0.5, "No minutes played\ndata available", 
                            ha='center', va='center', fontweight='bold', transform=ax2.transAxes)
                    ax2.axis('off')
                
                # Main title
                plt.suptitle("Playing Time Analysis", fontsize=14, fontweight='bold', y=0.98)
                
                # Adjust layout
                plt.subplots_adjust(wspace=0.3)
                fig.patch.set_facecolor('white')
                
        elif graph_type == "Physical Duels Analysis":
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Get duels stats
                total_duels = performance_data.get('total_duels_won', 0)
                ground_duels = performance_data.get('ground_duels_won', 0)
                aerial_duels = performance_data.get('aerial_duels_won', 0)
                
                # Use a professional color palette
                modern_colors = ['#2a9d8f', '#264653', '#e9c46a']
                
                # Create horizontal bar chart with better styling
                categories = ['Ground Duels', 'Aerial Duels', 'Total Duels']
                values = [ground_duels, aerial_duels, total_duels]
                
                # Create horizontal bars with custom colors and styling
                bars = ax.barh(
                    categories, 
                    values, 
                    color=modern_colors,
                    alpha=0.9, 
                    height=0.5,
                    edgecolor='white',
                    linewidth=1
                )
                
                # Add value labels with improved styling
                for bar in bars:
                    width = bar.get_width()
                    ax.text(
                        width + 0.1, 
                        bar.get_y() + bar.get_height()/2, 
                        f'{width:.1f}', 
                        va='center', 
                        fontweight='bold',
                        fontsize=10,
                        color='#333333'
                    )
                
                # Add duels won percentage if we have data
                if total_duels > 0:
                    ground_pct = (ground_duels / total_duels) * 100
                    aerial_pct = (aerial_duels / total_duels) * 100
                    
                    # Add percentage annotations on bars
                    ax.text(
                        ground_duels / 2, 
                        0, 
                        f"{ground_pct:.1f}%", 
                        va='center', 
                        ha='center',
                        fontweight='bold',
                        color='white',
                        fontsize=9
                    )
                    
                    ax.text(
                        aerial_duels / 2, 
                        1, 
                        f"{aerial_pct:.1f}%", 
                        va='center', 
                        ha='center',
                        fontweight='bold',
                        color='white',
                        fontsize=9
                    )
                
                # Add professional title
                plt.title(
                    "Physical Duels Analysis", 
                    fontsize=14, 
                    fontweight='bold',
                    pad=15
                )
                
                # Add professional x-axis label
                ax.set_xlabel(
                    "Duels Won Per Game", 
                    fontsize=10, 
                    labelpad=10,
                    color='#555555'
                )
                
                # Set appropriate x-axis limits with room for labels
                ax.set_xlim(0, max(values) * 1.15)
                
                # Add subtle summary annotation
                duels_total = ground_duels + aerial_duels
                if duels_total > 0:
                    ax.annotate(
                        f"Ground/Aerial Ratio: {ground_duels/aerial_duels:.2f}" if aerial_duels > 0 else "No aerial duels won",
                        xy=(0.5, -0.15),
                        xycoords='axes fraction',
                        ha='center',
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.2", fc='#F7F7F7', ec="gray", alpha=0.7)
                    )
                
                # Add horizontal grid lines with better styling
                ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#CCCCCC')
                ax.set_axisbelow(True)
                
                # Remove top and right spines for cleaner look
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#CCCCCC')
                ax.spines['left'].set_color('#CCCCCC')
                
        elif graph_type == "Error Analysis":
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Get error stats
                errors_shot = performance_data.get('errors_leading_to_shot', 0)
                errors_goal = performance_data.get('errors_leading_to_goal', 0)
                
                # Use professional color gradient
                colors = ['#ff7b00', '#dc2f02']  # Orange to deep red gradient
                
                # Create bar chart with improved styling
                labels = ['Errors Leading\nto Shot', 'Errors Leading\nto Goal']
                values = [errors_shot, errors_goal]
                
                # Improved bar styling
                bars = ax.bar(
                    labels, 
                    values, 
                    color=colors,
                    alpha=0.8, 
                    width=0.6,
                    edgecolor='white',
                    linewidth=1
                )
                
                # Add value labels on top of bars with better styling
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2., 
                        height + 0.05,
                        f'{height:.0f}', 
                        ha='center', 
                        va='bottom', 
                        fontweight='bold',
                        fontsize=10
                    )
                
                # Calculate error severity if there are errors
                if errors_shot > 0 or errors_goal > 0:
                    conversion_rate = (errors_goal / errors_shot * 100) if errors_shot > 0 else 0
                    
                    # Add severity annotation
                    ax.annotate(
                        f"Conversion Rate: {conversion_rate:.1f}%" if errors_shot > 0 else "N/A",
                        xy=(0.5, 0.9),
                        xycoords='axes fraction',
                        ha='center',
                        fontsize=10,
                        bbox=dict(boxstyle="round,pad=0.3", fc='#F7F7F7', ec="gray", alpha=0.7)
                    )
                
                # Set a good y-limit - always show at least up to 1
                max_val = max(values) if max(values) > 0 else 1
                ax.set_ylim(0, max_val + 0.5)
                
                # Add professional title
                plt.title(
                    "Error Analysis", 
                    fontsize=14, 
                    fontweight='bold',
                    pad=15
                )
                
                # Add y-axis label
                ax.set_ylabel(
                    "Number of Errors", 
                    fontsize=10,
                    color='#555555'
                )
                
                # Add horizontal grid lines with better styling
                ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#CCCCCC')
                ax.set_axisbelow(True)
                
                # Remove top and right spines for cleaner look
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_color('#CCCCCC')
                ax.spines['left'].set_color('#CCCCCC')
        
        elif graph_type == "Disciplinary Analysis":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height))
            
            if isinstance(performance_data, dict):
                # Get disciplinary stats
                yellow_cards = performance_data.get('yellow', 0)
                yellow_red_cards = performance_data.get('yellow_red', 0)
                straight_red_cards = performance_data.get('red_cards', 0) - yellow_red_cards
                total_red = performance_data.get('red_cards', 0)
                fouls = performance_data.get('fouls', 0)
                was_fouled = performance_data.get('was_fouled', 0)
                matches_played = performance_data.get('total_played', 0)
                
                # Left chart: Card visualization
                # Create a more professional stacked bar chart for cards
                card_types = ['Yellow', 'Second Yellow', 'Straight Red']
                card_values = [yellow_cards, yellow_red_cards, straight_red_cards]
                card_colors = ['#FFC107', '#FF9800', '#F44336']  # Professional color scheme
                
                # Create bars with professional styling
                bars = ax1.bar(
                    card_types, 
                    card_values, 
                    color=card_colors,
                    edgecolor='black',
                    linewidth=0.5,
                    width=0.7
                )
                
                # Add data labels on bars
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax1.text(
                            bar.get_x() + bar.get_width()/2.,
                            height - 0.15 if height > 0.5 else height + 0.1,
                            f'{int(height)}',
                            ha='center',
                            va='center',
                            fontsize=10,
                            fontweight='bold',
                            color='white' if height > 0.5 else 'black'
                        )
                
                # Calculate cards per match ratio
                if matches_played > 0:
                    cards_per_match = (yellow_cards + total_red) / matches_played
                    ax1.text(
                        1, 
                        max(card_values) * 1.1,
                        f"{cards_per_match:.2f} cards/match",
                        ha='center',
                        fontsize=9,
                        fontstyle='italic'
                    )
                
                # Configure first chart
                ax1.set_title("Card Distribution", fontsize=12, fontweight='bold')
                ax1.set_ylim(0, max(max(card_values) * 1.2, 1))  # Ensure space for labels
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.set_axisbelow(True)
                ax1.grid(axis='y', linestyle='--', alpha=0.3)
                
                # Right chart: Fouls comparison
                if fouls > 0 or was_fouled > 0:
                    # Create horizontal bars for fouls committed vs suffered
                    foul_labels = ['Committed', 'Suffered']
                    foul_values = [fouls, was_fouled]
                    foul_colors = ['#E57373', '#81C784']  # Red for committed, green for suffered
                    
                    # Horizontal bars for better readability
                    bars = ax2.barh(
                        foul_labels, 
                        foul_values, 
                        color=foul_colors,
                        edgecolor='black',
                        linewidth=0.5,
                        height=0.5
                    )
                    
                    # Add data labels
                    for bar in bars:
                        width = bar.get_width()
                        ax2.text(
                            width + 0.3,
                            bar.get_y() + bar.get_height()/2,
                            f'{int(width)}',
                            va='center',
                            fontsize=10,
                            fontweight='bold'
                        )
                    
                    # Calculate foul ratio
                    if was_fouled > 0:
                        foul_ratio = fouls / was_fouled
                        ax2.text(
                            max(foul_values) * 0.5,
                            -0.5,
                            f"Foul Ratio: {foul_ratio:.2f}",
                            ha='center',
                            fontsize=9,
                            fontstyle='italic'
                        )
                    
                    # Calculate fouls per match
                    if matches_played > 0:
                        fouls_per_match = fouls / matches_played
                        ax2.text(
                            max(foul_values) * 0.5,
                            -0.8,
                            f"{fouls_per_match:.2f} fouls/match",
                            ha='center',
                            fontsize=9,
                            fontstyle='italic'
                        )
                        
                    # Configure second chart
                    ax2.set_title("Fouls Analysis", fontsize=12, fontweight='bold')
                    ax2.set_xlim(0, max(foul_values) * 1.1)
                    ax2.spines['top'].set_visible(False)
                    ax2.spines['right'].set_visible(False)
                    ax2.set_axisbelow(True)
                    ax2.grid(axis='x', linestyle='--', alpha=0.3)
                else:
                    # No fouls data
                    ax2.text(0.5, 0.5, "No fouls data available", 
                            ha='center', va='center', fontweight='bold', transform=ax2.transAxes)
                    ax2.axis('off')
                
                # Add a professional title for the whole figure
                plt.suptitle("Disciplinary Analysis", fontsize=14, fontweight='bold', y=0.98)
                
                # Professional layout adjustments
                plt.subplots_adjust(wspace=0.3, bottom=0.15)
                fig.patch.set_facecolor('white')

                
        elif graph_type == "Overall Performance Radar Analysis":
            # Create radar chart with key performance metrics
            if isinstance(performance_data, dict):
                fig = plt.figure(figsize=(fig_width, fig_height))
                
                # Define metrics with better names
                metrics = [
                    ('Goals per Game', performance_data.get('goals_per_game', 0)),
                    ('Assists', performance_data.get('assists', 0)),
                    ('Tackles per Game', performance_data.get('tackles_per_game', 0)),
                    ('Passing Accuracy', performance_data.get('accurate_per_game', 0)),
                    ('Interceptions per Game', performance_data.get('interceptions_per_game', 0))
                ]
                
                # Normalize values for radar chart (scale from 0 to 1)
                categories = [m[0] for m in metrics]
                max_vals = {
                    'Goals per Game': 1.0,  # One goal per game is exceptional
                    'Assists': 10.0,  # 10 assists in a season is good
                    'Tackles per Game': 4.0,  # 4 tackles per game is solid
                    'Passing Accuracy': 60.0,  # 60 accurate passes per game is good
                    'Interceptions per Game': 3.0  # 3 interceptions per game is good
                }
            
                values = [min(1.0, m[1] / max_vals[m[0]]) for m in metrics]  # Normalize to 0-1 scale
                raw_values = [m[1] for m in metrics]  # Original values for display
                
                # Calculate angles for each metric before closing the polygon
                angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
                
                # Repeat first value to close the polygon
                categories = np.append(categories, categories[0])
                values = np.append(values, values[0])
                raw_values = np.append(raw_values, raw_values[0])
                angles = np.append(angles, angles[0])
                
                # Set up radar chart with improved styling
                ax = fig.add_subplot(111, polar=True)
                
                # Create a custom colormap for a professional look
                cmap = plt.cm.get_cmap('viridis')
                radar_color = cmap(0.7)
                
                # Draw the radar chart with professional styling
                ax.plot(angles, values, 'o-', linewidth=2.5, color=radar_color, markersize=8)
                ax.fill(angles, values, color=radar_color, alpha=0.25)
                
                # Add raw value annotations with improved styling
                for i, value in enumerate(raw_values[:-1]):
                    angle = angles[i]
                    # Position the text slightly outside the data point
                    ax.annotate(
                        f"{value:.1f}", 
                        xy=(angle, values[i]),
                        xytext=(angle, values[i] + 0.1 if values[i] < 0.7 else values[i] - 0.1), 
                        fontweight='bold',
                        fontsize=10,
                        color='#333333',
                        bbox=dict(boxstyle="round,pad=0.2", fc='white', ec="gray", alpha=0.8)
                    )
                
                # Set category labels with better styling
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(
                    categories[:-1], 
                    fontsize=10, 
                    fontweight='bold',
                    color='#333333'
                )
                
                # Remove radial labels but keep the grid for reference
                ax.set_yticklabels([])
                
                # Set grid styling for a clean look
                ax.set_rticks([0.2, 0.4, 0.6, 0.8, 1.0])
                ax.grid(True, color='gray', alpha=0.3, linestyle='--')
                
                # Add title with professional styling
                plt.title(
                    "Overall Performance Analysis", 
                    fontsize=14, 
                    fontweight='bold', 
                    pad=20
                )
                
                # Add a small legend explaining the scale
                plt.figtext(
                    0.5, 
                    0.02, 
                    "Scale: Values normalized to professional standards",
                    ha='center',
                    fontsize=8,
                    fontstyle='italic'
                )
                
                # Calculate and display overall rating
                avg_performance = np.mean(values[:-1])  # Exclude the duplicate last value
                performance_text = f"Overall Rating: {avg_performance*10:.1f}/10"
                
                plt.figtext(
                    0.5, 
                    0.06, 
                    performance_text,
                    ha='center',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", fc='#F7F7F7', ec="gray", alpha=0.8)
                )

        # Save the graph
        static_dir = os.path.join(current_app.root_path, 'static', 'graphs', 'performance_graphs')
        os.makedirs(static_dir, exist_ok=True)
        file_name = f"{footballer_id}_{graph_type.replace(' ', '_')}.png"
        file_path = os.path.join(static_dir, file_name)
        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        relative_path = f'/static/graphs/performance_graphs/{file_name}'
        return jsonify({'message': 'Graph generated', 'path': relative_path}), 200
    except Exception as e:
        print("Error during graph generation:", str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)