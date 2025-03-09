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
        ("data/processed_data/merged_players_last.csv", "players", [
            'player_id', 'footballer_id', 'footballer_name', 'rating', 'potential',
            'position_acronym', 'goalkeeping', 'mental', 'physical', 'technical',
            'aerial_reach', 'command_of_area', 'communication', 'eccentricity',
            'first_touch', 'handling', 'kicking', 'one_on_ones', 'passing',
            'punching_tendency', 'reflexes', 'rushing_out_tendency', 'throwing',
            'aggression', 'anticipation', 'bravery', 'composure', 'concentration',
            'decisions', 'determination', 'flair', 'leadership', 'off_the_ball',
            'positioning', 'teamwork', 'vision', 'work_rate', 'acceleration',
            'agility', 'balance', 'jumping_reach', 'natural_fitness', 'pace',
            'stamina', 'strength', 'free_kick_taking', 'penalty_taking',
            'technique', 'corners', 'crossing', 'dribbling', 'finishing', 'heading',
            'long_shots', 'long_throws', 'marking', 'tackling'
        ])
    ]

    try:
        for csv_path, table_name, columns in data_mappings:
            csv_loader.load_csv_to_table(csv_path, table_name, columns)
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
