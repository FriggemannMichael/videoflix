# Checkliste Videoflix

Bitte erfülle alle Punkte auf dieser Liste, bevor du das Projekt einreichst. **(Definition of Done \- DoD)**

**Bitte beachte auch die grundlegenden Conventions aus der [Checkliste](https://docs.google.com/document/d/1-gUz-skb24UTLAiY5Y-wYDB6GEYI4H9vnxATo-2QsOM/edit?tab=t.0#heading=h.oeodsmlvkdaa).**

Das Erweitern deines Projektes mit dem **Emailversand** bzw. der Umwandlung des Videos mit **HLS** ist Teil dieses **Projektes**. Es ist hier essentiell wichtig, dass hierzu benötigte Wissen sich selbst zu erarbeiten. Dies ist ebenfalls Teil der Aufgabenstellung. Bitte setze dich unbedingt mit den **Dokumentationen** auseinander. Der **Skill Dokumentationen** lesen, verstehen und umsetzen zu können, ist eine der **Kernkompetenzen** eines Entwicklers.

Die User Story ist aus Sicht des Users geschrieben. Entsprechende Umsetzungen für das Backend findest du immer am Ende der Story.

- Link: [Django Email versand](https://docs.djangoproject.com/en/5.2/topics/email/)  
- Link: [FFMPEG ( HLS )](https://ffmpeg.org/ffmpeg-formats.html#hls-2)

1. ## **Technische Anforderungen**

### **Clean Code**

- [ ] Funktionen sind maximal 14 Zeilen lang  
- [ ] Jede Funktion erfüllt genau eine Aufgabe  
- [ ]  Alle Funktionsnamen folgen der snake\_case-Konvention  
- [ ]  Sprechende Variablennamen sind durchgängig verwendet  
- [ ]  Alle deklarierten Variablen und Funktionen werden genutzt  
- [ ]  Auskommentierter Code wurde entfernt

      ### **Dokumentation**

- [ ]  Dokumentation ist vorhanden  
- [ ]  README.MD-Datei existiert und ist aussagekräftig

      ### **Django-Spezifisch**

- [ ] Code ist in der richtigen Datei  
      - [ ] views.py \- Nur views, die eine Response returnen  
      - [ ] functions.py oder utils.py \- Neu anlegen für Hilfsfunktionen

      ### **Pythonic Style**

- [ ] Code ist [PEP-8](https://pep8.org/) compliant  
- [ ] Wenn möglich, einhalten

# 

      ### **Sonstige Technische Anforderungen**

- [ ] Backend und Frontend sind getrennt und kommunizieren über eine **REST-API**  
      - [ ] Nutze das DRF im Backend  
- [ ] Aufwendige Tasks laufen im Hintergrund mit einem Background-Task Runner (Django RQ)  
- [ ] Einrichtung einer Main-Memory Datenbank als Caching Layer (Redis)  
- [ ] Postgres Datenbank statt SQLite  
- [ ] Die Benutzeroberfläche ist responsiv und passt sich verschiedenen Bildschirmgrößen an.  
- [ ] Für die Abgabe des Projektes soll **Docker** verwendet werden. Bitte richte das Projekt so ein, dass es sich vollständig über **Docker-Container** starten lässt.

2. ## **Funktionale Anforderungen \- Benutzeraccount & Registrierung:**

### **User Story 1: Benutzerregistrierung**

Als neuer Benutzer möchte ich mich bei Videoflix registrieren können, um Zugang zur Plattform zu erhalten und Inhalte anzusehen. (eine Möglichkeit wäre die Verwendung des Django eigenen [Email-Dienstes](https://docs.djangoproject.com/en/5.2/topics/email/))

- [ ] Es gibt ein Registrierungsformular mit Feldern für E-Mail, Passwort und Passwortbestätigung.  
- [ ] Nach erfolgreicher Registrierung wird eine Bestätigungs-E-Mail an den Benutzer gesendet.   
- [ ] Der Account muss vor dem ersten Login freigeschaltet werden.  
- [ ] Bei ungültiger Eingabe (z.B. bereits verwendete E-Mail) erhält der Benutzer eine Fehlermeldung. Aus Sicherheitsgründen sind die Meldungen allgemein gehalten. Beispiel: “Bitte überprüfe deine Eingaben und versuche es erneut.”  
- [ ] Der "Registrieren"-Button ist deaktiviert, solange nicht alle Pflichtfelder ausgefüllt sind.  
- [ ] Ist man bereits registriert, kann man zum Anmeldeformular wechseln.  
      

**Backend:**

Die Userdaten aus der Registrierung sollten einen neuen Nutzer in der Datenbank anlegen. Hier gilt es zu überprüfen, ob der User bereits existiert. Der User ist am Anfang noch nicht aktiv. Es wird dann vom Backend eine Aktivierungsmail mit entsprechendem Link verschickt, um den User aktiv zu schalten. Dieser Link soll entsprechend auf die Front-End-Seite leiten. Das Front-End sorgt für die entsprechende Verarbeitung und Weiterleitung auf das Backend. Es gibt für das Design der Email eine Vorlage im Repo des FrontEnds auf Github.

### **User Story 2: Benutzeranmeldung**

Als registrierter Benutzer möchte ich mich bei Videoflix anmelden können, um auf mein Konto zuzugreifen und Inhalte anzusehen.

- [ ] Es gibt ein Login-Formular mit Feldern für E-Mail und Passwort.  
- [ ] Bei falscher Eingabe erhält der Benutzer eine Fehlermeldung.   
- [ ] Fehlermeldungen sind aus Sicherheitsgründen allgemein gehalten. Spezifische Informationen wie "E-Mail nicht registriert" oder "Passwort falsch" werden vermieden.  
- [ ] Es gibt eine Option "Passwort vergessen" für den Fall, dass Benutzer ihr Passwort zurücksetzen müssen.  
- [ ] Nach erfolgreicher Anmeldung wird der Benutzer zur Startseite weitergeleitet.  
- [ ] Sollte der Nutzer noch kein Konto haben, kann er zum Registrierungsformular wechseln.

**Backend:**

Das Backend prüft beim Login entsprechende Daten. Bei fehlerhaften Daten bzw. bei nicht aktivem User, soll entsprechender Response an das Front-End geschickt werden. 

### 

### 

### 

### 

### 

### 

### **User Story 3: Benutzerabmeldung**

Als Benutzer möchte ich mich von Videoflix abmelden können, damit niemand ohne meine Zustimmung auf meinen Account zugreifen kann.

- [ ] Es gibt eine "Logout" \-Option in der Benutzeroberfläche.  
- [ ] Nach Auswahl dieser Option werde ich sicher aus der Anwendung ausgeloggt und zum Login-Bildschirm weitergeleitet.  
- [ ] Nach dem Abmelden sind meine persönlichen Daten und Einstellungen ohne erneutes Einloggen nicht zugänglich.

**Backend:**

Beim Logout sollen alle Cookies im Frontend gelöscht werden und entsprechender Response an das Front-End geschickt werden.

### **User Story 4: Passwort zurücksetzen**

Als Benutzer möchte ich mein Passwort zurücksetzen können, falls ich es vergessen habe, um wieder Zugang zu meinem Konto zu erhalten. (eine Möglichkeit wäre die Verwendung des Django eigenen [Email-Dienstes](https://docs.djangoproject.com/en/5.2/topics/email/))

- [ ] Es gibt eine "Passwort vergessen"-Funktion auf der Login-Seite.  
- [ ] Bei Eingabe einer E-Mail-Adresse für die Passwort-Zurücksetzung erhält man aus Sicherheitsgründen keine spezifische Rückmeldung zur Existenz des Kontos  
- [ ] Nach Eingabe der E-Mail-Adresse wird eine Passwort-Reset-E-Mail an den Benutzer gesendet.  
- [ ] Passwort-Reset-E-Mail sollte responsive und richtig angezeigt werden.  
- [ ] Der Benutzer kann über einen Link in der E-Mail ein neues Passwort festlegen.  
- [ ] Nach erfolgreichem Zurücksetzen kann sich der Benutzer mit dem neuen Passwort anmelden.

**Backend:**

Das Backend bekommt bei klick auf “Passwort vergessen” entsprechende Daten aus dem Front-End. Auch hier soll eine Email vom Backend verschickt werden, die ebenfalls einen Link enthält und auf das Front-End weiterleitet. Das Front-End sorgt für die entsprechende Verarbeitung und Weiterleitung auf das Backend. Es gibt für das Design der Email eine Vorlage im RePo des FrontEnds auf Github. Nach erfolgreicher Passwortänderung wird dieses in der Datenbank gespeichert und das alte gelöscht. Tipp: Schaue im Frontend, welche Parameter du brauchst.

3. ## **Funktionale Anforderungen \- Video-Dashboard & Wiedergabe**

### **User Story 5: Video-Dashboard**

Als angemeldeter Benutzer möchte ich eine Übersicht über verfügbare Videos sehen, um interessante Inhalte zu entdecken und auszuwählen.

- [ ] Das Dashboard zeigt einen Hero-Bereich mit einem hervorgehobenen Video-Teaser. (alternativ kann ein Standbild aus dem Video gezeigt werden)  
- [ ] Videos werden in Genres gruppiert angezeigt.  
- [ ] Reihenfolge der Videos nach Erstellungsdatum DESC  
- [ ] Jedes Video wird mit einem Thumbnail und Titel dargestellt. (Ein Bild aus dem Video reicht hier als Thumbnail)

**Backend:**

Das Backend muss entsprechende .m3u8 Dateien bzw. .ts Dateien ausliefern können. Zudem ist ein Thumbnail nötig.

### **User Story 6: Video-Wiedergabe**

Als Benutzer möchte ich Videos in der bestmöglichen Qualität ansehen können, die meiner Internetverbindung und meinem Gerät entspricht.

- [ ] Es werden verschiedene Auflösungen (480p, 720p, 1080p) zur manuellen Auswahl angeboten.  
- [ ] Der Player bietet grundlegende Steuerelemente wie Play, Pause, Vor- und Zurückspulen.  
- [ ] Es gibt eine Vollbildoption für eine immersive Wiedergabeerfahrung.

**Backend:**

Das Backend muss hier entsprechende .m3u8 Dateien und .ts Dateien für die entsprechende Auflösung bereitstellen.

4. ## **Sonstige Anforderungen**

### **User Story 7: Rechtliche Informationen**

Als Benutzer möchte ich Zugang zu rechtlichen Informationen wie Datenschutzerklärung und Impressum haben, um mich über meine Rechte und die Nutzungsbedingungen zu informieren.

- [ ] Es gibt leicht zugängliche Links zur Datenschutzerklärung und zum Impressum im Footer der Website.  
- [ ] Die Informationen sind klar strukturiert und in verständlicher Sprache verfasst.  
- [ ] Die Seiten sind responsiv und auf allen Geräten gut lesbar.

**Backend bzw. Deployment:**

Sofern du das Projekt für Dich selbst deployen möchtest, achte darauf, dass Impressum und Datenschutz mit richtigen Daten gefüllt sind. Ebenfalls ist die Kennzeichnung nötig, dass dieses Front-End von uns gestellt wurde.

- Videoflix empfehlen wir nicht als Portfolio-Projekt, da hier entsprechende Server-Hardware nötig ist. Dies ist mit erhöhten Kosten verbunden. Die Abgabe erfolgt für dieses Projekt ausschließlich als GitHub-Link bzw. ist hier nur das GitHub-Repo nötig. Achte darauf, dass nur das Backendprojekt in diesem Repo vorhanden ist. Bitte verändere keine Docker-Dateien die du von unserem Setup erhalten hast.  
  