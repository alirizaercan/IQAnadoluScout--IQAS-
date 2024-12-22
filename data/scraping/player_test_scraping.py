from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import csv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class PlayerScraper:
    def __init__(self, base_url='https://fminside.net'):
        self.base_url = base_url
        self.main_url = f'{base_url}/players'
        self.setup_driver()
        
    def setup_driver(self):
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def load_players_from_csv(self, filepath):
        try:
            players = []
            with open(filepath, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    players.append({'footballer_id': row[0], 'footballer_name': row[1]})
            return players
        except FileNotFoundError:
            logging.error(f"File not found: {filepath}")
            raise
            
    def wait_for_element(self, by, value, timeout=10):
        try:
            element = self.wait.until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.warning(f"Timeout waiting for element: {value}")
            return None
            
    def search_player(self, player_name):
        retries = 3
        for attempt in range(retries):
            try:
                self.driver.get(self.main_url)
                input_element = self.wait_for_element(By.NAME, 'name')
                if input_element:
                    input_element.clear()
                    input_element.send_keys(player_name)
                    input_element.send_keys(Keys.RETURN)
                    time.sleep(2)
                    return True
            except Exception as e:
                logging.warning(f"Search attempt {attempt + 1} failed for {player_name}: {str(e)}")
                if attempt == retries - 1:
                    logging.error(f"All search attempts failed for {player_name}")
                    return False
                time.sleep(2)
                
    def extract_player_stats(self, soup):
        stats = {
            'goalkeeping': '0', 'mental': '0', 'physical': '0', 'technical': '0',
            'aerial_reach': '0', 'command_of_area': '0', 'communication': '0',
            'eccentricity': '0', 'first_touch': '0', 'handling': '0',
            'kicking': '0', 'one_on_ones': '0', 'passing': '0',
            'punching_tendency': '0', 'reflexes': '0', 'rushing_out_tendency': '0',
            'throwing': '0', 'aggression': '0', 'anticipation': '0',
            'bravery': '0', 'composure': '0', 'concentration': '0',
            'decisions': '0', 'determination': '0', 'flair': '0',
            'leadership': '0', 'off_the_ball': '0', 'positioning': '0',
            'teamwork': '0', 'vision': '0', 'work_rate': '0',
            'acceleration': '0', 'agility': '0', 'balance': '0',
            'jumping_reach': '0', 'natural_fitness': '0', 'pace': '0',
            'stamina': '0', 'strength': '0', 'free_kick_taking': '0',
            'penalty_taking': '0', 'technique': '0', 'corners': '0',
            'crossing': '0', 'dribbling': '0', 'finishing': '0',
            'heading': '0', 'long_shots': '0', 'long_throws': '0',
            'marking': '0', 'tackling': '0'
        }
        
        try:
            player_info = soup.find('div', id='player_info')
            if not player_info:
                return stats
                
            # Basic info
            meta = player_info.find('div', class_='meta')
            if meta:
                stats['rating'] = meta.find('span', id='ability').text.strip() if meta.find('span', id='ability') else '0'
                stats['potential'] = meta.find('span', id='potential').text.strip() if meta.find('span', id='potential') else '0'
            
            # Position
            position_element = soup.find('li', class_='position')
            stats['position_acronym'] = position_element.find('span', class_='value').text.strip() if position_element else '0'
            
            # Detailed stats
            stat_sections = soup.find_all('tr', id=True)
            for section in stat_sections:
                stat_id = section.get('id')
                stat_value = section.find('td', class_='stat')
                if stat_value:
                    # Convert stat_id to match header format (replace hyphens with underscores)
                    cleaned_stat_id = stat_id.replace('-', '_')
                    stats[cleaned_stat_id] = stat_value.text.strip()
                    
            return stats
        except Exception as e:
            logging.error(f"Error extracting stats: {str(e)}")
            return stats
            
    def scrape_players(self, input_file, output_file):
        players = self.load_players_from_csv(input_file)
        
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=self.get_header())
            writer.writeheader()
            
            for idx, player in enumerate(players, 1):
                try:
                    if not self.search_player(player['footballer_name']):
                        continue
                        
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    player_links = soup.find_all('a', title=True)
                    
                    for link in player_links:
                        if player['footballer_name'].lower() in link['title'].lower():
                            player_url = self.base_url + link['href']
                            logging.info(f"Processing {link['title']} at {player_url}")
                            
                            self.driver.get(player_url)
                            time.sleep(2)
                            
                            player_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                            stats = self.extract_player_stats(player_soup)
                            
                            row_data = {
                                'player_id': idx,
                                'footballer_id': player['footballer_id'],
                                'footballer_name': player['footballer_name'],
                                **stats
                            }
                            writer.writerow(row_data)
                            logging.info(f"Successfully processed {player['footballer_name']}")
                            
                except Exception as e:
                    logging.error(f"Error processing {player['footballer_name']}: {str(e)}")
                    continue
                    
    @staticmethod
    def get_header():
        return [
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
            'technique', 'corners', 'crossing', 'dribbling', 'finishing',
            'heading', 'long_shots', 'long_throws', 'marking', 'tackling'
        ]
        
    def cleanup(self):
        self.driver.quit()

if __name__ == "__main__":
    try:
        input_path = os.path.abspath("data/processed_data/players_raw.csv")
        output_dir = os.path.join('data', 'raw_data')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "players_urls.csv")
        
        scraper = PlayerScraper()
        scraper.scrape_players(input_path, output_path)
        
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
    finally:
        scraper.cleanup()