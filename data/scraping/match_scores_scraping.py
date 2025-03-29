from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import traceback
import os

# Initialize the WebDriver
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

# Updated list of URLs to scrape (first two URLs for each league removed)
urls = [
    "https://www.sofascore.com/tournament/football/turkey/trendyol-super-lig/52#id:42632",
    "https://www.sofascore.com/tournament/football/turkey/trendyol-super-lig/52#id:53190",
    "https://www.sofascore.com/tournament/football/turkey/trendyol-super-lig/52#id:63814",
    "https://www.sofascore.com/tournament/football/turkey/trendyol-1lig/98#id:42678",
    "https://www.sofascore.com/tournament/football/turkey/trendyol-1lig/98#id:53276",
    "https://www.sofascore.com/tournament/football/turkey/trendyol-1lig/98#id:64425",
    "https://www.sofascore.com/tournament/football/poland/ekstraklasa/202#id:42004",
    "https://www.sofascore.com/tournament/football/poland/ekstraklasa/202#id:52176",
    "https://www.sofascore.com/tournament/football/poland/ekstraklasa/202#id:61236"
]

# Create directory structure and prepare CSV file
csv_dir = os.path.join('data', 'raw_data')
os.makedirs(csv_dir, exist_ok=True)
csv_filename = os.path.join(csv_dir, "matches_scores.csv")

# Updated seasons list (now starting from the third season)
seasons = ["22/23", "23/24", "24/25"]

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
            
            # Determine the league name based on URL index
            if index < 3:
                league = "Süper Lig"
            elif index < 6:
                league = "1.Lig"
            else:
                league = "PKO BP Ekstraklasa"
            
            # Determine season based on position in group of 3
            season_index = index % 3
            season = seasons[season_index]
            
            print(f"League: {league}, Season: {season}")
            # Find all dropdown buttons with the class "DropdownButton jQruaf"
            print("Finding dropdown buttons...")
            dropdown_buttons = driver.find_elements(By.CSS_SELECTOR, "button.DropdownButton.jQruaf")
            print(f"Found {len(dropdown_buttons)} dropdown buttons.")
            
            # Check if there are at least 3 dropdown buttons (index 2)
            if len(dropdown_buttons) > 2:
                # Click the 3rd dropdown button (index 2)
                print("Clicking the 3rd dropdown button...")
                dropdown_buttons[2].click()
                
                # Wait for the dropdown to open
                print("Waiting for the dropdown to open...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Box.hUgaAu"))
                )
                print("Dropdown opened successfully.")
                
                # Find all round elements
                print("Finding round elements...")
                rounds = driver.find_elements(By.CSS_SELECTOR, "li.DropdownItem.hXhsNJ, li.DropdownItem.gMqEua, li.DropdownItem.jdEvQI")
                print(f"Found {len(rounds)} rounds.")
                
                for i in range(len(rounds)):
                    try:
                        # Reopen dropdown if needed
                        if i > 0:
                            dropdown_buttons = driver.find_elements(By.CSS_SELECTOR, "button.DropdownButton.jQruaf")
                            if len(dropdown_buttons) > 2:
                                dropdown_buttons[2].click()
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Box.hUgaAu"))
                                )
                        
                        # Get all rounds again as elements might have changed
                        rounds = driver.find_elements(By.CSS_SELECTOR, "li.DropdownItem.hXhsNJ, li.DropdownItem.gMqEua, li.DropdownItem.jdEvQI")
                        if i >= len(rounds):
                            break
                            
                        round_element = rounds[i]
                        round_name = round_element.text
                        print(f"Processing round: {round_name}")
                        round_element.click()
                        
                        # Wait for the matches to load
                        print("Waiting for matches to load...")
                        time.sleep(2)
                        
                        # Parse the page content
                        print("Parsing page content...")
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        # Extract matches
                        matches = soup.find_all('a', {'class': 'sc-3f813a14-0'})
                        print(f"Found {len(matches)} matches.")
                        for match in matches:
                            try:
                                # Extract date
                                date_element = match.find('bdi', {'data-testid': 'event_time'})
                                date = date_element.text.strip() if date_element else "-"
                                
                                # Extract home team
                                home_team_element = match.find('div', {'data-testid': 'left_team'})
                                home_team = home_team_element.find('bdi').text.strip() if home_team_element else "-"
                                
                                # Extract away team
                                away_team_element = match.find('div', {'data-testid': 'right_team'})
                                away_team = away_team_element.find('bdi').text.strip() if away_team_element else "-"
                                
                                # Initialize default values for scores
                                home_goals = "-"
                                away_goals = "-"
                                
                                # Try to extract home goals if available
                                home_score_element = match.find('div', {'data-testid': 'left_score'})
                                if home_score_element:
                                    home_goals_element = home_score_element.find('span')
                                    if home_goals_element:
                                        home_goals = home_goals_element.text.strip()
                                
                                # Try to extract away goals if available
                                away_score_element = match.find('div', {'data-testid': 'right_score'})
                                if away_score_element:
                                    away_goals_element = away_score_element.find('span')
                                    if away_goals_element:
                                        away_goals = away_goals_element.text.strip()
                                # Write to CSV
                                writer.writerow([league, round_name, date, home_team, home_goals, away_team, away_goals, season])
                                
                            except Exception as e:
                                print(f"Error extracting match data: {e}")
                                print(f"Match HTML: {match}")
                                # Write basic info even if there's an error
                                writer.writerow([league, round_name, "-", "-", "-", "-", "-", season])
                                continue
                    except Exception as e:
                        print(f"Error processing round index {i}")
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