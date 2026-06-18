# Polityka prywatności — Automation (Very Interesting Videos)

Data aktualizacji: 2026-06-18

1. Administrator danych

- Administrator: Very Interesting Videos (konto dewelopera)
- Kontakt: veryinterestingvideos804@gmail.com

2. Zakres i cel przetwarzania danych

Niniejsza aplikacja („Automation”) automatyzuje przygotowanie i przesyłanie krótkich filmów na platformę YouTube w oparciu o zasoby lokalne oraz zewnętrzne API. W związku z tym aplikacja przetwarza i przechowuje wyłącznie te dane, które są niezbędne do działania funkcji:

- Poświadczenia OAuth Google (token dostępu i token odświeżania) — w celu autoryzacji i przesyłania filmów na konto YouTube użytkownika.
- Metadane filmów (tytuły, opisy, tagi, miniatury generowane przez aplikację) — w celu przygotowania i przesyłania treści.
- Lokalne pliki multimedialne wygenerowane przez aplikację (np. `final_video.mp4`, `voice.mp3`, pobrane assety) — przechowywane lokalnie w katalogu projektu.
- Logi aplikacji i plik stanu (`current_video_state.json`) — służą do debugowania oraz umożliwienia wznowienia procesu.

3. Podstawy prawne przetwarzania

Przetwarzanie danych odbywa się na podstawie zgody użytkownika udzielonej poprzez proces OAuth (uprawnienia do przesyłania wideo) oraz w zakresie niezbędnym do wykonania usługi (przesłanie wideo na konto użytkownika).

4. Przekazywanie danych do podmiotów trzecich

Aplikacja korzysta z następujących zewnętrznych usług API:

- Google / YouTube Data API v3 — obsługa przesyłania wideo oraz autoryzacji OAuth.
- GROQ (lub inny wybrany model AI) — używany do generowania treści (temat, skrypt, metadane).
- Pexels / Pixabay — opcjonalne źródła darmowych assetów multimedialnych.

Tokeny OAuth są używane wyłącznie do komunikacji z API Google i nie są przekazywane ani sprzedawane osobom trzecim. Inne dane (np. metadane filmów) mogą być przesyłane do serwisów zewnętrznych w celu wygenerowania treści lub pobrania zasobów (np. zapytania do Pexels). Nie sprzedajemy danych osobowych.

5. Przechowywanie i okres retencji

- Tokeny i poświadczenia: przechowywane lokalnie w pliku `youtube_credentials.json` w katalogu projektu. Użytkownik może je usunąć w dowolnym momencie, co spowoduje konieczność ponownej autoryzacji.
- Pliki multimedialne (wideo, audio, pobrane assety): przechowywane lokalnie — okres przechowywania zależy od użytkownika (plik usuwa się ręcznie poprzez usunięcie katalogu `assets` i plików w projekcie).
- Logi i plik stanu (`current_video_state.json`): przechowywane lokalnie do celów diagnostycznych.

6. Prawa użytkownika

Użytkownik ma prawo do:

- dostępu do swoich danych,
- sprostowania danych,
- usunięcia danych (np. usunięcie `youtube_credentials.json`, `final_video.mp4`, katalogu `assets`),
- cofnięcia zgody na przetwarzanie (odwołanie uprawnień OAuth w ustawieniach konta Google),
- ograniczenia przetwarzania oraz przenoszenia danych.

Aby skorzystać z praw lub uzyskać dodatkowe informacje, prosimy o kontakt: veryinterestingvideos804@gmail.com

7. Bezpieczeństwo

Położono nacisk na minimalizację zakresu przechowywanych danych. Tokeny OAuth są przechowywane lokalnie tylko w pliku `youtube_credentials.json` i nie są przesyłane do zewnętrznych serwerów projektu. Użytkownik odpowiada za zabezpieczenie swojego środowiska (system plików, kopie zapasowe).

8. Jak cofnąć dostęp aplikacji

Jeśli chcesz cofnąć dostęp aplikacji do konta Google:

1. Przejdź do https://myaccount.google.com/ → Bezpieczeństwo → Połączenia zewnętrzne / Aplikacje stron trzecich
2. Znajdź wpis powiązany z aplikacją używaną do autoryzacji i usuń dostęp.
3. Usuń lokalny plik `youtube_credentials.json` w katalogu projektu, aby usunąć zapisane tokeny.

9. Zmiany w polityce prywatności

Zastrzegamy prawo do wprowadzania zmian w tej polityce. Datę ostatniej aktualizacji wskazano na początku dokumentu.

10. Dodatkowe informacje

Projekt jest open‑source — kod źródłowy i dalsze informacje znajdują się w repozytorium projektu. Kontakt: veryinterestingvideos804@gmail.com

---
Plik wygenerowany automatycznie. Dostosuj szczegóły (np. nazwę administratora lub adres e‑mail), jeśli chcesz wprowadzić spersonalizowane informacje.
