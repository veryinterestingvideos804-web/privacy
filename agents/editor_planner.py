import json
import logging
import time

from groq import Groq

class EditorPlanner:
    def __init__(self, api_key: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger("EditorPlanner")

        if self.provider == "groq":
            if not self.api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.api_key)
            self.mode = "groq"
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def plan_editing(self, global_context: dict, script_data: dict, assets_data: dict, voice_data: dict) -> dict:
        self.logger.info("Rozpoczęcie generowania instrukcji montażowych dla wideo.")
        
        # Przygotowanie paczki danych wejściowych z poprzednich kroków pipeline'u
        pipeline_snapshot = {
            "context": global_context,
            "script": script_data,
            "assets": assets_data,
            "voice_and_subtitles": {
                "clean_narration": voice_data.get("clean_narration"),
                "tts_config": voice_data.get("tts_config")
            }
        }

        system_prompt = f"""
        Jesteś głównym inżynierem automatyzacji wideo i reżyserem technicznym montażu.
        Twoim zadaniem jest przeanalizowanie danych z dotychczasowego potoku i wygenerowanie precyzyjnej instrukcji montażowej (Timeline Manifest) w formacie JSON dla silnika renderującego.
        
        Oto dane wejściowe potoku:
        {json.dumps(pipeline_snapshot, indent=2, ensure_ascii=False)}
        
        Wymagania techniczne:
        1. 'timeline': Stwórz tablicę ujęć odpowiadającą segmentom. Zdefiniuj dokładne czasy start/stop, przypisz do nich asset, zdefiniuj typ cięcia/przejścia (np. 'cut', 'fade_in', 'cross_dissolve') oraz efekty wizualne (np. 'subtle_zoom', 'glitch_effect') i styl animacji napisów (np. 'word_by_word_pop').
        2. 'audio_settings': Dobierz styl muzyki podkładowej (zgodny z tonem kanału) oraz zdefiniuj precyzyjne poziomy głośności w decybelach lub skali procentowej (np. lektor: 1.0, muzyka: 0.15), aby podkład nie zagłuszał głosu.
        3. 'export_settings': Zaproponuj sztywne parametry renderowania w pionie (Shorts/TikTok -> 1080x1920) lub poziomie (1920x1080) w zależności od formatu, klatkaż (30fps lub 60fps) oraz sugerowany bitrate (np. '8 Mbps').
        
        MUSISZ ZWRÓCIĆ DANE W FORMACIE JSON. Struktura wyjściowa musi wyglądać dokładnie tak:
        {{
          "timeline": [
            {{
              "segment_index": 0,
              "start_time_sec": 0.0,
              "end_time_sec": 5.0,
              "assigned_asset_query": "wyszukiwana fraza z kroku 3, ułatwiająca identyfikację pliku",
              "transition_type": "cut | fade | cross_dissolve | none",
              "visual_effects": ["subtle_zoom_in", "color_grade_moody"],
              "text_animation_style": "bounce_popup | standard_subtitles"
            }}
          ],
          "audio_settings": {{
            "background_music_mood": "np. cinematic, dark ambient, upbeat energetic",
            "voiceover_volume_level": 1.0,
            "background_music_volume_level": 0.12,
            "audio_ducking_enabled": true
          }},
          "export_settings": {{
            "format": "mp4",
            "resolution": "1080x1920",
            "fps": 30,
            "target_bitrate": "8-10 Mbps",
            "video_codec": "h264"
          }}
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Wygeneruj techniczny manifest montażowy w formacie JSON."}
                ],
                response_format={ "type": "json_object" },
                temperature=0.4 
            )
            
            result_json = response.choices[0].message.content
            parsed_data = json.loads(result_json)
            
            self.logger.info("Pomyślnie wygenerowano plan montażowy.")
            return parsed_data

        except Exception as e:

            self.logger.error(f"Błąd podczas planowania montażu: {e}")
            return None