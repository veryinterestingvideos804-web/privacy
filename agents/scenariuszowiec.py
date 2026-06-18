import json
import logging
import time

from groq import Groq

class Scenariuszowiec:
    def __init__(self, api_key: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger("Scenariuszowiec")

        if self.provider == "groq":
            if not self.api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.api_key)
            self.mode = "groq"
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def generate_script(self, style: str, duration: int, selected_idea: dict) -> dict:
        self.logger.info(f"Generowanie skryptu dla tematu: {selected_idea.get('title')}")
        
        # Pobieranie danych z wybranego pomysłu
        title = selected_idea.get('title', '')
        hook = selected_idea.get('hook', '')
        description = selected_idea.get('description', '')

        system_prompt = f"""
        Jesteś wybitnym scenarzystą krótkich form wideo (Shorts/Reels/TikTok).
        Twoim zadaniem jest napisanie kompletnego skryptu w formie storyboardu na podstawie poniższego pomysłu:
        
        - Tytuł: {title}
        - Hook (wstęp): {hook}
        - Opis: {description}
        
        Styl kanału: {style}
        Czas trwania filmu: do {duration} sekund.
        
        Podziel film na segmenty 5–10 sekund. 
        Zadbaj o płynne przejścia, zatrzymanie uwagi widza oraz wezwanie do działania (CTA) na samym końcu.
        
        MUSISZ ZWRÓCIĆ DANE W FORMACIE JSON. Struktura wyjściowa musi wyglądać dokładnie tak:
        {{
          "segments": [
            {{
              "timeframe": "np. 0-5s",
              "narration": "dokładny tekst do przeczytania przez lektora (TTS)",
              "visual": "szczegółowy opis obrazu/klipu do dobrania",
              "audio_notes": "sugestia muzyki, tempa lub efektów dźwiękowych SFX"
            }}
          ],
          "cta_segment": {{
            "timeframe": "np. 50-60s",
            "narration": "tekst wezwania do działania (np. Subskrybuj po więcej!)",
            "visual": "opis wizualny CTA (np. animacja przycisku subskrypcji)"
          }}
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Napisz szczegółowy skrypt w formacie JSON."}
                ],
                response_format={ "type": "json_object" },
                temperature=0.7 
            )
            
            result_json = response.choices[0].message.content
            parsed_data = json.loads(result_json)
            
            self.logger.info("Pomyślnie wygenerowano scenariusz.")
            return parsed_data

        except Exception as e:
            self.logger.error(f"Błąd podczas generowania scenariusza: {e}")
            return None