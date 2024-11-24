from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

url = "https://www.transfermarkt.us/super-lig/startseite/wettbewerb/TR1"

# WebDriver başlatılıyor
driver = webdriver.Chrome()

driver.get(url)

wait = WebDriverWait(driver, 10)

# Sayfanın yüklenmesini bekle
time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekle

# Sayfa içeriği BeautifulSoup ile analiz ediliyor
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Takımların bulunduğu tüm satırları alıyoruz
teams = soup.find_all('tr', class_=['odd', 'even'])

# Takımların sayısını yazdıralım
print(len(teams))

# CSV dosyasını açıyoruz
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)  # Eğer 'data/raw_data' dizini yoksa oluşturuyoruz

csv_filename = os.path.join(csv_dir, "super_league.csv")

with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    # Başlıkları yazıyoruz
    header = ['league', 'league_id', 'team_name', 'team_info_link', 'img_path', 'num_players', 'avg_age', 'num_legionnaires', 'avg_marketing_val', 'total_squad_value']
    writer.writerow(header)

    # Her bir takım için bilgileri alıyoruz
    for team in teams:
        try:
            league = 'Super League'
            league_id = 'tr1'

            # Team name
            team_name = team.find('td', class_='hauptlink no-border-links').a.text.strip('()')

            # Team info link
            team_info_link = team.find('td', class_='hauptlink no-border-links').a['href']

            # Team image path
            img_path = team.find('img', class_='tiny_wappen')['src']

            # num_players, avg_age, num_legionnaires, avg_marketing_val, total_squad_value
            # Bu bilgileri almak için td etiketlerinin doğru sırasını takip etmelisiniz
            tds = team.find_all('td', class_='zentriert')  # zentriert sınıfı ile td'leri çekiyoruz

            if len(tds) >= 3:
                num_players = tds[0].text.strip()  # İlk td, oyuncu sayısı
                avg_age = tds[1].text.strip()      # İkinci td, ortalama yaş
                num_legionnaires = tds[2].text.strip()  # Üçüncü td, yabancı oyuncu sayısı
            else:
                num_players = avg_age = num_legionnaires = 'N/A'

            # Avg marketing value ve total squad value için doğru td sınıflarını kullanıyoruz
            financial_tds = team.find_all('td', class_='rechts')  # finansal bilgileri içeren td'ler

            if len(financial_tds) >= 2:
                avg_marketing_val = financial_tds[0].text.strip()  # Ortalama pazarlama değeri
                total_squad_value = financial_tds[1].a.text.strip('()')  # Takım toplam değeri
            else:
                avg_marketing_val = total_squad_value = 'N/A'

            # Verileri CSV dosyasına yazıyoruz
            writer.writerow([league, league_id, team_name, team_info_link, img_path, num_players, avg_age, num_legionnaires, avg_marketing_val, total_squad_value])

        except AttributeError as e:
            # Veri çekilemezse hatayı atlayın
            print(f"Error processing team: {e}")
            continue

# Tarayıcıyı kapatıyoruz
driver.quit()

# İşlem tamamlandığında mesaj yazdırıyoruz
print(f"Data extracted and saved to {csv_filename}")
