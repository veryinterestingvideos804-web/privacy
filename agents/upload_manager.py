import json
import logging
import time

from groq import Groq

class UploadManager:
    def __init__(self, api_key: str, provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model = model
        self.logger = logging.getLogger("UploadManager")

        if self.provider == "groq":
            if not self.api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.api_key)
            self.mode = "groq"
            self.model = "llama-3.3-70b-versatile"
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def generate_metadata(self, global_context: dict, selected_idea: dict) -> dict:
        self.logger.info("Rozpoczęcie generowania metadanych SEO dla YouTube.")
        
        system_prompt = f"""
        Jesteś ekspertem SEO dla platformy YouTube i menedżerem kanału.
        Masz przygotować kompletne metadane pod publikację krótkiego filmu (Short/TikTok), którego temat został wybrany wcześniej.
        
        Temat kanału/kontekst: {global_context.get('topic')}
        Styl: {global_context.get('style')}
        Tytuł roboczy: {selected_idea.get('title')}
        Hook z filmu: {selected_idea.get('hook')}
        Słowa kluczowe: {', '.join(selected_idea.get('keywords', []))}
        
        Wymagania:
        1. 'description': Pełny opis na YouTube. Musi zawierać intrygujący nagłówek, krótki zarys treści, mocne Call-to-Action (CTA) do subskrypcji oraz 3-5 dopasowanych hashtagów na samym końcu.
        2. 'tags': Lista najlepszych 8-12 tagów idealnych dla algorytmu YouTube, bez znaku '#'.
        3. 'thumbnail_text': Tekst na miniaturę wideo (maksymalnie 2-4 mocne słowa).
        4. 'alternative_title': Proponowany alternatywny tytuł (jeśli roboczy okazałby się za słaby), zoptymalizowany pod klikalność (CTR).
        5. 'viewer_question': Angażujące pytanie do widzów, które należy przypiąć w pierwszym komentarzu lub umieścić na końcu opisu.
        
        MUSISZ ZWRÓCIĆ DANE W FORMACIE JSON. Struktura wyjściowa musi wyglądać dokładnie tak:
        {{
          "youtube_metadata": {{
            "alternative_title": "Chwytliwy Tytuł Alternatywny",
            "description": "Pełny tekst opisu z CTA i #hashtagami...",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
            "thumbnail_text": "ZOBACZ TO!",
            "viewer_question": "A wy co myślicie o... Dajcie znać w komentarzach!"
          }}
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Wygeneruj kompletne metadane SEO w formacie JSON."}
                ],
                response_format={ "type": "json_object" },
                temperature=0.7 # Pozwalamy na nieco kreatywności w tworzeniu chwytliwych opisów
            )
            
            result_json = response.choices[0].message.content
            parsed_data = json.loads(result_json)
            
            self.logger.info("Pomyślnie wygenerowano metadane do publikacji.")
            return parsed_data

        except Exception as e:

            self.logger.error(f"Błąd podczas generowania metadanych: {e}")
            return None