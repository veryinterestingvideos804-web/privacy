import json
import os
import requests
from dotenv import load_dotenv

def fetch_videos_from_pexels():
    # 1. Wczytanie kluczy z pliku .env
    load_dotenv()
    pexels_api_key = os.getenv("PEXELS_API_KEY")
    
    if not pexels_api_key:
        print("BŁĄD: Brak klucza PEXELS_API_KEY w pliku .env")
        return

    # 2. Wczytanie wygenerowanego stanu filmu
    state_file = 'current_video_state.json'
    if not os.path.exists(state_file):
        print(f"Plik {state_file} nie istnieje. Najpierw uruchom main.py!")
        return

    with open(state_file, 'r', encoding='utf-8') as f:
        video_data = json.load(f)

    # Upewniamy się, że mamy assety
    assets = video_data.get("assets", {}).get("assets", [])
    if not assets:
        print("Brak zdefiniowanych materiałów wideo w pliku JSON.")
        return

    print("🎥 Szukanie materiałów wideo w bazie Pexels...\n")

    # 3. Iteracja po każdym segmencie ze scenariusza
    headers = {"Authorization": pexels_api_key}
    
    for asset in assets:
        query = asset.get("search_query")
        segment_idx = asset.get("segment_index")
        
        # Pexels API Endpoint dla wideo
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("videos"):
                # Pobieramy link do pierwszego wideo (najwyższa jakość)
                video_files = data["videos"][0]["video_files"]
                best_quality_link = video_files[0]["link"]
                
                print(f"✅ Segment {segment_idx} | Zapytanie: '{query}'")
                print(f"   👉 Znaleziono link: {best_quality_link}\n")
                
                # Tutaj w przyszłości dodasz kod pobierający plik na dysk
                # np. za pomocą urllib.request.urlretrieve(best_quality_link, f"video_{segment_idx}.mp4")
            else:
                print(f"⚠️ Segment {segment_idx} | Brak wyników dla: '{query}'\n")
                
        except requests.exceptions.RequestException as e:
            print(f"Błąd połączenia z Pexels dla zapytania '{query}': {e}")

if __name__ == "__main__":
    fetch_videos_from_pexels()