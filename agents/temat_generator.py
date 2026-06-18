from groq import Groq
import json
import logging
import time

class TematGenerator:
    def __init__(self, api_key: str = None, provider: str = "groq"):
        self.primary_api_key = api_key
        self.provider = provider.lower()
        self.logger = logging.getLogger("TematGenerator")

        if self.provider == "groq":
            if not self.primary_api_key:
                raise ValueError("Brak klucza GROQ_API_KEY dla providera groq.")
            self.client = Groq(api_key=self.primary_api_key)
            self.mode = "groq"
        else:
            raise ValueError("Nieznany provider. Użyj 'groq'.")

    def generate_topics(self, topic: str, style: str, duration: int) -> dict:
        self.logger.info(f"Generowanie tematów dla: {topic}")
        
        prompt = f"""
        Stwórz 3 pomysły na wideo o '{topic}'. Styl: {style}, czas: {duration}s.
        Zwróć odpowiedź wyłącznie w formacie JSON. Nie dodawaj żadnego tekstu poza czystym JSON.
        Użyj formatu: {{"ideas": [{{"title": "...", "hook": "...", "description": "...", "keywords": [...]}}]}}
        """

        try:
            return self._call_api(prompt)
        except Exception as e:
            self.logger.error(f"Błąd krytyczny po próbach ponowienia: {e}")
            return {"ideas": []}

    def _call_api(self, prompt: str, attempt: int = 1) -> dict:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            error_text = str(e)
            if attempt <= 3 and any(code in error_text for code in ["429", "500", "503", "json_validate_failed"]):
                wait_time = 10 * attempt
                self.logger.warning(f"Problem z API Groq (próba {attempt}/3). Czekam {wait_time}s...")
                time.sleep(wait_time)
                return self._call_api(prompt, attempt + 1)
            raise e