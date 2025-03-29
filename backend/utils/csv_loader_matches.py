import os
import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Veritabanı yöneticisini başlat."""
        self.connection = None
        self.cursor = None

    def connect(self):
        """Veritabanına bağlan."""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL ortam değişkeni bulunamadı")
            
            self.connection = psycopg2.connect(database_url)
            self.cursor = self.connection.cursor()
            print("Veritabanı bağlantısı başarılı.")
        except (Exception, psycopg2.Error) as error:
            print(f"Veritabanı bağlantı hatası: {error}")
            raise

    def close(self):
        """Veritabanı bağlantısını kapat."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                print("Veritabanı bağlantısı kapatıldı.")
        except (Exception, psycopg2.Error) as error:
            print(f"Bağlantı kapatma hatası: {error}")

    def execute_query(self, query, values=None):
        """SQL sorgusu çalıştır."""
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            return self.cursor
        except psycopg2.Error as e:
            print(f"Sorgu çalıştırma hatası: {e}")
            self.connection.rollback()
            raise

    def commit(self):
        """Değişiklikleri kaydet."""
        try:
            self.connection.commit()
            print("Değişiklikler kaydedildi.")
        except psycopg2.Error as e:
            print(f"Commit hatası: {e}")
            self.connection.rollback()

class CSVLoader:
    def __init__(self, db_manager):
        """CSV yükleyiciyi başlat."""
        self.db_manager = db_manager

    def prepare_row_values(self, row, columns):
        """
        Satır değerlerini veritabanına uygun şekilde hazırla.
        NaN ve numpy türlerini NULL veya uygun değerlere dönüştürür.
        """
        prepared_values = []
        for col in columns:
            value = row[col]
            
            # NaN kontrolü
            if pd.isna(value) or value is None:
                prepared_values.append(None)
            # numpy integer türlerini Python integer'ına dönüştür
            elif isinstance(value, np.integer):
                prepared_values.append(int(value))
            # numpy float türlerini Python float'ına dönüştür
            elif isinstance(value, np.floating):
                prepared_values.append(float(value))
            # diğer numpy türlerini normal Python türlerine dönüştür
            elif isinstance(value, np.ndarray):
                prepared_values.append(value.tolist())
            else:
                prepared_values.append(value)
        
        return tuple(prepared_values)

    def load_csv_to_table(self, csv_path, table_name, columns, skip_existing=True):
        """
        CSV dosyasını belirtilen tabloya yükle.
        
        Args:
            csv_path (str): CSV dosyasının yolu
            table_name (str): Hedef tablo adı
            columns (list): Yüklenecek sütunlar
            skip_existing (bool): Mevcut kayıtları atla
        """
        try:
            # CSV dosyasını oku
            data = pd.read_csv(csv_path)
            
            # İlk sütunu PRIMARY KEY varsay
            primary_key_column = columns[0]
            
            # Toplam satır ve işlenen satır sayısını takip et
            total_rows = len(data)
            processed_rows = 0
            skipped_rows = 0
            
            for _, row in data.iterrows():
                # PRIMARY KEY değerini al
                primary_key_value = row[primary_key_column]
                
                # Kayıt kontrolü
                if skip_existing:
                    select_query = sql.SQL("SELECT 1 FROM {table} WHERE {primary_key} = %s").format(
                        table=sql.Identifier(table_name),
                        primary_key=sql.Identifier(primary_key_column)
                    )
                    self.db_manager.execute_query(select_query, (primary_key_value,))
                    exists = self.db_manager.cursor.fetchone()
                    
                    if exists:
                        skipped_rows += 1
                        continue
                
                # INSERT sorgusu oluştur
                placeholders = ", ".join(["%s"] * len(columns))
                insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
                    table=sql.Identifier(table_name),
                    fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                    values=sql.SQL(placeholders)
                )
                
                # Sütunları hazırla ve NaN/numpy türlerini işle
                row_values = self.prepare_row_values(row, columns)
                
                try:
                    self.db_manager.execute_query(insert_query, row_values)
                    processed_rows += 1
                except psycopg2.Error as e:
                    print(f"Satır eklenirken hata: {e}")
                    print(f"Sorunlu satır: {row_values}")
                    # Hatalı satırı bir dosyaya kaydet
                    with open('error_rows.log', 'a') as f:
                        f.write(f"Hata: {e}\nSatır: {row_values}\n\n")
            
            # Değişiklikleri kaydet
            self.db_manager.commit()
            
            print(f"\nCSV Yükleme Raporu:")
            print(f"Toplam Satır: {total_rows}")
            print(f"İşlenen Satır: {processed_rows}")
            print(f"Atlanan Satır: {skipped_rows}")
        
        except Exception as e:
            print(f"CSV yükleme hatası: {e}")
            self.db_manager.connection.rollback()

def main():
    # Veritabanı bağlantısı
    db_manager = DatabaseManager()
    db_manager.connect()
    
    # CSV verilerinin yüklenmesi
    csv_loader = CSVLoader(db_manager)
    
    # CSV dosyaları ve tablo eşleşmeleri
    data_mappings = [
        ("data/processed_data/matches_scores_structured.csv", "matches", [
            'match_id', 'league_id', 'week', 'date', 'home_team_id', 
            'home_team', 'home_goals', 'away_team_id', 'away_team', 
            'away_goals', 'season', 'home_footballer_id', 
            'away_footballer_id', 'is_played'
        ])
    ]
    
    try:
        for csv_path, table_name, columns in data_mappings:
            csv_loader.load_csv_to_table(csv_path, table_name, columns)
    
    except Exception as e:
        print(f"Ana işlemde hata: {e}")
    
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()