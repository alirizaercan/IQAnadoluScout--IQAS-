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
        ("data/raw_data/leagues.csv", "leagues", [
            "league_id", "league_name", "league_logo_path", "country", "num_teams", "players",
            "foreign_players", "avg_marketing_val", "avg_age", "most_valuable_player", "total_market_value"
        ]),
        ("data/raw_data/football_teams.csv", "football_teams", [
            "team_id", "league_name","league_id", "team_name", "team_info_link", "img_path", "num_players",
            "avg_age", "num_legionnaires", "avg_marketing_val", "total_squad_value"
        ]),
        ("data/raw_data/footballers.csv", "footballers", [
            "footballer_id", "league_id", "team_id", "footballer_name", "club", "league_name",
            "trikot_num", "position", "birthday", "age", "nationality_img_path", "height",
            "feet", "contract", "market_value", "footballer_img_path"
        ]),
        ("data/processed_data/physical.csv", "physical", [
            "id", "footballer_id", "muscle_mass", "muscle_strength", "muscle_endurance", "flexibility",
            "weight", "body_fat_percentage", "heights", "thigh_circumference", "shoulder_circumference",
            "arm_circumference", "chest_circumference", "back_circumference", "waist_circumference",
            "leg_circumference", "calf_circumference", "created_at", "timestamp"
        ]),
        ("data/processed_data/conditional.csv", "conditional", [
            "id", "footballer_id", "vo2_max", "lactate_levels", "training_intensity", "recovery_times",
            "current_vo2_max", "current_lactate_levels", "current_muscle_strength", "target_vo2_max",
            "target_lactate_level", "target_muscle_strength", "created_at", "timestamp"
        ]),
        ("data/processed_data/endurance.csv", "endurance", [
            "id", "footballer_id", "running_distance", "average_speed", "heart_rate", "peak_heart_rate",
            "training_intensity", "session", "created_at", "timestamp"
        ]),
    ]

    try:
        for csv_path, table_name, columns in data_mappings:
            csv_loader.load_csv_to_table(csv_path, table_name, columns)
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
