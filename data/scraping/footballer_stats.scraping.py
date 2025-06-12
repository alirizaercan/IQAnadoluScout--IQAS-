# Footballer Stats Scraping Script
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

# Ana URL ve temel URL tanımları
base_url = 'https://www.sofascore.com'
main_url = 'https://www.sofascore.com'

# WebDriver başlatılıyor
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

# Debug modunu etkinleştir
print("WebDriver başlatılıyor...")
driver = webdriver.Chrome(options=options)
print("WebDriver başlatıldı.")

# 'players_raw.csv' dosyasının konumu
path = os.path.abspath("data/processed_data/players_raw.csv")
players_raw = []

try:
    # Oyuncu bilgilerini CSV dosyasından okuma
    print(f"CSV dosyası okunuyor: {path}")
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # İlk satırı atla
        for row in reader:
            players_raw.append({'footballer_id': row[0], 'footballer_name': row[1]})
    print(f"Toplam {len(players_raw)} oyuncu okundu.")
except FileNotFoundError:
    print(f"Dosya bulunamadı: {path}")
    driver.quit()
    exit()

# Veri kaydedilecek dosyanın konumu
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)
csv_filename = os.path.join(csv_dir, "players_sofascore.csv")

# CSV dosyasını oluşturma ve yazma
player_id_counter = 1  # player_id için sayaç

# İstatistikleri çekme fonksiyonu
def get_all_statistics(soup):
    statistics = {}
    # Tüm istatistikleri içeren div'leri bul
    stat_sections = soup.find_all('div', {'class': 'Box fTPNOD'})
    for section in stat_sections:
        rows = section.find_all('div', {'class': 'Box Flex dlyXLO bnpRyo'})
        for row in rows:
            stat_name = row.find('span', {'color': 'onSurface.nLv1'}).text.strip()
            stat_value = row.find_all('span', {'color': 'onSurface.nLv1'})[1].text.strip()
            statistics[stat_name] = stat_value
    return statistics

# Average Sofascore Rating değerini çekme fonksiyonu
def get_average_rating(soup):
    try:
        # Average Sofascore Rating butonunu bul
        rating_button = soup.find('button', {'class': 'Button ihQooJ'})
        if rating_button:
            # Buton içindeki span elementi içindeki değeri al
            rating_value = rating_button.find('span', {'role': 'meter'}).text.strip()
            return rating_value
    except Exception as e:
        print(f"Average Sofascore Rating çekilirken hata oluştu: {e}")
    return '0'

# İlk oyuncuyu işleyerek sütun başlıklarını belirle
first_player = players_raw[0]
player_name = first_player['footballer_name']
print(f"\n--- İşleniyor: {player_name} ---")
driver.get(main_url)
time.sleep(2)

# Arama kutusunu bul ve oyuncu ismini yaz
search_box = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, '//input[@id="search-input"]'))
)
search_box.clear()
search_box.send_keys(player_name)
search_box.send_keys(Keys.ENTER)
time.sleep(3)

# İlk çıkan futbolcunun linkini bul
first_player_link = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/player/")]'))
)
player_path = first_player_link.get_attribute('href')
if not player_path.startswith('http'):
    player_url = base_url + player_path
else:
    player_url = player_path

# Oyuncu sayfasına git
driver.get(player_url)
time.sleep(3)

# Sayfa içeriğini işle
player_soup = BeautifulSoup(driver.page_source, 'html.parser')
statistics = get_all_statistics(player_soup)

# Average Sofascore Rating değerini al
average_rating = get_average_rating(player_soup)
statistics['Average Sofascore Rating'] = average_rating

# Sütun başlıklarını belirle
header = ['player_id', 'footballer_id', 'footballer_name'] + list(statistics.keys())

# CSV dosyasını oluştur ve başlıkları yaz
with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(header)

    # Tüm oyuncuları işle
    for player in players_raw:
        footballer_id = player['footballer_id']
        player_name = player['footballer_name']
        try:
            print(f"\n--- İşleniyor: {player_name} ---")
            driver.get(main_url)
            time.sleep(2)

            # Arama kutusunu bul ve oyuncu ismini yaz
            search_box = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@id="search-input"]'))
            )
            search_box.clear()
            search_box.send_keys(player_name)
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)

            # İlk çıkan futbolcunun linkini bul
            first_player_link = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/player/")]'))
            )
            player_path = first_player_link.get_attribute('href')
            if not player_path.startswith('http'):
                player_url = base_url + player_path
            else:
                player_url = player_path

            # Oyuncu sayfasına git
            driver.get(player_url)
            time.sleep(3)

            # Sayfa içeriğini işle
            player_soup = BeautifulSoup(driver.page_source, 'html.parser')
            statistics = get_all_statistics(player_soup)

            # Average Sofascore Rating değerini al
            average_rating = get_average_rating(player_soup)
            statistics['Average Sofascore Rating'] = average_rating

            # Veriyi CSV'ye yaz
            row = [player_id_counter, footballer_id, player_name] + [statistics.get(stat, '0') for stat in header[3:]]
            writer.writerow(row)
            print(f"Veriler CSV'ye yazıldı: {player_name}")
            player_id_counter += 1

        except Exception as e:
            print(f"Error processing player {player_name}: {e}")
            continue

driver.quit()
print(f"İşlem tamamlandı. Veriler şuraya kaydedildi: {csv_filename}")