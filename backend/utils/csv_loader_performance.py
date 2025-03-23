import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını yükler

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Veritabanına bağlan."""
        database_url = os.getenv("DATABASE_URL")  # .env dosyasından DATABASE_URL'yi alır
        self.connection = psycopg2.connect(database_url)
        self.cursor = self.connection.cursor()

    def close(self):
        """Bağlantıyı kapat."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, values=None):
        """SQL sorgusu çalıştır."""
        self.cursor.execute(query, values)

    def commit(self):
        """Değişiklikleri kaydet."""
        self.connection.commit()

class CSVLoader:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def load_csv_to_table(self, csv_path, table_name, columns):
        """CSV dosyasını belirtilen tabloya yükle, mevcut kayıtları atla."""
        data = pd.read_csv(csv_path)
        data = data.where(pd.notnull(data), None)  # NULL değerleri düzenler

        for _, row in data.iterrows():
            # PRIMARY KEY veya UNIQUE alanı için bir kontrol yap
            primary_key_column = columns[0]  # İlk sütunu PRIMARY KEY varsayıyoruz
            primary_key_value = row[primary_key_column]

            # Veritabanında bu PRIMARY KEY'e sahip bir kayıt var mı kontrol et
            select_query = sql.SQL("SELECT 1 FROM {table} WHERE {primary_key} = %s").format(
                table=sql.Identifier(table_name),
                primary_key=sql.Identifier(primary_key_column)
            )
            self.db_manager.execute_query(select_query, (primary_key_value,))
            exists = self.db_manager.cursor.fetchone()

            if exists:
                # Kayıt zaten varsa, ekleme yapma
                print(f"Record with {primary_key_column}={primary_key_value} already exists. Skipping.")
                continue

            # Yeni kayıt için INSERT sorgusu oluştur
            placeholders = ", ".join(["%s"] * len(row))
            insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
                table=sql.Identifier(table_name),
                fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                values=sql.SQL(placeholders)
            )
            self.db_manager.execute_query(insert_query, tuple(row))

        self.db_manager.commit()


def main():
    # Veritabanı bağlantısı
    db_manager = DatabaseManager()
    db_manager.connect()

    # CSV verilerinin yüklenmesi
    csv_loader = CSVLoader(db_manager)

    data_mappings = [
        ("data/processed_data/players_sofascore_performance.csv", "performance", [
            'player_id', 'footballer_id', 'footballer_name', 'total_played', 'started', 
            'minutes_per_game', 'total_minutes_played', 'team_of_the_week', 'goals_conceded_per_game', 
            'penalties_saved', 'saves_per_game', 'succ_runs_out_per_game', 'goals_conceded', 
            'conceded_from_inside_box', 'conceded_from_outside_box', 'saves_made', 'goals_prevented', 
            'saves_from_inside_box', 'saves_from_outside_box', 'saves_caught', 'saves_parried', 
            'goals', 'scoring_frequency', 'goals_per_game', 'shots_per_game', 'shots_on_target_per_game', 
            'big_chances_missed', 'goal_conversion', 'penalty_goals', 'penalty_conversion', 
            'free_kick_goals', 'free_kick_conversion', 'goals_from_inside_the_box', 'goals_from_outside_the_box', 
            'headed_goals', 'left_foot_goals', 'right_foot_goals', 'penalty_won', 'assists', 
            'expected_assists_xa', 'touches_per_game', 'big_chances_created', 'key_passes_per_game', 
            'accurate_per_game', 'acc_own_half', 'acc_opposition_half', 'acc_long_balls', 
            'acc_chipped_passes', 'acc_crosses', 'clean_sheets', 'interceptions_per_game', 
            'tackles_per_game', 'possession_won_final_third', 'balls_recovered_per_game', 
            'dribbled_past_per_game', 'clearances_per_game', 'errors_leading_to_shot', 
            'errors_leading_to_goal', 'penalties_committed', 'succ_dribbles', 'total_duels_won', 
            'ground_duels_won', 'aerial_duels_won', 'possession_lost', 'fouls', 'was_fouled', 
            'offsides', 'goal_kicks_per_game', 'yellow', 'yellow_red', 'red_cards', 
            'average_sofascore_rating'
        ])
    ]

    try:
        for csv_path, table_name, columns in data_mappings:
            csv_loader.load_csv_to_table(csv_path, table_name, columns)
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()