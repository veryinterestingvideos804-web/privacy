import json
import logging
import time

from groq import Groq

class AssetsCollector:
    def __init__(self, api_key: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger("AssetsCollector")

        if self.provider == "groq":
            if not self.api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.api_key)
            self.mode = "groq"
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def collect_assets(self, script_data: dict) -> dict:
        self.logger.info("Rozpoczęcie dobierania materiałów wideo/graficznych do scenariusza.")
        
        # Przygotowanie czytelnego dla LLM zrzutu scenariusza
        segments_text = json.dumps(script_data, indent=2, ensure_ascii=False)

        system_prompt = f"""
        Jesteś dyrektorem artystycznym i reżyserem montażu krótkich form wideo (Shorts/Reels/TikTok).
        Twoim zadaniem jest przeanalizowanie poniższego scenariusza i dobranie idealnych materiałów stockowych (wideo, obrazy, animacje) dla KAŻDEGO segmentu oraz segmentu CTA.
        
        Scenariusz:
        {segments_text}
        
        Wymagania dotyczące dopasowania:
        1. Dla każdego segmentu zdefiniuj: typ zasobu, sugerowane źródło (np. Pexels, Pixabay, Unsplash, stock) oraz instrukcję pobierania.
        2. WAŻNE: Zapytanie wyszukiwania ('search_query') MUSI być napisane w języku angielskim, aby poprawnie działało w darmowych bazach Pexels/Pixabay. Zapytanie powinno być precyzyjne (np. 'dark moody forest fog aerial shot 4k', zamiast 'las').
        3. Styl wizualny musi być spójny i odpowiadać tonowi całego filmu.
        
        MUSISZ ZWRÓCIĆ DANE W FORMACIE JSON. Struktura wyjściowa musi wyglądać dokładnie tak:
        {{
          "assets": [
            {{
              "segment_index": 0,
              "asset_type": "video | image | animation | text_graphic",
              "source": "Pexels | Pixabay | Unsplash | custom",
              "search_query": "precyzyjne zapytanie po angielsku",
              "download_instructions": "np. Szukaj klipu w pionie (9:16), czas min 5s"
            }}
          ],
          "cta_asset": {{
            "asset_type": "video | image | animation | text_graphic",
            "source": "Pexels | Pixabay | Unsplash | custom",
            "search_query": "zapytanie po angielsku dla tła pod CTA",
            "download_instructions": "instrukcja"
          }}
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Przygotuj listę materiałów w formacie JSON."}
                ],
                response_format={ "type": "json_object" },
                temperature=0.5 # Niższa temperatura = bardziej logiczne i trafne tagi wyszukiwania
            )
            
            result_json = response.choices[0].message.content
            parsed_data = json.loads(result_json)
            
            self.logger.info("Pomyślnie dobrano materiały wideo.")
            return parsed_data

        except Exception as e:

            self.logger.error(f"Błąd podczas dobierania materiałów: {e}")
            return None