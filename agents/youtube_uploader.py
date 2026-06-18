import json
import logging
from pathlib import Path
from typing import Dict, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    Credentials = None
    InstalledAppFlow = None
    Request = None
    build = None
    MediaFileUpload = None

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    def __init__(
        self,
        client_secrets_file: str = "client_secret.json",
        token_file: str = "youtube_credentials.json",
    ):
        self.client_secrets_file = Path(client_secrets_file)
        self.token_file = Path(token_file)
        self.logger = logging.getLogger("YouTubeUploader")

        if build is None or InstalledAppFlow is None or Credentials is None or MediaFileUpload is None:
            raise ImportError(
                "Brakuje pakietów Google API. Zainstaluj google-auth-oauthlib i google-api-python-client."
            )

    def get_credentials(self) -> Credentials:
        if not self.client_secrets_file.exists():
            raise FileNotFoundError(
                "Nie znaleziono client_secret.json. Utwórz poświadczenia OAuth 2.0 dla YouTube i zapisz je w client_secret.json."
            )

        creds = None
        if self.token_file.exists():
            self.logger.info(f"Ładowanie zapisanych poświadczeń z {self.token_file}")
            with self.token_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            creds = Credentials.from_authorized_user_info(data, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Odnawianie poświadczeń YouTube...")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_file), SCOPES
                )
                creds = flow.run_local_server(port=0)

            with self.token_file.open("w", encoding="utf-8") as f:
                f.write(creds.to_json())

        return creds

    def build_service(self, credentials: Credentials):
        return build("youtube", "v3", credentials=credentials)

    def upload_video(
        self,
        video_file: str,
        metadata: Dict,
        privacy_status: str = "public",
    ) -> Dict:
        creds = self.get_credentials()
        service = self.build_service(creds)

        video_path = Path(video_file)
        if not video_path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku wideo: {video_file}")

        snippet = {
            "title": metadata.get("alternative_title", "Nowy film"),
            "description": metadata.get("description", ""),
            "tags": metadata.get("tags", []),
        }
        body = {
            "snippet": snippet,
            "status": {"privacyStatus": privacy_status},
        }

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        request = service.videos().insert(part="snippet,status", body=body, media_body=media)

        self.logger.info("Rozpoczynam przesyłanie wideo do YouTube...")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                self.logger.info(f"Upload progress: {int(status.progress() * 100)}%")

        self.logger.info("Przesyłanie zakończone.")
        return response

    def upload_from_state(
        self,
        video_file: str,
        metadata: Dict,
        privacy_status: str = "public",
    ) -> Dict:
        return self.upload_video(video_file=video_file, metadata=metadata, privacy_status=privacy_status)
