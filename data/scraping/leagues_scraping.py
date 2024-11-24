from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

# URL'ler ve lig ID'leri
urls = [
    {"url": "https://www.transfermarkt.us/super-lig/startseite/wettbewerb/TR1", "league_id": "tr1"},
    {"url": "https://www.transfermarkt.us/1-lig/startseite/wettbewerb/TR2", "league_id": "tr2"},
    {"url": "https://www.transfermarkt.us/pko-ekstraklasa/startseite/wettbewerb/PL1", "league_id": "pl1"},
]

# WebDriver başlatılıyor
driver = webdriver.Chrome()

# CSV dosyasını ayarlıyoruz
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)  # Eğer 'data/raw_data' dizini yoksa oluşturuyoruz

csv_filename = os.path.join(csv_dir, "leagues.csv")

with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    # Başlıkları yazıyoruz
    header = [
        'league_name', 'league_id', 'league_logo_path', 'country',
        'num_teams', 'players', 'foreign_players', 'avg_marketing_val',
        'avg_age', 'most_valuable_player', 'total_market_value'
    ]
    writer.writerow(header)

    # Her bir URL için veri çekiyoruz
    for league_data in urls:
        url = league_data["url"]
        league_id = league_data["league_id"]

        print(f"Processing URL: {url}")

        # Sayfayı açıyoruz
        driver.get(url)
        time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekle

        # Sayfa içeriği BeautifulSoup ile analiz ediliyor
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Lig bilgilerini çekiyoruz
        try:
            league = soup.find('header', class_='data-header')

            league_name = league.find('h1', class_='data-header__headline-wrapper data-header__headline-wrapper--oswald').text.strip()
            league_logo_path = league.find('div', class_='data-header__profile-container').img['src']
            country = league.find('div', class_='data-header__club-info').a.text.strip()

            spans = league.find_all('li', class_='data-header__label')

            if len(spans) >= 6:
                num_teams = spans[0].find('span', class_='data-header__content').text.strip()
                players = spans[1].find('span', class_='data-header__content').text.strip()
                foreign_players_data = spans[2].find('span', class_='data-header__content')
                foreign_players = foreign_players_data.text.split('Players')[0].strip()
                avg_marketing_val = spans[3].find('span', class_='data-header__content').text.strip()
                avg_age = spans[4].find('span', class_='data-header__content').text.strip()
                mvp_data = spans[5].find('span', class_='data-header__content')
                most_valuable_player = mvp_data.find('a').text.strip()
            else:
                num_teams = players = foreign_players = avg_marketing_val = avg_age = most_valuable_player = 'N/A'

            market_value_wrapper = league.find('a', class_='data-header__market-value-wrapper')
            if market_value_wrapper:
                # Tüm metni düz bir şekilde al
                raw_value = market_value_wrapper.get_text(strip=True)
                # "Total Market Value" kısmını at ve geri kalanı al
                total_market_value = raw_value.replace('Total Market Value', '').strip()
            else:
                total_market_value = 'N/A'  # Eğer element bulunamazsa

            # Verileri CSV dosyasına yazıyoruz
            writer.writerow([
                league_name, league_id, league_logo_path, country,
                num_teams, players, foreign_players, avg_marketing_val,
                avg_age, most_valuable_player, total_market_value
            ])

        except AttributeError as e:
            # Veri çekilemezse hatayı atlıyoruz
            print(f"Error processing league data from {url}: {e}")
            continue

# Tarayıcıyı kapatıyoruz
driver.quit()

# İşlem tamamlandığında mesaj yazdırıyoruz
print(f"Data extracted and saved to {csv_filename}")
