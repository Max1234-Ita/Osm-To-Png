# OSM to PNG

## **Indice**

>[Introduzione](#introduzione)
>
>[Interfaccia grafica](#interfaccia-grafica)
>
> [Selezione dell'area da scaricare](#selezione-dellarea-da-scaricare)
>
> [Impostazione del download](#impostazione-del-download-delle-mattonelle)
>
> [Altre impostazioni del programma](#altre-impostazioni-del-programma)
>
> [Scaricamento delle mattonelle](#scaricamento-delle-mattonelle)
>
> [Tradurre l'interfaccia utente in una lingua diversa](#tradurre-linterfaccia-utente-in-una-lingua-diversa)
>
> [Tradurre il file di Aiuto in una lingua diversa](#tradurre-il-file-di-aiuto-in-una-lingua-diversa)
>
 
<br>

---

## Introduzione
Questo programma permette di unire più mattonelle della mappa OpenStreetMap (OSM) in una sola grande immagine che comprende l'estensione di un'area a scelta, al fattore di zoom desiderato.

All'origine dello sviluppo vi è uno script pubblicato dalla pagina web <a href="https://bikingaroundagain.com/make-paper-maps-osm-data" target="_blank">*Biking Around Again*</a>, assieme ad altre piccole utility.

Il codice, in origine per Python 2, è stato adattato per funzionare in Python 3.12; E' stata inoltre aggiunta un'interfaccia grafica per poter selezionare la bounding box (*"bbox"*) in modo più intuitivo ed impostare il fattore di zoom da scaricare indipendentemente da quello della mappa visualizzata.

[ ^^ Vai all' Indice](#indice)<br>

---
## Interfaccia grafica

All'avvio, viene mostrata una mappa interattiva OpenStreetMap.
E' possibile spostare la vista trascinando con il mouse; per modificare lo zoom, muovere la rotella oppure utilizzare i pulsanti **" + "** e **" - "** sulla sinistra.<br>

![Immagine GUI](images/area_select.png)

**Elementi principali della finestra**:

>**1.** Località più vicina al centro della mappa (città o paese)
>
>**2.** Zoom della mappa visualizzata
>
>**3.** Livello di zoom delle tessere da scaricare
>
>**4.** Selezione dello stile di mappa
>
>**5.** Ricerca località (tramite *Nominatim*)
>
>**6.** Visualizza anteprima delle mattonelle al livello di zoom impostato ([ 3 ])
>
>**7.** Stima del numero di tile necessarie e del loro peso totale (approssimativo)
>
>**8.** Uscita dal programma
>
>**9.** Avvio del download
>
>**10.** Aiuto (visualizza questo documento)
>
>**11.** Impostazioni


[ ^^ Vai all' Indice](#indice)<br>


---
## Selezione dell'area da scaricare
 - Centrare la finestra sulla località desiderata; Se lo si desidera, è possibile ricercare la località che interessa tramite il servizio *Nominatim* **[ 5 ]**, digitandone il nome (ad esempio: *Milano*) nella casella di testo *Ricerca Località* e facendo click sul tasto *Ricerca*.

 - Ridimensionare la finestra trascinandone i bordi e/o regolare lo zoom della mappa con i pulsanti '+' e '-' **[ 3 ]** nell'angolo superiore sinistro della mappa, in modo da comprendere l'intera area che si desidera scaricare;

>  **IMPORTANTE** - *<u>Il bordo della finestra definisce la bbox</u>; Lo zoom della mappa NON influisce sul fattore di zoom delle tile che verranno scaricate; quest'ultimo va impostato manualmente.*

[ ^^ Vai all' Indice](#indice)<br>

---

## Impostazione del download
 -  Selezionare lo stile di mappa desiderato tra quelli disponibili **[ 4 ]**.

>	**ATTENZIONE** - *Lo stile "Mapnik (OSM)" è offerto da [OpenStreetMap](https://www.openstreetmap.org) e lo scaricamento delle tessere è possibile solo specificando un indirizzo email; tutti gli altri, invece, sono forniti da [Thunderforest](https://www.thunderforest.com); per poterli visualizzare e scaricare occorre inserire una "API Key", ottenibile registrandosi sul sito [https://www.thunderforest.com](https://www.thunderforest.com); Email e/o API Key devono essere inserite nei rispettivi campi del menu Impostazioni* **[ 11 ]**


 - Utilizzare il controllo *Zoom tile*  **[ 3 ]** per impostare il fattore di zoom desiderato per le mattonelle da scaricare. N.B.: questo controllo NON modifica lo zoom della mappa visualizzata nella finestr); sulla destra  **[ 7 ]**, è possibile leggere una stima del numero di mattonelle da necessarie per coprire l'area scelta ed una stima approssimativa del loro peso complessivo in Megabyte.

 - Fare click sul pulsante *Anteprima tile*  **[ 6 ]** per visualizzare in un pop-up l'effettivo livello di dettaglio impostato per il download. 

![Anteprima tile](images/tile_preview.png)

[ ^^ Vai all' Indice](#indice)<br>

---

## Altre impostazioni del programma
Nella schermata di selezione dell'area da scaricare, fare click sul pulsante [⚙️], nell'angolo in alto a destra della finestra.

![Anteprima tile](images/settings.png)


 - **Dimensione del font** utilizzato nella finestra del programma;

 - **Api Key**: Chiave necessaria per poter scaricare le mattonelle degli stili forniti da thunderforest.com (Cyclemap, Transport, ecc.).  
Per ottenere una API Key è sufficiente visitare il sito *https://www.thunderforest.com*, registrare un nuovo account (occorre fornire un indirizzo email valido) e/o eseguire l'accesso. 
Il piano gratuito offerto da Thunderforest.com permette di scaricare fino a 150000 mattonelle al mese, valore che dovrebbe essere più che sufficiente per un utilizzo non intensivo del servizio: ad esempio, per ottenere l'intera area di Milano a zoom 17 (nel quale sono leggibili i nomi di tutte le strade) occorre scaricare circa 11000 tessere (circa il 7% dell'intera quota);

 - **Email OpenStreetMap**: è richiesta per poter scaricare le mattonelle dello stile Mapnik, nativo del progetto OpenStreetMap. E' possibile indicare un qualunque indirizzo email, ma sarebbe bene utilizzare un account OSM (è possibile iscriversi gratuitamente su *https://www.openstreetmap.org*).    

> **ATTENZIONE:** <u>*OpenstreetMap non impone alcun limite</u> al numero di tile scaricabili, ma raccomanda agli utenti di "non inviare un numero eccessivo di richieste"(anche questo concetto è abbastanza generico): per utilizzi intensivi sarebbe più consigliato utilizzare un tile server locale. 
>Per scelta progettuale, il programma si interfaccia con il server OSM, ma invia le proprie richieste a cadenza rallentata, nell'intento di non sovraccaricarlo.*

 - **Lingua dell'interfaccia**: Selezionare la lingua desiderata tra quelle disponibili. Chiudere e riavviare l'app per applicare l'impostazione.

[ ^^ Vai all' Indice](#indice)<br>


--- 
## Scaricamento delle mattonelle
 - Fare click sul pulsante "Avvia" **[ 9 ]** per iniziare il download delle immagini dell'area corrispondenti allo stile e fattore di zoom desiderato. 

 - Viene mostrata una finestra di Gestione risorse (*"Salva con nome"*): Selezionare la directory e digitare il nome del file da creare (estensione *.png*); fare click sul pulsante *Salva* per avviare le operazioni.
 
![Save](images/save_file.png#center)


 - Una volta confermato il nome del file, compare una piccola finestra di supervisione: attendere il termine delle operazioni; se lo si desidera. è possibile arrestare temporaneamente il download (pulsante *[Pausa]*) oppure abortirlo (*[Annulla]*).
 
 ![Download](images/download.png)
 
 
<br>

>   **ATTENZIONE** - *Il download delle immagini impiega servizi online e potrebbe richiedere molto tempo. I server di OpenStreetMap e ThunderForest non sono progettati per gestire operazioni massive: il programma cerca di interagire con essi in modo rispettoso ed invia le sue richieste ad un ritmo piuttosto lento e con frequenti pause.*


[ ^^ Vai all' Indice](#indice)<br>

---
___

## Tradurre l'interfaccia utente in una lingua diversa

La lingua dell'interfaccia utente' è definita da file *.ini* che si trovano nella directory */lang*; il nome del file è nel formato "ui_[lingua].ini", come ad esempio *ui_English.ini* per la lingua Inglese e *ui_Italiano.ini* per quella Italiana.

1. Con un File Manager, ad esempio *Gestione File* di Windows, **raggiungere la cartella nella quale si trova il programma principale** (*osm2png*) ed entrare nella directory */lang* .

2. **Creare la copia** del file che corrisponde alla lingua di partenza e rinominarlo, sostituendo il nome della linqua con quello desiderato.  

> **Esempio**: per una traduzione in Francese, copiare il file *ui_english.ini* (lingua Inglese), ed assegnargli il nome *ui_français.ini*.

3. **Aprire il nuovo file con un qualsiasi editor di testo ASCII**, come *Blocco Note* in Windows o *Gedit* in Linux e tradurre nella nuova lingua tutte le stringhe presenti .  
>**Ricordare i seguenti 2 punti**:  
> -  **I nomi delle "chiavi"** (--> tutto ciò che si trova a sinistra dei segni "=") **non vanno modificati**.   
>   
>  - **I valori tra parentesi graffe**, ad esempio *{n_tiles}* , **non vanno modificati**.
>
> **Esempio**: 
>
> *zoom_map_label = Map zoom* diventerà
>
> *zoom_map_label = Zoom de la carte*

<br>

> **IMPORTANTE: *la sezione [info], andrà così compilata***:
>
> **[info]**  
> **language** = Nome della lingua da visualizzare nel menu (es. *'Français'*)  
> **lang** = sigla internazionale della lingua (es. '*fr*')  
> **translator** = Nome del traduttore (facoltativo)  
> **help_file** = nome del file di aiuto da visualizzare quando viene cliccato il pulsante ' ? ' **[ 10 ]** (vedi sotto)
>


4. **Salvare** il file e riavviare il programma: la nuova lingua dovrebbe essere disponibile nel menu **⚙️** *Impostazioni*.

[ ^^ Vai all' Indice](#indice)<br>

---

## Tradurre il file di aiuto in una lingua diversa

I file di aiuto all'utente sono documenti testuali, scritti in formato [Markdown](https://it.wikipedia.org/wiki/Markdown) e che i trovano nella directory */lang*: si possono modificare con un qualunque editor di testo come *Blocco note* di Windows, ma si raccomanda di utilizzare un'applicazione che possa anche mostrare l'anteprima del risultato, come *Visual Studio Code* (*https://code.visualstudio.com/download*) oppure *Ghostwriter* (*https://github.com/KDE/ghostwriter*).

<br>
Se si desidera tradurre il file di aiuto in un'altra lingua:

1. Con un File Manager, **raggiungere la cartella nella quale si trova il programma principale** (*osm2png*) ed entrare nella directory */help* .

2. **Creare una copia** del file che corrisponde alla lingua di partenza e rinominarla, sostituendo la sigla della linqua con quella desiderata.  

> **Esempio**: per una traduzione in Francese, copiare il file *help_eng.md* (lingua Inglese), ed assegnargli il nome *help_fra.md*. 

3. Aprire il nuovo file nell'editor Markdown ed **eseguire la traduzione**.   
Non serve che sia letterale, sarebbe però buona cosa rispettare struttura ed impaginazione del documento di origine, oltre alle regole basilari del linguaggio Markdown.

4. **Salvare** il lavoro terminato ed **aggiornare la sezione [info]** del file *.ini* che configura l'interfaccia del programma nella medesima lingua (/lang/ui_[Lingua].ini), come spiegato al punto '3' del paragrafo precedente (vedi).*  

> **Esempio**: Se il nome del nuovo file è *help_fra.md*, nella sezione [info] di */lang/ui_Français.ini* si dovrà specificare la chiave:      
>
>&emsp; *help_file = help_fra.md*


> **IMPORTANTE**: *Il file .md deve trovarsi nella directory "/help"; Se non si aggiorna la sezione [info] del file di localizzazione dell'interfaccia utente, la nuova versione tradotta del file di aiuto non sarà disponibile nel programma.*


[ ^^ Vai all' Indice](#indice)<br>
