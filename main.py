import os
import json
import logging
from dotenv import load_dotenv

# Importy wszystkich sześciu agentów
from agents.temat_generator import TematGenerator
from agents.scenariuszowiec import Scenariuszowiec
from agents.assets_collector import AssetsCollector
from agents.assets_downloader import AssetsDownloader
from agents.tts_generator import TTSGenerator
from agents.voice_subtitles_generator import VoiceSubtitlesGenerator
from agents.editor_planner import EditorPlanner
from agents.upload_manager import UploadManager
from agents.video_renderer import VideoRenderer
from agents.youtube_uploader import YouTubeUploader

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/agent.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        print("BŁĄD: Brak klucza API. Upewnij się, że masz plik .env z GROQ_API_KEY")
        return

    provider = "groq"
    provider_api_key = groq_api_key

    # Inicjalizacja głównego obiektu potoku (Master JSON)
    master_video_data = {
        "global_context": {
            "topic": "Najdziwniejsze fakty o sztucznej inteligencji", 
            "style": "edukacyjny, szybki, wiralowy",
            "duration_seconds": 60
        },
        "selected_idea": {},
        "script": {},
        "assets": {},
        "voice_and_subtitles": {},
        "editing_plan": {},
        "upload_data": {}, 
        "metadata": {"status": "processing"}
    }

    print(f"\n🚀 ROZPOCZYNANIE ZAUTOMATYZOWANEGO POTOKU ({provider.upper()}) 🚀\n")

    # Krok 1: Temat
    agent1 = TematGenerator(api_key=groq_api_key, provider="groq")
    topics_output = agent1.generate_topics(
        topic=master_video_data["global_context"]["topic"],
        style=master_video_data["global_context"]["style"],
        duration=master_video_data["global_context"]["duration_seconds"]
    )
    
    # Zabezpieczenie przed błędem listy
    if topics_output and "ideas" in topics_output and len(topics_output["ideas"]) > 0:
        master_video_data["selected_idea"] = topics_output["ideas"][0]
        print(f"✅ Wybrano temat: {master_video_data['selected_idea']['title']}")
    else:
        print("❌ Błąd: API nie zwróciło żadnych pomysłów. Sprawdź logi.")
        return

    # Krok 2: Skrypt
    agent2 = Scenariuszowiec(api_key=provider_api_key, provider=provider)
    script_output = agent2.generate_script(master_video_data["global_context"]["style"], master_video_data["global_context"]["duration_seconds"], master_video_data["selected_idea"])
    if script_output: master_video_data["script"] = script_output
    else: return

    # Krok 3: Wideo/Assety
    agent3 = AssetsCollector(api_key=provider_api_key, provider=provider)
    assets_output = agent3.collect_assets(master_video_data["script"])
    if assets_output:
        master_video_data["assets"] = assets_output
    else:
        return

    # Krok 3b: Pobranie assetów z internetu
    downloader = AssetsDownloader(assets_dir="assets")
    downloaded_assets = downloader.download_assets(master_video_data["assets"])
    master_video_data["assets"] = downloaded_assets

    # Krok 4: Lektor i Napisy
    agent4 = VoiceSubtitlesGenerator(api_key=provider_api_key, provider=provider)
    voice_output = agent4.generate_voice_and_subs(master_video_data["script"], master_video_data["global_context"]["style"])
    if voice_output:
        master_video_data["voice_and_subtitles"] = voice_output
        with open("movie_subtitles.srt", "w", encoding="utf-8") as f:
            f.write(voice_output["srt_content"])
    else:
        return

    # Krok 4b: Generowanie audio AI
    tts_generator = TTSGenerator(api_key=provider_api_key, provider=provider)
    clean_narration = voice_output.get("clean_narration")
    tts_config = voice_output.get("tts_config", {})
    audio_path = None
    if clean_narration and tts_config:
        audio_path = tts_generator.synthesize_audio(clean_narration, tts_config, output_path="voice.mp3")
        if audio_path:
            print(f"✅ Wygenerowano audio AI: {audio_path}")
        else:
            print("⚠️ Nie wygenerowano audio AI. Renderuję wideo bez lektora audio.")
    else:
        print("⚠️ Brak clean_narration lub tts_config. Pomijam generowanie audio AI.")

    # Krok 5: Plan Montażu
    agent5 = EditorPlanner(api_key=provider_api_key, provider=provider)
    editing_output = agent5.plan_editing(master_video_data["global_context"], master_video_data["script"], master_video_data["assets"], master_video_data["voice_and_subtitles"])
    if editing_output: master_video_data["editing_plan"] = editing_output
    else: return

    # Krok 6: Metadane YouTube
    print("\n--- Uruchamianie Agenta 6: UploadManager ---")
    agent6 = UploadManager(api_key=provider_api_key, provider=provider)
    upload_output = agent6.generate_metadata(
        global_context=master_video_data["global_context"],
        selected_idea=master_video_data["selected_idea"]
    )

    if upload_output and "youtube_metadata" in upload_output:
        master_video_data["upload_data"] = upload_output
        master_video_data["metadata"]["status"] = "ready_for_render_and_upload"
        
        print(f"✅ Wygenerowano metadane do publikacji!")
        print(f"   Tytuł końcowy: {upload_output['youtube_metadata']['alternative_title']}")
    else:
        print("❌ Błąd Agenta 6. Przerywam.")
        return

    with open('current_video_state.json', 'w', encoding='utf-8') as f:
        json.dump(master_video_data, f, indent=4, ensure_ascii=False)

    # Krok 7: Renderowanie wideo
    print("\n--- Renderowanie wideo ---")
    renderer = VideoRenderer(state_path="current_video_state.json", assets_dir="assets")
    force_text_only = not os.path.isdir("assets") or len(os.listdir("assets")) == 0
    audio_candidate = None
    for candidate in ["voice.mp3", "voice.wav", "audio.mp3", "audio.wav"]:
        if os.path.isfile(candidate):
            audio_candidate = candidate
            break

    try:
        final_video_path = renderer.render(
            output_path="final_video.mp4",
            audio_path=audio_candidate,
            force_text_only=force_text_only,
        )
        master_video_data["metadata"]["rendered_video"] = str(final_video_path)
        print(f"✅ Wygenerowano plik wideo: {final_video_path}")
    except Exception as e:
        print(f"❌ Błąd podczas renderowania wideo: {e}")
        return

    # Krok 8: Upload na YouTube
    youtube_secrets = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secret.json")
    youtube_token = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_credentials.json")
    privacy_status = os.getenv("YOUTUBE_PRIVACY", "public")

    try:
        uploader = YouTubeUploader(
            client_secrets_file=youtube_secrets,
            token_file=youtube_token,
        )
        upload_response = uploader.upload_from_state(
            video_file=str(final_video_path),
            metadata=upload_output["youtube_metadata"],
            privacy_status=privacy_status,
        )
        video_id = upload_response.get("id")
        master_video_data["metadata"]["status"] = "uploaded"
        master_video_data["metadata"]["youtube_video_id"] = video_id
        print(f"✅ Film przesłany na YouTube: https://youtu.be/{video_id}")
    except Exception as e:
        master_video_data["metadata"]["status"] = "rendered_but_upload_failed"
        print(f"❌ Upload na YouTube nie powiódł się: {e}")

    # Ostateczny zapis
    with open('current_video_state.json', 'w', encoding='utf-8') as f:
        json.dump(master_video_data, f, indent=4, ensure_ascii=False)
    
    print("\n🎉 POTOK ZAKOŃCZONY SUKCESEM! Stan wideo został zapisany w current_video_state.json")

if __name__ == '__main__':
    main()