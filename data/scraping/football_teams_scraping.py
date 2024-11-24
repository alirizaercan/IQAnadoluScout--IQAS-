from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

# Ligdeki URL'leri listeleyelim
urls = [
    "https://www.transfermarkt.us/super-lig/startseite/wettbewerb/TR1",  # Süper Lig
    "https://www.transfermarkt.us/pko-ekstraklasa/startseite/wettbewerb/PL1",  # Ekstraklasa
    "https://www.transfermarkt.com.tr/super-lig/startseite/wettbewerb/TR2"  # TFF 1. Lig
]

# WebDriver başlatılıyor
driver = webdriver.Chrome()

# CSV dosyasını açıyoruz
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)  # Eğer 'data/raw_data' dizini yoksa oluşturuyoruz

csv_filename = os.path.join(csv_dir, "football_teams.csv")

with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    # Başlıkları yazıyoruz
    header = ['team_id', 'league_name', 'league_id', 'team_name', 'team_info_link', 'img_path', 'num_players', 'avg_age', 'num_legionnaires', 'avg_marketing_val', 'total_squad_value']
    writer.writerow(header)

    # Her URL için işlem yapıyoruz
    team_counter = 0  # Takım ID'si için sayıcıyı başlatıyoruz
    for url in urls:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Sayfanın yüklenmesini bekle
        time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekle

        # Sayfa içeriği BeautifulSoup ile analiz ediliyor
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Lig adı ve ID'si URL'den çıkarılabilir
        if "TR1" in url:
            league = 'Super League'
            league_id = 'tr1'
        elif "PL1" in url:
            league = 'PKO BP Ekstraklasa'
            league_id = 'pl1'
        elif "TR2" in url:
            league = 'Trendyol TFF 1. League'
            league_id = 'tr2'
        else:
            league = 'Unknown League'
            league_id = 'unknown'

        # Debugging çıktısı
        print(f"Processing URL: {url}, League: {league}, League ID: {league_id}")

        # Takımların bulunduğu tüm satırları alıyoruz
        teams = soup.find_all('tr', class_=['odd', 'even'])

        # Her bir takım için bilgileri alıyoruz
        for team in teams:
            try:
                team_counter += 1  # Benzersiz team_id oluşturmak için sayaç artırılıyor

                # Team name
                team_name_tag = team.find('td', class_='hauptlink no-border-links')
                team_name = team_name_tag.a.text.strip() if team_name_tag else 'N/A'

                # Team info link
                team_info_link = team_name_tag.a['href'] if team_name_tag else 'N/A'

                # Team image path
                img_tag = team.find('img', class_='tiny_wappen')
                img_path = img_tag['src'] if img_tag else 'N/A'

                # num_players, avg_age, num_legionnaires
                tds = team.find_all('td', class_='zentriert')
                num_players = tds[0].text.strip() if len(tds) > 0 else 'N/A'
                avg_age = tds[1].text.strip() if len(tds) > 1 else 'N/A'
                num_legionnaires = tds[2].text.strip() if len(tds) > 2 else 'N/A'

                # Avg marketing value ve total squad value
                financial_tds = team.find_all('td', class_='rechts')
                avg_marketing_val = financial_tds[0].text.strip() if len(financial_tds) > 0 else 'N/A'
                total_squad_value = financial_tds[1].a.text.strip('()') if len(financial_tds) > 1 and financial_tds[1].a else 'N/A'

                # Verileri CSV dosyasına yazıyoruz
                writer.writerow([team_counter, league, league_id, team_name, team_info_link, img_path, num_players, avg_age, num_legionnaires, avg_marketing_val, total_squad_value])

            except Exception as e:
                print(f"Error processing team: {e}")
                continue

# Tarayıcıyı kapatıyoruz
driver.quit()

# İşlem tamamlandığında mesaj yazdırıyoruz
print(f"Data extracted and saved to {csv_filename}")
