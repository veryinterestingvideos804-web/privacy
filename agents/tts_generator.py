import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

from groq import Groq
import requests

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"


class TTSGenerator:
    def __init__(self, api_key: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger("TTSGenerator")

        if self.provider == "groq":
            if not self.api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.api_key)
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def generate_voice_and_subs(self, script_data: dict, style: str) -> dict:
        self.logger.info("Rozpoczynam generowanie treści TTS i napisów.")
        script_text = json.dumps(script_data, indent=2, ensure_ascii=False)

        system_prompt = f"""
        Jesteś inżynierem dźwięku i specjalistą ds. postprodukcji wideo.
        Twoim zadaniem jest przetworzenie poniższego scenariusza i przygotowanie paczki danych do syntezy mowy (TTS) oraz napisów.

        Scenariusz:
        {script_text}

        Styl wideo: {style}

        Wymagania:
        1. 'clean_narration': Połącz narrację ze wszystkich segmentów (w tym CTA) w jeden, czysty tekst dla lektora AI. Usuń znaki specjalne, nawiasy i didaskalia.
        2. 'srt_content': Wygeneruj poprawny plik napisów SRT. Przekonwertuj czasy na format 00:00:00,000 --> 00:00:05,000.
        3. 'tts_config': Zaproponuj parametry TTS: język pl, głos, speed, tone.

        MUSISZ ZWRÓCIĆ DANE W FORMACIE JSON. 
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Wygeneruj czysty tekst do TTS, konfigurację TTS oraz plik SRT."}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        result_json = response.choices[0].message.content
        parsed_data = json.loads(result_json)
        self.logger.info("Wygenerowano dane TTS i SRT.")
        return parsed_data

    def synthesize_audio(self, clean_narration: str, tts_config: dict, output_path: str = "voice.mp3") -> Optional[str]:
        self.logger.info("Rozpoczynam generowanie pliku audio lektora AI.")

        voice = tts_config.get("voice", "Adam")
        speed = tts_config.get("speed", 1.0)
        language = tts_config.get("language", "pl")

        eleven_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Jeśli brak klucza ElevenLabs, używaj pyttsx3 (darmowy, offline)
        if not eleven_api_key and HAS_PYTTSX3:
            return self._synthesize_with_pyttsx3(clean_narration, voice, speed, output_path)
        elif not eleven_api_key:
            self.logger.warning("Brak ELEVENLABS_API_KEY i pyttsx3. Zainstaluj: pip install pyttsx3")
            return None

        headers = {
            "xi-api-key": eleven_api_key,
            "Content-Type": "application/json"
        }

        body = {
            "text": clean_narration,
            "voice": voice,
            "model": "eleven_multilingual_v1",
            "voice_settings": {
                "stability": 0.6,
                "similarity_boost": 0.7
            }
        }

        response = requests.post(
            f"{ELEVENLABS_TTS_URL}/{voice}/stream",
            headers=headers,
            json=body,
            timeout=120
        )

        if response.status_code != 200:
            self.logger.warning(f"Błąd ElevenLabs TTS: {response.status_code} {response.text}")
            return None

        path = Path(output_path)
        path.write_bytes(response.content)
        self.logger.info(f"Zapisano audio TTS jako {output_path}")
        return str(path)

    def _synthesize_with_pyttsx3(self, text: str, voice_name: str, speed: float, output_path: str) -> Optional[str]:
        """Generuj audio używając pyttsx3 (całkowicie darmowe, offline)"""
        try:
            engine = pyttsx3.init()
            
            # Ustaw język na polski
            engine.setProperty('rate', int(150 * speed))  # Prędkość mowy
            engine.setProperty('volume', 0.9)  # Głośność (0.0 - 1.0)
            
            # Ustaw głos (jeśli dostępny)
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'polish' in voice.name.lower() or voice.languages and 'pl' in voice.languages:
                    engine.setProperty('voice', voice.id)
                    break
            
            # Zapisz do pliku MP3
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            self.logger.info(f"✅ Wygenerowano audio pyttsx3 jako {output_path} (OFFLINE, DARMOWE)")
            return str(Path(output_path))
        except Exception as e:
            self.logger.error(f"Błąd pyttsx3: {e}")
            return None
