
# 🗺️ Selettore di Coordinate OSM (Coordinate Picker)

## 🇮🇹 Funzionalità principali

### 🗺️ Selezione area su mappa
- L’app mostra una mappa interattiva OpenStreetMap.
- È possibile spostare la vista trascinando con il mouse e modificare lo zoom con la rotella.
- Alla pressione di **OK**, il programma restituisce:
  - le coordinate del centro della mappa (latitudine, longitudine),
  - il livello di zoom attuale,
  - lo stile della mappa selezionato.
- Alla pressione di **Annulla**, viene restituito `None`.

### 🌍 Stili mappa multipli
- Gli stili disponibili vengono caricati dalla variabile `map_styles`, che include **Mapnik** (predefinito) e tutti gli stili **Thunderforest**.
- Se necessario, viene utilizzata automaticamente la chiave API di Thunderforest.

### 🔎 Ricerca località (Nominatim)
- Tramite la casella di testo e il pulsante **“Cerca”**, puoi ricercare un luogo per nome.
- Se la ricerca produce più risultati, viene mostrato un popup con l’elenco.
  - È possibile selezionare una voce con doppio clic o tramite il pulsante “Seleziona”.
- Dopo la scelta, la mappa si centra automaticamente sulla località trovata.
- È anche possibile avviare la ricerca premendo **Invio** nella casella di testo.

### 🧭 Anteprima della mappa
- Il pulsante **“Anteprima”** apre una finestra popup (dimensione circa metà dell’app principale) che mostra una mini-mappa:
  - centrata sullo stesso punto della mappa principale,
  - con lo **zoom e lo stile impostati** dall’utente.
- La mini-mappa si aggiorna automaticamente se:
  - cambia lo stile selezionato,
  - cambia il valore di zoom richiesto,
  - o si sposta la vista della mappa principale.
- Rimane sempre **in primo piano** finché non viene chiusa.

### ℹ️ Aiuto contestuale
- Un pulsante **“?”** apre un popup di aiuto, caricando il testo da un file (es. `help.txt`).
- Il popup è leggibile e scrollabile.
- È possibile aprire lo stesso popup premendo **F1** da qualunque punto dell’applicazione.
- I nomi del file e del titolo del popup sono definiti nei file di lingua (`ui_ita.ini`, `ui_eng.ini`).

### ⚙️ Configurazione persistente
- Tutte le impostazioni vengono salvate in `config.ini`:
  - posizione della finestra (`win_width`, `win_height`),
  - ultima posizione mappa (`lastposition`),
  - ultimo zoom (`lastzoom`),
  - lingua dell’interfaccia (`general.language`),
  - dimensione carattere (`general.fontsize`).
- Al riavvio, l’app ripristina automaticamente lo stato precedente.

### 🔡 Interfaccia localizzabile
- Tutti i testi dell’interfaccia (etichette, pulsanti, titoli, messaggi) sono caricati da file `.ini` di lingua:
  - `ui_ita.ini` per l’italiano,
  - `ui_eng.ini` per l’inglese.
- La lingua corrente è definita nella sezione `[general]` del file `config.ini`.

### ✨ Dettagli di interfaccia
- Etichette di zoom e attribuzione OSM sovrapposte alla mappa.
- Testo centrato nella casella Zoom.
- Font e dimensione letti da `config.ini`.
- Overlay sempre visibili in primo piano.
- Numero stimato di tile e peso totale calcolati automaticamente.


---

## 🇬🇧 Main Features

### 🗺️ Map Area Selection
- The app displays an interactive OpenStreetMap view.
- You can **pan** by dragging and **zoom** with the mouse wheel.
- When clicking **OK**, the app returns:
  - the coordinates of the map center (latitude, longitude),
  - the current zoom level,
  - and the selected map style.
- Clicking **Cancel** returns `None`.

### 🌍 Multiple Map Styles
- Map styles are loaded from the `map_styles` variable, including **Mapnik** (default) and all **Thunderforest** styles.
- If needed, your Thunderforest API key is automatically used.

### 🔎 Location Search (Nominatim)
- The **Search** field lets you find places by name.
- If multiple results are found, a popup list appears:
  - double-click or click **Select** to choose one.
- The map centers on the selected location.
- You can also press **Enter** to start the search.

### 🧭 Map Preview
- The **Preview** button opens a popup window (about half the main window size) showing a mini-map:
  - centered on the same point as the main map,
  - using the **zoom and style** chosen by the user.
- The mini-map automatically updates if:
  - the map style changes,
  - the zoom level is adjusted,
  - or the main map is moved.
- The preview window stays **always on top**.

### ℹ️ Contextual Help
- The **“?”** button opens a help popup that loads text from a file (e.g. `help.txt`).
- You can also open the help window by pressing **F1** anywhere in the app.
- The popup supports scrolling and uses localized titles and filenames.

### ⚙️ Persistent Configuration
- All user preferences are saved in `config.ini`:
  - window size,
  - last map position and zoom,
  - interface language,
  - font size.
- The app automatically restores the previous session at startup.

### 🔡 Localized Interface
- All UI strings (buttons, labels, messages) are loaded from language `.ini` files:
  - `ui_ita.ini` for Italian,
  - `ui_eng.ini` for English.
- The active language is set in `[general]` of `config.ini`.

### ✨ UI Details
- OSM attribution and zoom labels overlaid on the map.
- Zoom entry text centered.
- Font and size read from configuration.
- Real-time display of estimated tiles and total download size.
- Smooth and consistent layout using Tkinter + ttk.
