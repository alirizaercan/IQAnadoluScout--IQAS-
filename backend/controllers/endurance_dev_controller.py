# backend/controllers/endurance_dev_controller.py
import os 
from flask import Blueprint, request, jsonify, current_app, url_for
from services.endurance_service import EnduranceService
from utils.database import Database
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

endurance_bp = Blueprint('endurance_dev', __name__)
db = Database()

@endurance_bp.route('/leagues', methods=['GET'])
def get_leagues():
    """Get all leagues."""
    print("GET request received at /api/endurance-development/leagues")  # Debugging line
    session = db.connect()
    try:
        service = EnduranceService(session)
        leagues = service.get_all_leagues()
        if not leagues:
            return jsonify({'message': 'No leagues found'}), 404  # Return a clear message if no leagues found
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@endurance_bp.route('/teams/<league_id>', methods=['GET'])
def get_teams(league_id):
    """Get teams by league_id."""
    session = db.connect()
    try:
        service = EnduranceService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@endurance_bp.route('/footballers/<team_id>', methods=['GET'])
def get_footballers(team_id):
    """Get footballers by team_id."""
    session = db.connect()
    try:
        service = EnduranceService(session)
        footballers = service.get_footballers_by_team(team_id)
        return jsonify(footballers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@endurance_bp.route('/endurance-data', methods=['POST'])
def get_endurance_data():
    """Get endurance data for a footballer within a date range."""
    session = db.connect()
    data = request.json
    try:
        footballer_id = data.get('footballer_id')
        graph_type = data.get('graph_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        service = EnduranceService(session)
        graph_data = service.get_endurance_data(footballer_id, graph_type, start_date, end_date)
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)
        
@endurance_bp.route('/generate-graph', methods=['POST'])
def generate_graph():
    """Generate graph based on selected type and date range."""
    data = request.json
    graph_type = data.get('graph_type')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    footballer_id = data.get('footballer_id')
    
    session = db.connect()
    
    try:
        # Fiziksel verileri al
        service = EnduranceService(session)
        endurance_data = service.get_endurance_data(footballer_id, graph_type, start_date, end_date)

        # Eğer veri yoksa hata döndür
        if not endurance_data:
            return jsonify({'error': 'No data available for the selected criteria'}), 404

        # Verilere göre grafik oluştur
        days = [data['created_at'] for data in endurance_data]
        plt.figure(figsize=(10, 5))

        if graph_type == "Key Endurance Metrics Overview":
            running_distance_values = [data['running_distance'] for data in endurance_data]
            average_speed_values = [data['average_speed'] for data in endurance_data]
            heart_rate_values = [data['heart_rate'] for data in endurance_data]
            
            fig, ax = plt.subplots(1, 3, figsize=(10, 5))
            
            # Running Distance Card
            ax[0].barh(['Player'], [np.mean(running_distance_values)], color='lightblue')
            ax[0].set_xlim(0, 10)
            ax[0].set_title('Average Running Distance (km)', fontsize=14)
            ax[0].text(np.mean(running_distance_values) + 0.1, 0, f"{np.mean(running_distance_values):.2f}", va='center')

            # Average Speed Card
            ax[1].barh(['Player'], [np.mean(average_speed_values)], color='lightgreen')
            ax[1].set_xlim(0, 15)
            ax[1].set_title('Average Speed (km/h)', fontsize=14)
            ax[1].text(np.mean(average_speed_values) + 0.1, 0, f"{np.mean(average_speed_values):.2f}", va='center')

            # Heart Rate Card
            ax[2].barh(['Player'], [np.mean(heart_rate_values)], color='salmon')
            ax[2].set_xlim(100, 200)
            ax[2].set_title('Average Heart Rate (bpm)', fontsize=14)
            ax[2].text(np.mean(heart_rate_values) + 1, 0, f"{np.mean(heart_rate_values):.2f}", va='center')

            # Adjust layout
            plt.tight_layout()
            
            
        elif graph_type == "Endurance Trends":
            running_distance_values = [data['running_distance'] for data in endurance_data]
            average_speed_values = [data['average_speed'] for data in endurance_data]
            heart_rate_values = [data['heart_rate'] for data in endurance_data]
            
            plt.plot(days, running_distance_values, marker='o', color='royalblue', label='Running Distance (km)')
            plt.plot(days, average_speed_values, marker='o', color='orange', label='Average Speed (km/h)')
            plt.plot(days, heart_rate_values, marker='o', color='red', label='Heart Rate (bpm)')
            plt.title('Endurance Metrics Over 30 Days', fontsize=16, fontweight='bold')
            plt.xlabel('Days', fontsize=10)
            plt.ylabel('Values', fontsize=14)
            plt.xticks(days, [day.strftime('%d-%m') for day in days], rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend()
            plt.grid()
            plt.tight_layout()


        elif graph_type == "Peak Heart Rate Focused Endurance Development":
            session_values = [data['session'] for data in endurance_data]
            peak_heart_rate_values = [data['peak_heart_rate'] for data in endurance_data]

            # Create the plot with a professional style (using 'ggplot' style)
            plt.style.use('ggplot')  # Using a built-in style from matplotlib

            # Plotting the peak heart rate with a bar chart and adding edge color
            bars = plt.bar(session_values, peak_heart_rate_values, color='slateblue', width=0.6, edgecolor='black')

            # Adding horizontal lines for clarity
            plt.axhline(y=np.mean(peak_heart_rate_values), color='r', linestyle='--', label=f'Mean: {np.mean(peak_heart_rate_values):.2f} bpm')

            # Title and labels with professional font settings
            plt.title('Peak Heart Rate Development Over 10 Sessions', fontsize=18, fontweight='bold')
            plt.xlabel('Sessions', fontsize=14, fontweight='bold')
            plt.ylabel('Peak Heart Rate (bpm)', fontsize=14, fontweight='bold')

            # Add custom ticks and grid
            plt.xticks(session_values, fontsize=12)
            plt.yticks(fontsize=12)
            plt.grid(True, linestyle=':', color='gray', alpha=0.6)

            # Adding value labels on top of the bars for clarity
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, yval + 2, round(yval, 1), ha='center', va='bottom', fontsize=10)

            # Display the plot with a tight layout
            plt.legend(loc='upper left', fontsize=12)
            plt.tight_layout()


        elif graph_type == "Performance Radar":
            # Oyuncunun verileri
            running_distance_values = [data['running_distance'] for data in endurance_data]
            average_speed_values = [data['average_speed'] for data in endurance_data]
            heart_rate_values = [data['heart_rate'] for data in endurance_data]
            player_values = [np.mean(running_distance_values), np.mean(average_speed_values), np.mean(heart_rate_values)]
            
            # Diğer oyuncuların verileri için sorgu
            footballer_id = data.get('footballer_id')  # Kullanıcıdan "team_id" bilgisi alınmalı
            other_players_data = service.get_other_players_data(footballer_id, start_date, end_date)
            
            # Diğer oyuncuların verilerinin ortalamalarını hesapla
            other_running_distance_values = [item['running_distance'] for item in other_players_data]
            other_average_speed_values = [item['average_speed'] for item in other_players_data]
            other_heart_rate_values = [item['heart_rate'] for item in other_players_data]
            other_players_values = [
                np.mean(other_running_distance_values) if other_running_distance_values else 0,
                np.mean(other_average_speed_values) if other_average_speed_values else 0,
                np.mean(other_heart_rate_values) if other_heart_rate_values else 0
            ]

            # Radar grafiği için kategoriler
            categories = ['Running Distance (km)', 'Average Speed (km/h)', 'Heart Rate (bpm)']
            num_vars = len(categories)

            # Açıları hesapla
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

            # Verileri çemberin kapatılması için döngüyü tamamla
            player_values += player_values[:1]
            other_players_values += other_players_values[:1]
            angles += angles[:1]

            # Radar grafiği oluştur
            fig, ax = plt.subplots(figsize=(8, 5), subplot_kw=dict(polar=True))
            ax.fill(angles, player_values, color='blue', alpha=0.25, label='Player')
            ax.fill(angles, other_players_values, color='red', alpha=0.25, label='Team Average')

            # Etiketler ve grafik ayarları
            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12)
            ax.set_title('Endurance Comparison (Radar Chart)', fontsize=16, fontweight='bold')
            ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

            # Arka plan olmadan göster
            ax.spines['polar'].set_visible(False)  # Arka planı kaldır
            plt.tight_layout()


        else:
            return jsonify({'error': f'Unknown graph type: {graph_type}'}), 400


        # Statik klasöre kaydet
        static_dir = os.path.join(current_app.root_path, 'static', 'graphs', 'endurance_graphs')
        os.makedirs(static_dir, exist_ok=True)
        file_name = f"{footballer_id}_{graph_type.replace(' ', '_')}_{start_date}_{end_date}.png"
        file_path = os.path.join(static_dir, file_name)
        plt.savefig(file_path)
        plt.close()

        # Dosya gerçekten oluşturuldu mu kontrol et
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Graph file not found at {file_path}")

        # Ön uç için göreceli yol döndür
        relative_path = f'/static/graphs/endurance_graphs/{file_name}'
        return jsonify({'message': 'Graph generated', 'path': relative_path}), 200

    except Exception as e:
        # Hataları yakala ve logla
        print("Error during graph generation:", str(e))
        return jsonify({'error': str(e)}), 500

    finally:
        # Bağlantıyı kapat
        db.close(session)