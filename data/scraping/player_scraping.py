from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import os

# Ana URL ve temel URL tanımları
base_url = 'https://fminside.net'
main_url = 'https://fminside.net/players'

# WebDriver başlatılıyor
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')

driver = webdriver.Chrome(options=options)

# 'players_raw.csv' dosyasının konumu
path = os.path.abspath("data/processed_data/players_raw.csv")

players_raw = []
try:
    # Oyuncu bilgilerini CSV dosyasından okuma
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)  # Sütun başlıkları olmayan bir CSV için normal reader kullanıyoruz
        for row in reader:
            players_raw.append({'footballer_id': row[0], 'footballer_name': row[1]})
except FileNotFoundError:
    print(f"Dosya bulunamadı: {path}")
    driver.quit()
    exit()

# Veri kaydedilecek dosyanın konumu
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)
csv_filename = os.path.join(csv_dir, "players.csv")

# Header satırı
header = [
    'player_id', 'footballer_id', 'footballer_name', 'rating', 'potential', 'position_acronym', 'goalkeeping', 'mental',
    'physical', 'technical', 'aerial-reach', 'command-of-area', 'communication', 'eccentricity', 'first-touch', 'handling',
    'kicking', 'one-on-ones', 'passing', 'punching-tendency', 'reflexes', 'rushing-out-tendency', 'throwing', 'aggression',
    'anticipation', 'bravery', 'composure', 'concentration', 'decisions', 'determination', 'flair', 'leadership', 'off-the-ball',
    'positioning', 'teamwork', 'vision', 'work-rate', 'acceleration', 'agility', 'balance', 'jumping-reach', 'natural-fitness',
    'pace', 'stamina', 'strength', 'free-kick-taking', 'penalty-taking', 'technique', 'corners', 'crossing', 'dribbling',
    'finishing', 'heading', 'long-shots', 'long-throws', 'marking', 'tackling'
]

# CSV dosyasını oluşturma ve yazma
player_id_counter = 1  # player_id için sayaç
with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(header)  # Header satırını yazma

    for player in players_raw:
        footballer_id = player['footballer_id']
        player_name = player['footballer_name']

        try:
            # Ana URL'ye git
            driver.get(main_url)
            time.sleep(1)  # Sayfanın yüklenmesi için bekleme

            # Oyuncu ismini yazıp arama yap
            input_element = driver.find_elements(By.CLASS_NAME, 'option')[1].find_element(By.NAME, 'name')
            input_element.clear()
            input_element.send_keys(player_name)
            input_element.send_keys(Keys.RETURN)  # "Enter" tuşuna basılıyor

            # Sayfa yüklenene kadar bekleme
            time.sleep(1)

            # Oyuncuların linklerini al
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            player_links = soup.find_all('a', title=True)

            # Şimdi, tam isim eşleşmesi yapan futbolcuyu bulalım
            for player_link in player_links:
                # Eğer futbolcu adı tam olarak eşleşiyorsa (case-insensitive ve unidecode ile)
                if unidecode(player_name.strip().lower()) == unidecode(player_link['title'].strip().lower()):
                    player_detail_url = base_url + player_link['href']
                    print(f"Player Name: {player_link['title']}")
                    print(f"Player Detail URL: {player_detail_url}")

                    # Detay sayfasına git
                    driver.get(player_detail_url)
                    time.sleep(1)

                    # Detay sayfasını işlemek için BeautifulSoup kullanabilirsiniz
                    player_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Player info kısmını al
                    player_info = player_soup.find('div', id='main_body').find('div', id='player_info').find('div', id='player')

                    h3_elements = player_soup.find_all('h3')

                    # Rating, Potential, Position gibi bilgileri al
                    rating = player_info.find('div', class_='meta').find('span', id='ability').text.strip() if player_info.find('div', class_='meta').find('span', id='ability') else '0'
                    potential = player_info.find('div', class_='meta').find('span', id='potential').text.strip() if player_info.find('div', class_='meta').find('span', id='potential') else '0'
                    position_acronym = player_info.find('ul').find_all('li')[-1].find('span', class_='desktop_positions').text.strip() if player_info.find('ul') else '0'

                    # Diğer teknik ve fiziksel istatistikler
                    stats = {}

                    for h3 in h3_elements:
                        title = h3.text.split()[0].lower()  # Başlığı küçük harfe çevir
                        stat_value = h3.find('span', class_='stat')  # 'stat' sınıfına sahip span'ı bul
                        if stat_value:
                            stats[title] = stat_value.text.strip()  # İlgili statiyi kaydet

                    # Stat bilgilerini çekmek için döngü
                    stat_sections = player_soup.find_all('tr')  # Tüm tr elementlerini al

                    for stat_section in stat_sections:
                        stat_id = stat_section.get('id')

                        if stat_id:
                            stat_value = stat_section.find('td', class_='stat')

                            if stat_value:
                                stat_text = stat_value.text.strip()  # Stat değerini al
                                stats[stat_id] = stat_text  # Sözlüğe ekle
                            else:
                                stats[stat_id] = '0'  # Değer yoksa 0 olarak ekle

                    # Sonuçları yazdır
                    print(stats)

                    # Veriyi CSV'ye yazma
                    row = [player_id_counter, footballer_id, player_name, rating, potential, position_acronym]
                    for stat in header[6:]:  # Header'daki istatistikleri ekle
                        stat_value = stats.get(stat, '0')  # Eğer stat değeri yoksa 0 ekle
                        row.append(stat_value)

                    writer.writerow(row)
                    player_id_counter += 1  # player_id'yi artır

        except Exception as e:
            print(f"Error processing player {player_name}: {e}")
            continue

driver.quit()
print(f"Data extracted and saved to {csv_filename}")
