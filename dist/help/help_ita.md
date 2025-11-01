
# 🗺️ OSM to PNG
Questo programma è nato per una necessità di unire più mattonelle della mappa OSM in una sola grande immagine che comprendesse l'intera estensione di una città, ad un fattore di zoom che permettesse di leggere i nomi delle strade.

La base di partenza è stata lo script *png_from_osm.py*, trovato nella pagina web *https://bikingaroundagain.com/make-paper-maps-osm-data*, assieme ad altre piccole utility.

Lo script originale, scritto per Python v.2, è stato adattato per funzionare in Python v. 3.12; ho inoltre aggiunto una semplice GUI per poter selezionare direttamente dalla mappa la bounding box (bbox) ed impostare il fattore di zoom che si desidera scaricare.

<br>

## Selezione dell'area sulla mappa
- All'avvio, viene mostrata una mappa interattiva OpenStreetMap. È possibile spostare la vista trascinando con il mouse e modificare lo zoom con la rotella.

- Centrare la finestra sulla località desiderata e ridimensionarla in modo da comprendere l'intera area che si desidera scaricare; Se lo si desidera, è possibile ricercare la località che interessa tramite il servizio Nominatim, digitandone il nome (ad esempio: *Milano*) nella casella di testo *Ricerca Località* e facendo click sul tasto *Ricerca*.

- Regolare lo zoom della mappa con i pulsanti [+] e [-] nell'angolo superiore sinistro della mappa oppure muovendo la rotella del mouse. 

>  **IMPORTANTE** - *Il bordo della finestra definisce la bbox che copre l'intera area visualizzata; Lo zoom della mappa NON influisce sul fattore di zoom delle tile che verranno scaricate; quest'ultimo va impostato manualmente (vedi sotto).*


<br>

## Impostazione del download delle mattonelle
- Selezionare lo stile di mappa desiderato tra quelli disponibili.
>	**ATTENZIONE** - *Le mattonelle degli stili diversi da Mapnik (OSM) sono fornite dal servizio Thunderforest.com; per poterle visualizzare e scaricare occorre inserire una "API Key", ottenibile registrandosi sul sito https://www.thunderforest.com; il piano gratuito consente di scaricare 150000 mattonelle ogni mese.* 
- Utilizzare il controllo *Zoom tile* per impostare il fattore di zoom desiderato per le mattonelle scaricate (questo controllo NON modifica lo zoom della mappa visualizzata nella finestra); sulla destra, è possibile leggere il numero di mattonelle da scaricare per coprire l'intera area, ed una stima del loro peso complessivo in Megabyte.

- Fare click sul pulsante *Anteprima tile* per visualizzare in un pop-up l'effettivo livello di dettaglio impostato per il download. 
 
<br>
 
## Scaricamento delle mattonelle
- Fare click sul pulsante "Avvia" per iniziare il download delle immagini dell'area corrispondenti allo stile e fattore di zoom desiderato. 

- Selezionare la directory ed il nome del file da creare (estensione *.png*) e fare click sul pulsante *Salva* per avviare le operazioni.

>   **ATTENZIONE** - *Quest'operazione utilizza servizi online e potrebbe richiedere molto tempo. I server di OpenStreetMap e ThunderForest non sono progettati per gestire operazioni massive: il programma cerca di interagire con essi in modo rispettoso ed invia le sue richieste ad un ritmo piuttosto lento e con frequenti pause.*


<br>
<br>

## Altre impostazioni del programma
Nella schermata di selezione dell'area da scaricare, fare click sul pulsante [⚙️], nell'angolo in alto a destra della finestra.

Il menu permette di impostare:
- **Dimensione del font** utilizzato nella finestra del programma
- **Api Key**: per poter ottenere le mattonelle degli stili forniti da thunderforest.com (Cyclemap, Transport, ecc.).  
Per ottenere una API Key è sufficiente visitare il sito *https://www.thunderforest.com*, registrare un nuovo account (occorre fornire un indirizzo email valido) ed eseguire l'accesso. 
Il piano gratuito offerto da Thunderforest.com permette di scaricare fino a 150000 mattonelle al mese, valore che dovrebbe essere più che sufficiente per un utilizzo non intensivo del servizio: ad esempio, per ottenere l'intera area di Milano a zoom 17 (nel quale sono leggibili i nomi di tutte le strade) occorre scaricare circa 11000 tessere (circa il 7% dell'intera quota)
- **Email OpenStreetMap**: è richiesta per poter scaricare le mattonelle dello stile Mapnik, nativo del progetto OpenStreetMap. E' possibile indicare un qualunque indirizzo email, ma sarebbe bene iscriversi al progetto su *https://www.openstreetmap.org* con un indirizzo valido e specificare quello all'interno del programma.    

	OpenstreetMap non impone alcun limite al numero di tile scaricabili, ma raccomanda agli utenti di "non inviare un numero eccessivo di richieste"(anche questo concetto è abbastanza generico): per utilizzi intensivi sarebbe più consigliato utilizzare un tile server locale. 
Per scelta progettuale, il programma si interfaccia con il server OSM, ma invia  le proprie richieste a cadenza rallentata, nell'intento di non sovraccaricarlo.

- **Lingua dell'interfaccia**: Selezionare la lingua desiderata tra quelle disponibili.

<br>

## Tradurre l'interfaccia utente in una lingua diversa

La lingua della UI è definita da file *.ini* che si trovano nella directory */lang*:
1. Con un File Manager, raggiungere la cartella nella quale si trova il programma principale (*osm2png*)
2. Accedere alla directory */lang*
3. Creare la copia di uno dei file presenti, inserendo la sigla della linqua desiderata al posto di qquella presente.   
Ad esempio, per creare una traduzione in Francese, creare una copia *ui_eng.ini* (lingua Inglese), assegnandogli il nome di *ui_fra.ini*.
4. Aprire il file appena creato e tradurre tutte le stringhe presenti nella nuova lingua, lasciando invariato tutto ciò che si trova a sinistra dei segni "=". 

	-> Esempio: *zoom_map_label = Map zoom:* diventerà *zoom_map_label = Zoom de la carte:*
6. Salvare il file e riavviare il programma: la nuova lingua dovrebbe essere disponibile nel menu delle impostazioni.

## Tradurre il file di aiuto in una lingua diversa

Per tradurre il file di aiuto, aprire la directory */help* e creare una copia rinominata di uno dei file esistenti, ad esempio *help-eng.md* --> *help-fra.md*; I file di help sono file testuali, scritti in formato Markdown: si possono modificare con un qualunque editor di testo come *Notepad* di WIndows, ma si raccomanda di utilizzare un editor che consenta anche l'anteprima del risultato, come *Visual Studio Code* (*https://code.visualstudio.com/downloa*d) oppure *Ghostwriter* (*https://github.com/KDE/ghostwriter*)

Il testo si può modificare liberamente, ma sarebbe bene seguire la struttura del presente documento.


