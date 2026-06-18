# 🎬 Pipeline Całkowicie Za Darmo

## ✅ Co masz już zainstalowane i darmowe:

1. **GROQ_API_KEY** ✅ - masz już w `.env`
   - Darmowy tier: 10,000 requests/min
   - Nie kosztuje nic

2. **PEXELS_API_KEY** ✅ - masz już w `.env`
   - Darmowy tier: 200 requests/hour
   - Nie kosztuje nic

## 🔑 Co dodatkowo potrzebujesz (wszystko darmowe):

### 1. Pixabay API Key - DARMOWY
```
Link: https://pixabay.com/api/docs/
1. Kliknij "Sign up" lub zaloguj się
2. Przejdź do https://pixabay.com/api/
3. Kopiuj klucz API (znajduje się w prawym górnym rogu)
4. Dodaj do .env:
   PIXABAY_API_KEY=twoj_klucz
```

### 2. YouTube OAuth - DARMOWY
```
1. Przejdź na https://console.cloud.google.com/
2. Utwórz nowy projekt
3. Włącz YouTube Data API v3
4. Utwórz OAuth 2.0 Desktop Application
5. Pobierz JSON i zapisz jako client_secret.json
6. Ustawienia .env:
   YOUTUBE_CLIENT_SECRETS=client_secret.json
   YOUTUBE_TOKEN_FILE=youtube_credentials.json
```

### 3. TTS (Lektor AI) - DARMOWY - dwie opcje:

#### OPCJA A: ElevenLabs (ma darmowy tier)
```
Link: https://elevenlabs.io/
1. Zaloguj się/zarejestruj
2. Przejdź do https://elevenlabs.io/api
3. Skopiuj API Key
4. Darmowy tier: 10,000 znaków/miesiąc
5. Dodaj do .env:
   ELEVENLABS_API_KEY=twoj_klucz
```

#### OPCJA B: pyttsx3 - CAŁKOWICIE OFFLINE I DARMOWY ⭐ REKOMENDOWANY
```
✅ Nie wymaga internetu
✅ Nie wymaga API Key
✅ Działa offline
✅ Zupełnie za darmo

Instalacja:
pip install pyttsx3

W .env:
ELEVENLABS_API_KEY=  (puste - system użyje pyttsx3 zamiast)
```

## 📋 Gotowy .env dla całkowicie darmowego pipeline'u:

```
# AI
GROQ_API_KEY=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

# Assets (obrazy/wideo)
PEXELS_API_KEY=u2IZlgn9mrJsfIgM9XEmfhounfKrsczVvrms6gbifuZsz2BdH4qtOk5p
PIXABAY_API_KEY=twoj_darmowy_klucz_pixabay

# TTS (Lektor) - pozostaw puste żeby używać pyttsx3 (offline)
ELEVENLABS_API_KEY=

# YouTube
YOUTUBE_CLIENT_SECRETS=client_secret.json
YOUTUBE_TOKEN_FILE=youtube_credentials.json
YOUTUBE_PRIVACY=public
```

## 🚀 Czym zastąpić ElevenLabs (jeśli chcesz):

1. **pyttsx3** - całkowicie darmowe, offline
   - Zainstaluj: `pip install pyttsx3`
   - Modyfikacja: `agents/tts_generator.py` będzie automatycznie używać pyttsx3 zamiast ElevenLabs
   
2. **Google Text-to-Speech** - darmowy tier
   - Link: https://cloud.google.com/text-to-speech
   - Darmowy: 1 milion znaków/miesiąc (pierwszy rok)
   - Instalacja: `pip install google-cloud-texttospeech`

## 💾 Koszt całego pipeline'u:

| Komponent | Koszt | Limit darmowy |
|-----------|-------|---------------|
| GROQ AI | 0 zł | 10,000 req/min |
| Pexels Assets | 0 zł | 200 req/h |
| Pixabay Assets | 0 zł | bez limitu (50 req/h ok) |
| pyttsx3 TTS | 0 zł | bez limitu |
| YouTube Upload | 0 zł | bez limitu |
| **RAZEM** | **0 zł** | ✅ |

## ✨ Jak uruchomić:

```bash
# 1. Zainstaluj pyttsx3 (jeśli chcesz offline TTS)
pip install pyttsx3

# 2. Ustaw .env (patrz góra)

# 3. Uruchom
python main.py
```

## 🎯 Najlepsze darmowe opcje:
- ✅ GROQ (masz już)
- ✅ PEXELS (masz już) 
- ✅ PIXABAY (zarejestruj teraz)
- ✅ pyttsx3 (zainstaluj - całkowicie offline!)
- ✅ YouTube OAuth (bezpłatne)

**Razem: CAŁKOWICIE DARMOWY, NIE PŁACISZ NIC! 🎉**
