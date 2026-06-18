import json
import logging
import time

from groq import Groq

class VoiceSubtitlesGenerator:
    def __init__(self, api_key: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger("VoiceSubtitlesGenerator")

        if self.provider == "groq":
            if not self.api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.api_key)
            self.mode = "groq"
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def generate_voice_and_subs(self, script_data: dict, style: str) -> dict:
        self.logger.info("Rozpoczęcie przetwarzania tekstu lektorskiego i generowania napisów SRT.")
        
        # Przygotowanie zrzutu skryptu dla modelu
        script_text = json.dumps(script_data, indent=2, ensure_ascii=False)

        system_prompt = f"""
        Jesteś inżynierem dźwięku i specjalistą ds. postprodukcji wideo. 
        Twoim zadaniem jest przetworzenie poniższego scenariusza i przygotowanie paczki danych do syntezy mowy (TTS) oraz napisów.
        
        Scenariusz:
        {script_text}
        
        Styl wideo: {style}
        
        Wymagania:
        1. 'clean_narration': Połącz narrację ze wszystkich segmentów (w tym CTA) w jeden, czysty tekst dla lektora AI. Usuń wszelkie znaki specjalne, nawiasy, didaskalia. Tekst ma być gotowy do bezpośredniego przeczytania.
        2. 'srt_content': Wygeneruj poprawny, kompletny plik napisów w formacie SRT. Przekonwertuj uproszczone czasy (np. 0-5s, 5-12s) na oficjalny format SRT (00:00:00,000 --> 00:00:05,000). Pamiętaj o numeracji bloków i pustych liniach separujących sekcje SRT. Wszystkie linie wewnątrz formatu SRT muszą być poprawnie odseparowane znakami nowej linii '\\n'.
        3. 'tts_config': Zaproponuj najlepsze parametry dla syntezatora mowy (np. ElevenLabs/OpenAI TTS) pasujące do stylu '{style}'.
        
        MUSISZ ZWRÓCIĆ DANE W FORMACIE JSON. Struktura wyjściowa musi wyglądać dokładnie tak:
        {{
          "tts_config": {{
            "language": "pl",
            "voice": "Nazwa sugerowanego głosu (np. Adam, Antoni, Rachel, Onyx)",
            "speed": 1.0,
            "tone": "krótki opis barwy i emocji (np. głęboki, kinowy, dynamiczny, tajemniczy)"
          }},
          "clean_narration": "Pełny, połączony i oczyszczony tekst dla lektora...",
          "srt_content": "1\\n00:00:00,000 --> 00:00:05,000\\nTekst pierwszego segmentu\\n\\n2\\n00:00:05,000 --> 00:00:10,000\\nTekst drugiego segmentu..."
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Wygeneruj czysty tekst, konfigurację TTS oraz plik SRT."}
                ],
                response_format={ "type": "json_object" },
                temperature=0.3 # Niska temperatura dla sztywnego trzymania się struktur czasu i formatu SRT
            )
            
            result_json = response.choices[0].message.content
            parsed_data = json.loads(result_json)
            
            self.logger.info("Pomyślnie wygenerowano napisy SRT oraz tekst dla lektora.")
            return parsed_data

        except Exception as e:

            self.logger.error(f"Błąd podczas generowania głosu i napisów: {e}")
            return None