---
name: store-visuals
description: "Crea gli screenshot a carosello e il video dimostrativo per le schede App Store e Google Play di un'app Flutter (iOS/Android). Usala quando servono screenshot per gli store, mockup con cornice e sfondo, un video promozionale dell'app o l'aggiornamento degli asset dopo un cambio di interfaccia."
argument-hint: "carosello | video | tutto (facoltativo: lingue e formati)"
---

# Screenshot a carosello e video dimostrativo per gli store

Produce due cose, dalla stessa app e con lo stesso stile:

- **il carosello**: le slide degli store, composte su un'unica tela larga così che
  lo sfondo prosegua da un'immagine all'altra e la scena principale stia a
  cavallo delle prime due;
- **il video**: l'app pilotata da un test di integrazione, registrata dal
  simulatore, con i tocchi disegnati dopo e — in una seconda versione — cornice,
  sfondo e didascalie.

Le catture vengono dall'**app vera**, pilotata da `flutter drive`: niente mockup
disegnati, niente finti dati.

---

## 1. Prima di toccare qualsiasi cosa: mettersi d'accordo

**Non produrre nulla prima che l'utente abbia approvato scene, testi e
scaletta.** Rifare una campagna di catture costa un'ora di macchina; concordarla
costa cinque minuti.

Guarda l'app (schermate principali, `l10n`, funzioni recenti) e **proponi**, in
una tabella:

1. **Le scene da catturare**, in ordine di caricamento sugli store. La prima è
   quella che App Store mostra nei risultati di ricerca: di solito la schermata
   che risponde alla domanda per cui l'app esiste.
2. **Le didascalie del carosello**, titolo e sottotitolo per ciascuna slide,
   nelle lingue previste. Titoli brevi: al corpo usato ci stanno ~20 caratteri
   per riga.
3. **La scaletta del video**: quali scene, in che ordine, quanto dura ognuna,
   e soprattutto **su cosa chiude** — la funzione che distingue l'app.
4. **Che cosa evidenziare** con i cerchi che pulsano: al massimo due o tre
   punti in tutto il filmato, altrimenti diventano rumore.

Chiedi anche, se non è deducibile dal progetto:

- quali **formati** servono (vedi `reference/specifiche-store.md`): il set
  iPhone 6.9" e iPad 13" sono obbligatori su App Store se l'app gira su iPad,
  il telefono Android su Play, i tablet solo se si vuole il badge "ottimizzata
  per tablet";
- quali **lingue**;
- se c'è una **palette** o un colore di marca da usare per lo sfondo;
- quale **spiaggia/prodotto/contenuto** fare da protagonista: deve essere ricco
  di dati veri (foto, valori, contenuti), non un caso vuoto.

