from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

main_url = 'https://www.transfermarkt.us'
urls = [
    "https://www.transfermarkt.us/super-lig/startseite/wettbewerb/TR1",  # Süper Lig
    "https://www.transfermarkt.us/pko-ekstraklasa/startseite/wettbewerb/PL1",  # Ekstraklasa
    "https://www.transfermarkt.com.tr/super-lig/startseite/wettbewerb/TR2"  # TFF 1. Lig
]

# WebDriver başlatılıyor
driver = webdriver.Chrome()

# CSV dosyasını oluşturuyoruz
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)
csv_filename = os.path.join(csv_dir, "footballers.csv")

with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    header = ['league_id', 'team_id', 'footballer_id', 'footballer_name', 'club', 'league_name', 'trikot_num',
              'position', 'birthday', 'age', 'nationality_img_path', 'height', 'feet', 'contract', 'market_value', 'footballer_img_path']
    writer.writerow(header)

    team_id = 0
    footballer_id = 0

    for url in urls:
        driver.get(url)
        time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekle

        # Sayfa içeriği BeautifulSoup ile analiz ediliyor
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Lig bilgileri
        league_name = 'Unknown League'
        league_id = 'unknown'
        if "TR1" in url:
            league_name = 'Super League'
            league_id = 'tr1'
        elif "PL1" in url:
            league_name = 'PKO BP Ekstraklasa'
            league_id = 'pl1'
        elif "TR2" in url:
            league_name = 'Trendyol TFF 1. League'
            league_id = 'tr2'

        print(f"Processing URL: {url}, League: {league_name}, League ID: {league_id}")

        # Takım bağlantılarını alıyoruz
        team_links = soup.find_all('td', class_='hauptlink no-border-links')
        for team_tag in team_links:
            try:
                team_name = team_tag.a.text.strip()
                team_path = team_tag.a['href']
                team_url = f"{main_url}{team_path}"
                team_id += 1
                print(f"Processing Team: {team_name}, URL: {team_url}")

                # Takım sayfasına gidiyoruz
                driver.get(team_url)
                time.sleep(3)

                # Detailed sayfasını buluyoruz
                team_soup = BeautifulSoup(driver.page_source, 'html.parser')
                detailed_link_tag = team_soup.find('a', class_='tm-tab', href=lambda x: 'plus/1' in x)
                if not detailed_link_tag:
                    print(f"No detailed link found for {team_name}. Skipping...")
                    continue

                detailed_url = f"{main_url}{detailed_link_tag['href']}"
                print(f"Accessing Detailed Page: {detailed_url}")

                driver.get(detailed_url)
                time.sleep(3)

                detailed_soup = BeautifulSoup(driver.page_source, 'html.parser')
                footballers = detailed_soup.find_all('tr', class_=['odd', 'even'])
                for footballer in footballers:
                    try:
                        footballer_name = footballer.find('td', class_='hauptlink').a.text.strip()
                        trikot_num = footballer.find('div', class_='rn_nummer').text.strip() if footballer.find('div', class_='rn_nummer') else ''
                        position_cell = footballer.find('td', class_='posrela')
                        if position_cell:
                            position = position_cell.find_all('td')[2].text.strip()
                        else:
                            position = "Unknown"
                        birthday_full = footballer.find_all('td', class_='zentriert')[1].text.strip() if footballer.find_all('td', class_='zentriert') else ''
                        birthday = birthday_full.split('(')[0].strip()  # Parantezden önceki kısmı alır
                        age = footballer.find_all('td', class_='zentriert')[1].text.strip()[-3:-1] if footballer.find_all('td', class_='zentriert') else ''
                        nationality_img = footballer.find('img', class_='flaggenrahmen')['src'] if footballer.find('img', class_='flaggenrahmen') else ''
                        height = footballer.find_all('td', class_='zentriert')[3].text.strip() if len(footballer.find_all('td', class_='zentriert')) > 3 else ''
                        feet = footballer.find_all('td', class_='zentriert')[4].text.strip() if len(footballer.find_all('td', class_='zentriert')) > 4 else ''
                        contract = footballer.find_all('td', class_='zentriert')[7].text.strip() if len(footballer.find_all('td', class_='zentriert')) > 7 else ''
                        market_value = footballer.find('td', class_='rechts hauptlink').a.text.strip() if footballer.find('td', class_='rechts hauptlink') else ''
                        footballer_img = footballer.find('img', class_='bilderrahmen-fixed')['src'] if footballer.find('img', class_='bilderrahmen-fixed') else ''

                        footballer_id += 1

                        writer.writerow([league_id, team_id, footballer_id, footballer_name, team_name, league_name,
                                         trikot_num, position, birthday, age, nationality_img, height, feet, contract, market_value, footballer_img])
                    except Exception as e:
                        print(f"Error processing footballer: {e}")
                        continue
            except Exception as e:
                print(f"Error processing team: {e}")
                continue

driver.quit()
print(f"Data extracted and saved to {csv_filename}")
