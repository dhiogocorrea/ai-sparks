import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

BASE_URL = 'https://www.jamendo.com'
OUTPUT_DIR = 'track_data'

class JamendoCrawler:
    def __init__(self):
        self.driver = None
        self.start_driver()

    def start_driver(self):
        if not self.driver:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_genres(self):
        genres = []
        try:
            self.driver.get(BASE_URL + '/start')
            # Wait for the select element to be present
            select_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "select_genre"))
            )
            
            # Get all option elements
            options = select_element.find_elements(By.TAG_NAME, "option")
            genres = [option.get_attribute('value') for option in options if option.get_attribute('value')]
            genres = [genre for genre in genres if 'Todos' not in genre]
        except Exception as e:
            print(f"Error getting genres: {str(e)}")
        
        return genres

    def get_genre_page(self, genre):
        try:
            url = f"{BASE_URL}/community/{genre}/tracks"
            self.driver.get(url)
            
            # Wait for track elements to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "track.js-trackrow-trackrow"))
            )
            
            return self.driver.page_source
        except Exception as e:
            print(f"Error getting genre page {genre}: {str(e)}")
            return None

    def get_track_details(self, url, genre):
        try:
            self.driver.get(url)
            
            # Wait for title to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "primary"))
            )
            
            # Extract information - now getting the nested span for title
            title = self.driver.find_element(By.CSS_SELECTOR, "h1.primary > span").text.strip()
            
            # Get artist from the nested structure
            artist = self.driver.find_element(By.CSS_SELECTOR, "a.secondary > span").text.strip()
            
            # Album might not always be present
            try:
                album = self.driver.find_element(By.CLASS_NAME, "source-link").text.strip()
            except:
                album = "Unknown Album"
            
            album = album.replace("Do álbum: ", "")
            
            # Get tags
            tags = []
            try:
                tags_ul = self.driver.find_element(By.CLASS_NAME, "tags")
                tag_elements = tags_ul.find_elements(By.TAG_NAME, "li")
                tags = [tag.text.strip() for tag in tag_elements]
            except:
                tags = []
            
            return {
                "genre": genre,
                "title": title,
                "artist": artist,
                "album_name": album,
                "tags": tags,
                "url": url
            }
        except Exception as e:
            print(f"Error getting track details for {url}: {str(e)}")
            return None

    def download_mp3(self, track_url, output_dir='assets'):
        try:
            self.driver.get(track_url)
            
            # Wait for meta tag to be present and get its content
            audio_meta = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="og:audio:secure_url"]'))
            )
            
            audio_url = audio_meta.get_attribute('content')
            if not audio_url:
                print(f"No audio URL found for {track_url}")
                return None
            
            # Create downloads directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract track ID from URL for filename
            track_id = track_url.split('/')[-1]
            output_file = os.path.join(output_dir, f"{track_id}.mp3")
            
            # Set headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': track_url,
                'Connection': 'keep-alive',
            }
            
            # Download the audio file with headers
            response = requests.get(
                audio_url,
                headers=headers,
                stream=True
            )
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte
                
                with open(output_file, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
                        
                print(f"Successfully downloaded: {output_file}")
                return output_file
            else:
                print(f"Failed to download audio: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error downloading MP3 from {track_url}: {str(e)}")
            import traceback
            traceback.print_exc()  # Print full error trace for debugging
            return None

    def extract_track_links(self, html_content):
        track_links = []
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all li elements with class 'track js-trackrow-trackrow'
        track_elements = soup.find_all('li', class_='track js-trackrow-trackrow')
        
        for track_element in track_elements:
            # Find the first anchor tag within the track element
            track_link = track_element.find('a')
            if track_link and track_link.get('href'):
                # Make sure we have the full URL
                href = track_link['href']
                if not href.startswith('http'):
                    href = f"{BASE_URL}{href}"
                track_links.append(href)
        
        return track_links

def save_json(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    crawler = JamendoCrawler()
    try:
        crawler.start_driver()
        
        # Test downloading a single track
        test_url = "https://www.jamendo.com/track/1900662/mineral"
        downloaded_file = crawler.download_mp3(test_url)
        if downloaded_file:
            print(f"Test download successful: {downloaded_file}")
        
        # Comment out or remove the test above and uncomment the below code to run the full crawler
        """
        genres = crawler.get_genres()
        print(f"Found genres: {genres}")
        
        all_tracks = []
        
        for genre in genres:
            print(f"\nProcessing genre: {genre}")
            content = crawler.get_genre_page(genre)
            genre_tracks = []
            
            if content:
                track_links = crawler.extract_track_links(content)
                print(f"Found {len(track_links)} tracks for {genre}")
                
                for i, track_url in enumerate(track_links, 1):
                    print(f"Processing track {i}/{len(track_links)} for {genre}")
                    track_data = crawler.get_track_details(track_url, genre)
                    if track_data:
                        genre_tracks.append(track_data)
                        all_tracks.append(track_data)
                
                # Save genre-specific data
                save_json(genre_tracks, f"{genre}.json")
            else:
                print(f"Failed to fetch page for {genre}")
        """
    
    finally:
        crawler.close_driver()