Solo dopo l'approvazione si passa alla produzione. Se durante il lavoro emerge
che una scena non funziona (dati assenti, schermata che chiede l'accesso), si
torna dall'utente con una proposta, non si cambia la scaletta di testa propria.

---

## 2. Preparare le catture

### 2.1 Stato deterministico

Il pilota gira su un'installazione pulita a ogni esecuzione: tutto ciò che
comparirebbe "la prima volta" va spento nelle preferenze simulate, altrimenti
finisce nelle immagini. Nel progetto da cui nasce questa skill sono comparsi, a
turno: il tour di primo avvio, il permesso notifiche, la richiesta di
valutazione, l'invito a installare la PWA, il consenso alle statistiche e un
popup promozionale. Ogni volta è costata una campagna di catture da rifare.

Prima di registrare, cerca nel progetto le chiavi di `SharedPreferences` che
governano quei "primi avvii" (`grep -rn "SharedPreferences" lib | grep -i
"seen\|asked\|done\|dismissed"`) e mettile tutte a `true` nel test.

### 2.2 Pubblicità spenta

Se l'app mostra annunci, spegnili a build time (`--dart-define`) e **asserisci**
nel test che siano spenti: un banner o un modulo di consenso in mezzo a una
cattura la rende inutilizzabile.

### 2.3 Aspettare i dati, non i secondi

Non basta `await Future.delayed`: aspetta il **provider** o lo stato che porta i
dati. Con un'attesa a tempo capita di catturare schermate a metà caricamento —
indicatori di aggiornamento, elenchi vuoti, mappe senza contenuto.

---

## 3. Catturare gli screenshot

Il pilota (`reference/driver_template.dart`) naviga l'app e **stampa un
marcatore** a ogni scena; uno script esterno legge lo stdout e scatta con
`simctl`/`adb`:

```bash
scripts/capture_screens.sh ios <udid> <cartella> <lingua>
scripts/capture_screens.sh android <serial> <cartella> <lingua>
scripts/capture_android_all.sh          # crea/avvia gli emulatori e cattura
```

Non si usa `binding.takeScreenshot`: su iOS sostituisce la superficie viva con
un'immagine statica e da lì in poi le catture escono bianche. La cattura di
sistema, in più, include la barra di stato vera.

Simulatori e emulatori: `reference/trappole.md` ha i comandi per crearli con le
risoluzioni giuste e i tre modi in cui si rompono.

---

## 4. Comporre il carosello

```bash
python3 scripts/build_carousel.py --config store-visuals.json
```

Le scelte che rendono lo stile riconoscibile, e che vanno mantenute:

- **una tela sola.** Le slide si disegnano su un'unica immagine larga
  `n × larghezza` e si tagliano alla fine: è l'unico modo perché le bande
  diagonali dello sfondo proseguano senza scalini e perché un telefono possa
  stare a cavallo di due slide.
- **la scena principale a cavallo delle prime due**, inclinata di ~10°: chi
  scorre il carosello vede un movimento, non cartoline scollegate.
- **cornice bianca spessa, senza finto notch**: le catture contengono già barra
  di stato e isola dinamica vere; disegnarne un'altra dà due tacche.
- **tre quote legate fra loro** — aria dal bordo, aria del testo dal bordo
  (uguali) e distanza testo-telefono. Con valori diversi il telefono si incolla
  a un bordo e il vuoto si accumula dall'altra parte.
- **corpo del testo sulla media geometrica** fra i rapporti di larghezza e
  altezza: tarandolo sulla sola larghezza, su tablet le didascalie diventano
  enormi.

`n` slide per `n-1` scene: la prima ne occupa due.

---

## 5. Girare il video

### 5.1 Gesti veri, senza mirino

`tester.tap` e `fling` fanno disegnare al binding dei test un **mirino tondo con
la croce** sul punto toccato: in un video promozionale è inguardabile e non si
può spegnere. Il pilota usa eventi con sorgente **device**
(`handlePointerEventForSource` + `shouldPropagateDevicePointerEvents`): per
l'app sono identici a un dito — ondine di tocco, trascinamenti con velocità — e
il binding non ci disegna sopra niente.

Il flag va **rimesso a `false`** prima della fine del test, altrimenti il
framework lo segnala come errore.

### 5.2 Marcatori invece di disegni

Il pilota non disegna niente: stampa dove il dito ha toccato e cosa
evidenziare, con le coordinate prese dall'albero dei widget (non misurate a
occhio sui fotogrammi):

```
VIDEO:start,<ms>   VIDEO:zoom,<ms>   VIDEO:end,<ms>
TOUCH:<ms>,<x>,<y>
RING:<ms>,<cx>,<cy>,<rx>,<ry>,<secondi>
```

### 5.3 La catena

```bash
scripts/record_video.sh <udid> <lingua>      # registra + salva i marcatori
python3 scripts/add_touches.py --lang it     # pallini bianchi + taglio
python3 scripts/compose_video.py --lang it   # cornice, sfondo, didascalie, cerchi
```

Escono due file, e servono a due cose diverse:

| File | Cosa | Dove si carica |
|---|---|---|
| `promo-<lang>.mov` | solo riprese dell'app, con i pallini dei tocchi | **App Store** (l'App Preview non ammette cornici né grafiche aggiunte) |
| `promo-<lang>-social.mov` | cornice, sfondo a bande, didascalie, cerchi | YouTube, Play, social |

### 5.4 Tempi legati ai marcatori, mai fissi

Ogni ripresa dura un po' diversa (i dati arrivano quando arrivano). Le
didascalie prendono inizio e fine dai **tocchi** registrati e il taglio iniziale
si conta dal marcatore dello zoom: con tempi scritti a mano la didascalia di una
scena finisce sopra quella dopo.

---

## 6. Verifica prima di consegnare

- [ ] ogni immagine ha **la misura esatta** dello slot (nessun ridimensionamento
      in fase di caricamento);
- [ ] su Play il lato lungo **non supera il doppio** del corto — la risoluzione
      nativa dei telefoni moderni (1080×2400) la viola;
- [ ] nessun popup, banner, indicatore di caricamento o schermata di accesso
      nelle immagini;
- [ ] i dati mostrati sono reali e sensati (niente elenchi vuoti, niente valori
      a zero);
- [ ] nel video le didascalie coincidono con quello che si vede;
- [ ] i file grezzi e intermedi restano **fuori dal repository** (registrazione
      non tagliata, marcatori, timeline): si rigenerano.

Guarda le immagini e il video prima di dire che sono pronti: affiancare le slide
in una striscia unica rivela sbilanciamenti che sulla singola non si vedono.

---

## Riferimenti

- `reference/specifiche-store.md` — misure e limiti di App Store e Play
- `reference/trappole.md` — i modi in cui questo lavoro si rompe, e i rimedi
- `reference/driver_template.dart` — pilota di partenza, con i gesti "device"
- `scripts/` — composizione carosello, catena video, orchestrazione emulatori
