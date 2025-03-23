from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import traceback  # Hata detaylarını almak için

# Initialize the WebDriver
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)

# List of URLs to scrape
urls = [
    "https://www.sofascore.com/tournament/football/turkey/trendyol-super-lig/52#id:63814",
    "https://www.sofascore.com/tournament/football/turkey/trendyol-1lig/98#id:64425",
    "https://www.sofascore.com/tournament/football/poland/ekstraklasa/202#id:61236"
]

# Prepare CSV file for output
csv_filename = "matches_data.csv"
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['League', 'Week', 'Date', 'Home Team', 'Home Goals', 'Away Team', 'Away Goals', 'Season'])

    for index, url in enumerate(urls):
        try:
            print(f"Processing URL: {url}")
            driver.get(url)
            
            # Wait for the page to load
            print("Waiting for the page to load...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sc-3f813a14-0"))
            )
            print("Page loaded successfully.")
            
            # Determine the league name based on the URL index
            if index == 0:
                league = "Super Lig"
            elif index == 1:
                league = "Trendyol 1. Lig"
            elif index == 2:
                league = "Ekstraklasa"
            else:
                league = "Unknown League"  # Fallback for unexpected URLs

            print(f"League: {league}")

            # Find all dropdown buttons with the class "DropdownButton jQruaf"
            print("Finding dropdown buttons...")
            dropdown_buttons = driver.find_elements(By.CLASS_NAME, "DropdownButton.jQruaf")
            print(f"Found {len(dropdown_buttons)} dropdown buttons.")
            
            # Check if there are at least 3 dropdown buttons (index 2)
            if len(dropdown_buttons) > 2:
                # Click the 3rd dropdown button (index 2)
                print("Clicking the 3rd dropdown button...")
                dropdown_buttons[2].click()
                
                # Wait for the dropdown to open
                print("Waiting for the dropdown to open...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "Box.hUgaAu"))
                )
                print("Dropdown opened successfully.")
                
                # Find all round elements
                print("Finding round elements...")
                rounds = driver.find_elements(By.CSS_SELECTOR, "li.DropdownItem.hXhsNJ")
                print(f"Found {len(rounds)} rounds.")
                
                for round_element in rounds:
                    try:
                        round_name = round_element.text
                        print(f"Processing round: {round_name}")
                        round_element.click()
                        
                        # Wait for the matches to load
                        print("Waiting for matches to load...")
                        time.sleep(2)  # Adjust sleep time if necessary
                        
                        # Parse the page content
                        print("Parsing page content...")
                        soup = BeautifulSoup(driver.page_source, 'html.parser')

                        # Extract matches
                        matches = soup.find_all('a', {'class': 'sc-3f813a14-0'})
                        print(f"Found {len(matches)} matches.")
                        for match in matches:
                            try:
                                # Extract date
                                date = match.find('bdi', {'data-testid': 'event_time'}).text.strip()

                                # Extract home team
                                home_team = match.find('div', {'data-testid': 'left_team'}).find('bdi').text.strip()

                                # Extract away team
                                away_team = match.find('div', {'data-testid': 'right_team'}).find('bdi').text.strip()

                                # Extract home goals
                                home_goals = match.find('div', {'data-testid': 'left_score'}).find('span').text.strip()

                                # Extract away goals
                                away_goals = match.find('div', {'data-testid': 'right_score'}).find('span').text.strip()

                                # Assuming the season is part of the URL or can be derived from it
                                season = url.split('#id:')[1]

                                # Write to CSV
                                writer.writerow([league, round_name, date, home_team, home_goals, away_team, away_goals, season])
                            except AttributeError as e:
                                print(f"Error extracting match data: {e}")
                                print(f"Match HTML: {match}")
                                continue
                    except Exception as e:
                        print(f"Error processing round: {round_name}")
                        print(f"Error details: {traceback.format_exc()}")
                        continue
            else:
                print(f"Not enough dropdown buttons found on {url}. Expected at least 3, found {len(dropdown_buttons)}.")
        except Exception as e:
            print(f"Error processing URL: {url}")
            print(f"Error details: {traceback.format_exc()}")
            continue

driver.quit()
print(f"Data extracted and saved to {csv_filename}")