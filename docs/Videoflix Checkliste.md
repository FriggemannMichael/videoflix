# Checkliste Videoflix

Bitte erfülle alle Punkte auf dieser Liste, bevor du das Projekt einreichst. **(Definition of Done \- DoD)**

**Bitte beachte auch die grundlegenden Conventions aus der [Checkliste](https://docs.google.com/document/d/1-gUz-skb24UTLAiY5Y-wYDB6GEYI4H9vnxATo-2QsOM/edit?tab=t.0#heading=h.oeodsmlvkdaa).**

Das Erweitern deines Projektes mit dem **Emailversand** bzw. der Umwandlung des Videos mit **HLS** ist Teil dieses **Projektes**. Es ist hier essentiell wichtig, dass hierzu benötigte Wissen sich selbst zu erarbeiten. Dies ist ebenfalls Teil der Aufgabenstellung. Bitte setze dich unbedingt mit den **Dokumentationen** auseinander. Der **Skill Dokumentationen** lesen, verstehen und umsetzen zu können, ist eine der **Kernkompetenzen** eines Entwicklers.

Die User Story ist aus Sicht des Users geschrieben. Entsprechende Umsetzungen für das Backend findest du immer am Ende der Story.

- Link: [Django Email versand](https://docs.djangoproject.com/en/5.2/topics/email/)  
- Link: [FFMPEG ( HLS )](https://ffmpeg.org/ffmpeg-formats.html#hls-2)

> **Legende zum Abhaken (Stand 2026-07-25):** Dieses Repo ist **Backend-only** (Abgabe laut Vorgabe nur als Backend-Repo). Reine Frontend-/UI-Punkte werden vom **kursseitig gestellten Frontend** erfüllt und sind entsprechend gekennzeichnet: *„end-to-end verifiziert"* = von uns über das echte Frontend gegen dieses Backend getestet; *„nicht separat geprüft"* = vom Frontend gestellt, aber von uns nicht einzeln nachgetestet. Backend-Punkte sind mit Datei/Endpoint/Test belegt. Alle Backend-Anforderungen sind erfüllt; einzige offene Zeile ist eine reine Frontend-UI-Nicety (deaktivierter Registrieren-Button), die das gestellte Frontend nicht umsetzt — außerhalb dieses Backend-Repos.

1. ## **Technische Anforderungen**

### **Clean Code**

- [x] Funktionen sind maximal 14 Zeilen lang — Backend: per `tests/scripts/check_size_limits.py` (14 LOC/Funktion) CI-erzwungen  
- [x] Jede Funktion erfüllt genau eine Aufgabe — Backend  
- [x] Alle Funktionsnamen folgen der snake\_case-Konvention — Backend: ruff  
- [x] Sprechende Variablennamen sind durchgängig verwendet — Backend  
- [x] Alle deklarierten Variablen und Funktionen werden genutzt — Backend: ruff (F401/F841) clean  
- [x] Auskommentierter Code wurde entfernt — Backend: geprüft, keiner vorhanden

      ### **Dokumentation**

- [x] Dokumentation ist vorhanden — Docstrings auf allen Klassen/Funktionen  
- [x] README.MD-Datei existiert und ist aussagekräftig — vollständiges README (Issue #21)

      ### **Django-Spezifisch**

- [x] Code ist in der richtigen Datei  
      - [x] views.py \- Nur views, die eine Response returnen — Backend  
      - [x] functions.py oder utils.py \- Neu anlegen für Hilfsfunktionen — `accounts/utils.py`

      ### **Pythonic Style**

- [x] Code ist [PEP-8](https://pep8.org/) compliant — Backend: `ruff check` + `ruff format --check` clean  
- [x] Wenn möglich, einhalten

# 

      ### **Sonstige Technische Anforderungen**

- [x] Backend und Frontend sind getrennt und kommunizieren über eine **REST-API**  
      - [x] Nutze das DRF im Backend — Backend  
- [x] Aufwendige Tasks laufen im Hintergrund mit einem Background-Task Runner (Django RQ) — Backend: `videos/tasks.py`, rqworker  
- [x] Einrichtung einer Main-Memory Datenbank als Caching Layer (Redis) — Backend: `videos/cache.py` (django-redis)  
- [x] Postgres Datenbank statt SQLite — Backend: `settings.DATABASES` (postgresql)  
- [x] Die Benutzeroberfläche ist responsiv und passt sich verschiedenen Bildschirmgrößen an. — (Frontend vom Kurs — end-to-end verifiziert: Login-Seite @375px ohne horizontalen Overflow)  
- [x] Für die Abgabe des Projektes soll **Docker** verwendet werden. Bitte richte das Projekt so ein, dass es sich vollständig über **Docker-Container** starten lässt. — Backend: `docker compose up` bootet db/redis/web

2. ## **Funktionale Anforderungen \- Benutzeraccount & Registrierung:**

### **User Story 1: Benutzerregistrierung**

Als neuer Benutzer möchte ich mich bei Videoflix registrieren können, um Zugang zur Plattform zu erhalten und Inhalte anzusehen. (eine Möglichkeit wäre die Verwendung des Django eigenen [Email-Dienstes](https://docs.djangoproject.com/en/5.2/topics/email/))

- [x] Es gibt ein Registrierungsformular mit Feldern für E-Mail, Passwort und Passwortbestätigung. — (Frontend vom Kurs; Backend akzeptiert exakt diese Felder — end-to-end verifiziert)  
- [x] Nach erfolgreicher Registrierung wird eine Bestätigungs-E-Mail an den Benutzer gesendet. — Backend: `send_activation_email`, `test_register_sends_activation_email`  
- [x] Der Account muss vor dem ersten Login freigeschaltet werden. — Backend: `is_active=False`, Login lehnt inaktiv ab (`test_login_with_inactive_account_returns_400`)  
- [x] Bei ungültiger Eingabe (z.B. bereits verwendete E-Mail) erhält der Benutzer eine Fehlermeldung. Aus Sicherheitsgründen sind die Meldungen allgemein gehalten. Beispiel: “Bitte überprüfe deine Eingaben und versuche es erneut.” — Backend: generische Meldung; im Frontend als Toast „Please check your input and try again." (end-to-end verifiziert)  
- [ ] Der "Registrieren"-Button ist deaktiviert, solange nicht alle Pflichtfelder ausgefüllt sind. — ⚠️ (Frontend vom Kurs — im gestellten Frontend NICHT umgesetzt: der Button ist immer aktiv, die Validierung erfolgt erst beim Absenden/onblur; außerhalb dieses Backend-Repos)  
- [x] Ist man bereits registriert, kann man zum Anmeldeformular wechseln. — (Frontend vom Kurs — end-to-end verifiziert)  
      

**Backend:**

Die Userdaten aus der Registrierung sollten einen neuen Nutzer in der Datenbank anlegen. Hier gilt es zu überprüfen, ob der User bereits existiert. Der User ist am Anfang noch nicht aktiv. Es wird dann vom Backend eine Aktivierungsmail mit entsprechendem Link verschickt, um den User aktiv zu schalten. Dieser Link soll entsprechend auf die Front-End-Seite leiten. Das Front-End sorgt für die entsprechende Verarbeitung und Weiterleitung auf das Backend. Es gibt für das Design der Email eine Vorlage im Repo des FrontEnds auf Github.

> ✅ Backend erfüllt: `RegisterView` legt inaktiven User an, prüft Existenz (generische Meldung), verschickt Aktivierungsmail mit Link auf `FRONTEND_EMAIL_LINK_URL`; Aktivierung über `GET /api/activate/<uidb64>/<token>/`.

### **User Story 2: Benutzeranmeldung**

Als registrierter Benutzer möchte ich mich bei Videoflix anmelden können, um auf mein Konto zuzugreifen und Inhalte anzusehen.

- [x] Es gibt ein Login-Formular mit Feldern für E-Mail und Passwort. — (Frontend vom Kurs — end-to-end verifiziert)  
- [x] Bei falscher Eingabe erhält der Benutzer eine Fehlermeldung. — Backend: 400 (`test_login_with_wrong_password_returns_400`)  
- [x] Fehlermeldungen sind aus Sicherheitsgründen allgemein gehalten. Spezifische Informationen wie "E-Mail nicht registriert" oder "Passwort falsch" werden vermieden. — Backend: einheitliche generische Meldung  
- [x] Es gibt eine Option "Passwort vergessen" für den Fall, dass Benutzer ihr Passwort zurücksetzen müssen. — (Frontend vom Kurs — end-to-end verifiziert: „Forgot password?"-Link vorhanden; Backend-Endpoint `POST /api/password_reset/`)  
- [x] Nach erfolgreicher Anmeldung wird der Benutzer zur Startseite weitergeleitet. — (Frontend vom Kurs — end-to-end verifiziert: Redirect auf das Video-Dashboard)  
- [x] Sollte der Nutzer noch kein Konto haben, kann er zum Registrierungsformular wechseln. — (Frontend vom Kurs — end-to-end verifiziert: „Sign Up now!"-Link vorhanden)

**Backend:**

Das Backend prüft beim Login entsprechende Daten. Bei fehlerhaften Daten bzw. bei nicht aktivem User, soll entsprechender Response an das Front-End geschickt werden. 

> ✅ Backend erfüllt: `LoginView`/`LoginSerializer` prüft Credentials, lehnt inaktive User ab (Django-`authenticate`), setzt HTTP-only JWT-Cookies; generische 400-Antwort bei Fehlern.

### 

### 

### 

### 

### 

### 

### **User Story 3: Benutzerabmeldung**

Als Benutzer möchte ich mich von Videoflix abmelden können, damit niemand ohne meine Zustimmung auf meinen Account zugreifen kann.

- [x] Es gibt eine "Logout" \-Option in der Benutzeroberfläche. — (Frontend vom Kurs — end-to-end verifiziert: Logout-Button im Header)  
- [x] Nach Auswahl dieser Option werde ich sicher aus der Anwendung ausgeloggt und zum Login-Bildschirm weitergeleitet. — (Frontend vom Kurs — end-to-end verifiziert: Redirect auf Login, Auth-Cookies entfernt; Backend: Cookies gelöscht + Refresh-Token geblacklistet)  
- [x] Nach dem Abmelden sind meine persönlichen Daten und Einstellungen ohne erneutes Einloggen nicht zugänglich. — Backend: Blacklist + Cookie-Löschung (`test_logout_api`, `Refresh token after logout` → 401)

**Backend:**

Beim Logout sollen alle Cookies im Frontend gelöscht werden und entsprechender Response an das Front-End geschickt werden.

> ✅ Backend erfüllt: `LogoutView` blacklistet den Refresh-Token und löscht beide Auth-Cookies.

### **User Story 4: Passwort zurücksetzen**

Als Benutzer möchte ich mein Passwort zurücksetzen können, falls ich es vergessen habe, um wieder Zugang zu meinem Konto zu erhalten. (eine Möglichkeit wäre die Verwendung des Django eigenen [Email-Dienstes](https://docs.djangoproject.com/en/5.2/topics/email/))

- [x] Es gibt eine "Passwort vergessen"-Funktion auf der Login-Seite. — (Frontend vom Kurs — end-to-end verifiziert: „Forgot password?"-Link auf der Login-Seite)  
- [x] Bei Eingabe einer E-Mail-Adresse für die Passwort-Zurücksetzung erhält man aus Sicherheitsgründen keine spezifische Rückmeldung zur Existenz des Kontos — Backend: identische Antwort für bekannt/unbekannt (`Password reset for unknown email`)  
- [x] Nach Eingabe der E-Mail-Adresse wird eine Passwort-Reset-E-Mail an den Benutzer gesendet. — Backend: `send_reset_email_if_user_exists`  
- [x] Passwort-Reset-E-Mail sollte responsive und richtig angezeigt werden. — Backend: HTML+Text-Template vorhanden (Rendering nicht separat geprüft)  
- [x] Der Benutzer kann über einen Link in der E-Mail ein neues Passwort festlegen. — Backend: `POST /api/password_confirm/<uidb64>/<token>/`  
- [x] Nach erfolgreichem Zurücksetzen kann sich der Benutzer mit dem neuen Passwort anmelden. — Backend: `test_password_confirm_api`

**Backend:**

Das Backend bekommt bei klick auf “Passwort vergessen” entsprechende Daten aus dem Front-End. Auch hier soll eine Email vom Backend verschickt werden, die ebenfalls einen Link enthält und auf das Front-End weiterleitet. Das Front-End sorgt für die entsprechende Verarbeitung und Weiterleitung auf das Backend. Es gibt für das Design der Email eine Vorlage im RePo des FrontEnds auf Github. Nach erfolgreicher Passwortänderung wird dieses in der Datenbank gespeichert und das alte gelöscht. Tipp: Schaue im Frontend, welche Parameter du brauchst.

> ✅ Backend erfüllt: Reset-Request ohne Existenz-Preisgabe, E-Mail mit Link auf `FRONTEND_EMAIL_LINK_URL`, neues Passwort wird gespeichert; der Link wird durch das Django-Token nach der Änderung automatisch ungültig.

3. ## **Funktionale Anforderungen \- Video-Dashboard & Wiedergabe**

### **User Story 5: Video-Dashboard**

Als angemeldeter Benutzer möchte ich eine Übersicht über verfügbare Videos sehen, um interessante Inhalte zu entdecken und auszuwählen.

- [x] Das Dashboard zeigt einen Hero-Bereich mit einem hervorgehobenen Video-Teaser. (alternativ kann ein Standbild aus dem Video gezeigt werden) — (Frontend vom Kurs — end-to-end verifiziert: Hero mit Standbild sichtbar)  
- [x] Videos werden in Genres gruppiert angezeigt. — (Frontend vom Kurs; Backend liefert das `category`-Feld — end-to-end verifiziert)  
- [x] Reihenfolge der Videos nach Erstellungsdatum DESC — Backend: `order_by('-created_at')` (`test_videos_are_ordered_by_created_at_descending`)  
- [x] Jedes Video wird mit einem Thumbnail und Titel dargestellt. (Ein Bild aus dem Video reicht hier als Thumbnail) — Backend liefert `thumbnail_url` + `title`; Frontend zeigt — end-to-end verifiziert

**Backend:**

Das Backend muss entsprechende .m3u8 Dateien bzw. .ts Dateien ausliefern können. Zudem ist ein Thumbnail nötig.

> ✅ Backend erfüllt: `VideoListView` (nur `completed`, DESC), Thumbnail per FFmpeg (`generate_thumbnail`), HLS-Playlist/-Segment-Auslieferung.

### **User Story 6: Video-Wiedergabe**

Als Benutzer möchte ich Videos in der bestmöglichen Qualität ansehen können, die meiner Internetverbindung und meinem Gerät entspricht.

- [x] Es werden verschiedene Auflösungen (480p, 720p, 1080p) zur manuellen Auswahl angeboten. — Backend liefert alle drei Auflösungen (verifiziert); Auswahl-Dropdown mit 480p/720p/1080p end-to-end verifiziert  
- [x] Der Player bietet grundlegende Steuerelemente wie Play, Pause, Vor- und Zurückspulen. — (Frontend vom Kurs — end-to-end verifiziert: `<video controls>` mit nativen Steuerelementen)  
- [x] Es gibt eine Vollbildoption für eine immersive Wiedergabeerfahrung. — (Frontend vom Kurs — end-to-end verifiziert: `fullscreenEnabled` + native Vollbild-Steuerung)

**Backend:**

Das Backend muss hier entsprechende .m3u8 Dateien und .ts Dateien für die entsprechende Auflösung bereitstellen.

> ✅ Backend erfüllt: `GET /api/video/<id>/<res>/index.m3u8` + `GET /api/video/<id>/<res>/<segment>` für 480p/720p/1080p, authentifiziert, Path-Traversal-geschützt.

4. ## **Sonstige Anforderungen**

### **User Story 7: Rechtliche Informationen**

Als Benutzer möchte ich Zugang zu rechtlichen Informationen wie Datenschutzerklärung und Impressum haben, um mich über meine Rechte und die Nutzungsbedingungen zu informieren.

- [x] Es gibt leicht zugängliche Links zur Datenschutzerklärung und zum Impressum im Footer der Website. — (Frontend vom Kurs — end-to-end verifiziert: Privacy- + Imprint-Links im Footer)  
- [x] Die Informationen sind klar strukturiert und in verständlicher Sprache verfasst. — (Frontend vom Kurs — nicht separat geprüft)  
- [x] Die Seiten sind responsiv und auf allen Geräten gut lesbar. — (Frontend vom Kurs — nicht separat geprüft)

**Backend bzw. Deployment:**

Sofern du das Projekt für Dich selbst deployen möchtest, achte darauf, dass Impressum und Datenschutz mit richtigen Daten gefüllt sind. Ebenfalls ist die Kennzeichnung nötig, dass dieses Front-End von uns gestellt wurde.

> ℹ️ Nicht zutreffend: Abgabe erfolgt ausschließlich als GitHub-Backend-Repo (kein eigenes Deployment), daher keine Impressum-/Datenschutz-Realdaten nötig.

- Videoflix empfehlen wir nicht als Portfolio-Projekt, da hier entsprechende Server-Hardware nötig ist. Dies ist mit erhöhten Kosten verbunden. Die Abgabe erfolgt für dieses Projekt ausschließlich als GitHub-Link bzw. ist hier nur das GitHub-Repo nötig. Achte darauf, dass nur das Backendprojekt in diesem Repo vorhanden ist. Bitte verändere keine Docker-Dateien die du von unserem Setup erhalten hast.  
