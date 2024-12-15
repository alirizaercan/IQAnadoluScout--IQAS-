# backend/controllers/physical_dev_controller.py
import os 
from flask import Blueprint, request, jsonify, current_app, url_for
from services.physical_service import PhysicalService
from utils.database import Database
import random
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

physical_bp = Blueprint('physical_dev', __name__)
db = Database()

@physical_bp.route('/leagues', methods=['GET'])
def get_leagues():
    """Get all leagues."""
    print("GET request received at /api/physical-development/leagues")  # Debugging line
    session = db.connect()
    try:
        service = PhysicalService(session)
        leagues = service.get_all_leagues()
        if not leagues:
            return jsonify({'message': 'No leagues found'}), 404  # Return a clear message if no leagues found
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@physical_bp.route('/teams/<league_id>', methods=['GET'])
def get_teams(league_id):
    """Get teams by league_id."""
    session = db.connect()
    try:
        service = PhysicalService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@physical_bp.route('/footballers/<team_id>', methods=['GET'])
def get_footballers(team_id):
    """Get footballers by team_id."""
    session = db.connect()
    try:
        service = PhysicalService(session)
        footballers = service.get_footballers_by_team(team_id)
        return jsonify(footballers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@physical_bp.route('/physical-data', methods=['POST'])
def get_physical_data():
    """Get physical data for a footballer within a date range."""
    session = db.connect()
    data = request.json
    try:
        footballer_id = data.get('footballer_id')
        graph_type = data.get('graph_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        service = PhysicalService(session)
        graph_data = service.get_physical_data(footballer_id, graph_type, start_date, end_date)
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)
        
@physical_bp.route('/generate-graph', methods=['POST'])
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
        service = PhysicalService(session)
        physical_data = service.get_physical_data(footballer_id, graph_type, start_date, end_date)

        # Eğer veri yoksa hata döndür
        if not physical_data:
            return jsonify({'error': 'No data available for the selected criteria'}), 404

        # Verilere göre grafik oluştur
        days = [data['created_at'] for data in physical_data]
        plt.figure(figsize=(10, 5))
        
        def get_color(value, target):
            percentage = (value / target) * 100
            
            if percentage >= 85:  # Green for 85% and above
                return "#6BBE45"  # Matte Green
            elif percentage >= 70:  # Light orange for 70% to 85%
                return "#FFA500"  # Matte Orange
            else:  # Red for below 70%
                return "#D32F2F"  # Matte Red
            
        def convert_height_to_float(height_str):
                if height_str:
                    # 'm' veya 'cm' birimini ve boşlukları temizleyelim
                    height_str = height_str.replace("m", "").replace("cm", "").strip()
                    # Virgül olan yerleri nokta ile değiştirelim
                    height_str = height_str.replace(",", ".")
                    try:
                        return float(height_str)
                    except ValueError:
                        return 0.0  # Hatalı değer durumunda 0.0 dönüyoruz
                return 0.0

        if graph_type == "Physical Progress Tracker":
            metrics = {
                "Muscle Mass (kg)": [data['muscle_mass'] for data in physical_data],
                "Muscle Strength (kg)": [data['muscle_strength'] for data in physical_data],
                "Muscle Endurance (reps)": [data['muscle_endurance'] for data in physical_data],
                "Flexibility (cm)": [data['flexibility'] for data in physical_data]
            }

            targets = {metric: max(values) + random.randint(-20, +20) for metric, values in metrics.items()}

            # Tek grafik için oluşturulmuş figür
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.set_facecolor('#f0f0f0')
            card_width = 180
            card_height = 100
            ax.set_xlim(0, card_width * len(metrics))
            ax.set_ylim(0, card_height)

            for i, (metric, values) in enumerate(metrics.items()):
                avg_value = sum(values) / len(values)
                target = targets[metric]
                percentage = (avg_value / target) * 100
                color = get_color(avg_value, target)

                # Metrik kartını çiz
                ax.add_patch(Rectangle((i * card_width, 0), card_width, card_height, color='white', alpha=0.9))
                fill_height = (avg_value / target) * card_height
                ax.add_patch(Rectangle((i * card_width, 0), card_width, fill_height, color=color))

                # Metin etiketleri ekle
                ax.text((i + 0.5) * card_width, 60, f'Avg: {avg_value:.1f}', ha='center', fontsize=10)
                ax.text((i + 0.5) * card_width, 40, f'Target: {target}', ha='center', fontsize=10)
                ax.text((i + 0.5) * card_width, 20, f'{percentage:.1f}%', ha='center', fontsize=10, color=color)
                ax.text((i + 0.5) * card_width, 5, metric, ha='center', fontsize=9)

            ax.axis('off')

        elif graph_type == "Training Progress Time Tracker":
            # Verilerden metrikleri çıkartma
            metrics = {
                "Muscle Mass (kg)": [data['muscle_mass'] for data in physical_data],
                "Muscle Strength (kg)": [data['muscle_strength'] for data in physical_data],
                "Muscle Endurance (reps)": [data['muscle_endurance'] for data in physical_data],
                "Flexibility (cm)": [data['flexibility'] for data in physical_data]
            }

            # Hedef değerlerin dinamik olarak belirlenmesi: Her metrik için max değerin üzerine rastgele bir değer ekleniyor
            targets = {metric: max(values) + random.randint(-20, +20) for metric, values in metrics.items()}

            # Yüzdelik hesaplamalar
            muscle_mass_percentage = [(value / targets["Muscle Mass (kg)"]) * 100 for value in metrics["Muscle Mass (kg)"]]
            muscle_strength_percentage = [(value / targets["Muscle Strength (kg)"]) * 100 for value in metrics["Muscle Strength (kg)"]]
            muscle_endurance_percentage = [(value / targets["Muscle Endurance (reps)"]) * 100 for value in metrics["Muscle Endurance (reps)"]]
            flexibility_percentage = [(value / targets["Flexibility (cm)"]) * 100 for value in metrics["Flexibility (cm)"]]

            # Grafiğin çizilmesi
            plt.plot(days, muscle_mass_percentage, label="Muscle Mass (%)")
            plt.plot(days, muscle_strength_percentage, label="Muscle Strength (%)")
            plt.plot(days, muscle_endurance_percentage, label="Muscle Endurance (%)")
            plt.plot(days, flexibility_percentage, label="Flexibility (%)")

            # Başlık ve etiketler
            plt.title("Training Progress Time Tracker")
            plt.xlabel("Date")
            plt.ylabel("Value (%)")

            # Grafik üzerinde etiketler ve grid
            plt.legend()
            plt.grid(True)

            # X eksenindeki tarihleri daha okunabilir hale getirmek için döndürme
            plt.xticks(rotation=45)

            # Layout düzenlemesi
            plt.tight_layout()

        elif graph_type == "Body Composition Progress Tracker":
            weight_values = [data['weight'] for data in physical_data]
            height_values = [convert_height_to_float(data['heights']) for data in physical_data]
            muscle_mass_values = [data['muscle_mass'] for data in physical_data]

            # Grafik oluşturulması
            plt.figure(figsize=(10, 5))

            # Ağırlık, boy ve kas kütlesi için çizimler
            plt.fill_between(days, weight_values, color='lightblue', alpha=0.5, label='Weight (kg)')
            plt.fill_between(days, height_values, color='lightgreen', alpha=0.5, label='Height (cm)')
            plt.fill_between(days, muscle_mass_values, color='salmon', alpha=0.5, label='Muscle Mass (kg)')

            # Başlık ve etiketler
            plt.title("Body Composition Progress Tracker", fontsize=16)
            plt.xlabel("Date", fontsize=10)
            plt.ylabel("Value", fontsize=14)
            plt.xticks(days, [day.strftime('%d-%m') for day in days], rotation=45, fontsize=10)
            plt.yticks(np.arange(0, max(weight_values + height_values + muscle_mass_values) + 5, 5))

            # Grafik üzerinde etiketler ve grid
            plt.legend(loc='upper right')
            plt.grid(True)
            
        elif graph_type == "Athletic Performance Radar Analysis":
            metrics = {
                "Muscle Mass (kg)": [data['muscle_mass'] for data in physical_data],
                "Muscle Strength (kg)": [data['muscle_strength'] for data in physical_data],
                "Muscle Endurance (reps)": [data['muscle_endurance'] for data in physical_data],
                "Flexibility (cm)": [data['flexibility'] for data in physical_data]
            }

            averages = [sum(values) / len(values) for values in metrics.values()]
            labels = list(metrics.keys())

            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            averages += averages[:1]  # Close the radar chart
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            ax.fill(angles, averages, color='blue', alpha=0.25)
            ax.plot(angles, averages, color='blue', linewidth=2)
            ax.set_yticks([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)
            ax.set_title("Athletic Performance Radar Analysis", y=1.1)

        elif graph_type == "BMI Distribution Analysis":
            # Verilerin 'physical_data' içinden alınması
            height_values = [convert_height_to_float(data['heights']) for data in physical_data]
            weight_values = [data['weight'] for data in physical_data]

            # BMI Hesaplama
            bmi_values = [weight / (height ** 2) for weight, height in zip(weight_values, height_values)]

            # BMI Dağılımı - Histogram
            plt.hist(bmi_values, bins=10, color='royalblue', edgecolor='black', alpha=0.9)
            plt.title('BMI Distribution (Histogram)', fontsize=16, fontweight='bold')
            plt.xlabel('BMI', fontsize=14)
            plt.ylabel('Frequency', fontsize=14)
            plt.grid(axis='y', alpha=0.75)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)

        elif graph_type == "Comprehensive Physical Metrics Box Plot":
            # Verileri 'physical_data' içinden alıyoruz
            muscle_mass_values = [data['muscle_mass'] for data in physical_data]
            muscle_strength_values = [data['muscle_strength'] for data in physical_data]
            muscle_endurance_values = [data['muscle_endurance'] for data in physical_data]
            flexibility_values = [data['flexibility'] for data in physical_data]
            weight_values = [data['weight'] for data in physical_data]
            height_values = [convert_height_to_float(data['heights']) for data in physical_data]

            # BMI hesaplama: BMI = Ağırlık / (Boy * Boy)
            bmi_values = [weight / (height ** 2) for weight, height in zip(weight_values, height_values)]
            
            # Box plot çizimi: Kas kütlesi, kas gücü, kas dayanıklılığı, esneklik ve BMI verilerini birleştiriyoruz
            sns.boxplot(data=[muscle_mass_values, muscle_strength_values, muscle_endurance_values, flexibility_values, bmi_values], 
                        palette="pastel", orient="h", width=0.4)
            
            # Grafik başlıkları ve etiketleri
            plt.title('Physical Parameters Distribution (Box Plot)', fontsize=16, fontweight='bold')
            
            # Y eksenindeki etiketleri sağa kaydırma
            plt.yticks(ticks=[0, 1, 2, 3, 4], labels=['Muscle Mass (kg)', 'Muscle Strength (kg)', 
                                                        'Muscle Endurance (reps)', 'Flexibility (cm)', 'BMI'], 
                    fontsize=12)
            
            # Y-label'leri sağa kaydırmak için labelpad parametresi kullanıyoruz
            plt.ylabel('Physical Parameters', fontsize=14, labelpad=20)  # labelpad ile sağa kaydırma
            
            # X eksenindeki etiketler
            plt.xlabel('Values', fontsize=14)

        elif graph_type == "Dynamic Body Metrics Tracker":
            thigh_circumference = [data['thigh_circumference'] for data in physical_data]
            shoulder_circumference = [data['shoulder_circumference'] for data in physical_data]
            arm_circumference = [data['arm_circumference'] for data in physical_data]
            chest_circumference = [data['chest_circumference'] for data in physical_data]
            back_circumference = [data['back_circumference'] for data in physical_data]
            waist_circumference = [data['waist_circumference'] for data in physical_data]
            leg_circumference = [data['leg_circumference'] for data in physical_data]
            calf_circumference = [data['calf_circumference'] for data in physical_data]

            plt.plot(days, thigh_circumference, label="Thigh Circumference")
            plt.plot(days, shoulder_circumference, label="Shoulder Circumference")
            plt.plot(days, arm_circumference, label="Arm Circumference")
            plt.plot(days, chest_circumference, label="Chest Circumference")
            plt.plot(days, back_circumference, label="Back Circumference")
            plt.plot(days, waist_circumference, label="Waist Circumference")
            plt.plot(days, leg_circumference, label="Leg Circumference")
            plt.plot(days, calf_circumference, label="Calf Circumference")
            plt.title("Dynamic Body Metrics Tracker")
            plt.xlabel("Date")
            plt.ylabel("Value (%)")

            # Grafik üzerinde etiketler ve grid
            plt.legend()
            plt.grid(True)

        else:
            return jsonify({'error': f'Unknown graph type: {graph_type}'}), 400


        # Statik klasöre kaydet
        static_dir = os.path.join(current_app.root_path, 'static', 'graphs', 'physical_graphs')
        os.makedirs(static_dir, exist_ok=True)
        file_name = f"{footballer_id}_{graph_type.replace(' ', '_')}_{start_date}_{end_date}.png"
        file_path = os.path.join(static_dir, file_name)
        plt.savefig(file_path)
        plt.close()

        # Dosya gerçekten oluşturuldu mu kontrol et
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Graph file not found at {file_path}")

        # Ön uç için göreceli yol döndür
        relative_path = f'/static/graphs/physical_graphs/{file_name}'
        return jsonify({'message': 'Graph generated', 'path': relative_path}), 200

    except Exception as e:
        # Hataları yakala ve logla
        print("Error during graph generation:", str(e))
        return jsonify({'error': str(e)}), 500

    finally:
        # Bağlantıyı kapat
        db.close(session)