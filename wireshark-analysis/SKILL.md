---
name: wireshark-analysis
description: >
  Leggi e analizza un file esportato da Wireshark (CSV, JSON, PDML, TXT)
  e produce un report dettagliato in Markdown.
  Usa quando l'utente dice "analizza questo pcap", "leggi il file wireshark",
  "analisi traffico di rete", "cosa vedo in questa capture", "studia questo dump",
  "analizza questo CSV/JSON di wireshark", "traffico HTTP", "pacchetti",
  "analisi di rete", "network capture", "tshark export", "packet analysis".
  Usa un subagent dedicato per l'analisi sistematica.
allowed-tools: Read, Bash, Write, Task
model: claude-opus-4-5
---

# Wireshark Capture Analysis — Subagent Report

## Quando Usare
- L'utente fornisce un file esportato da Wireshark o tshark
- Analisi di traffico di rete per debug, security, performance
- File supportati: CSV (export from Wireshark), JSON (tshark -T json),
  PDML (XML), testo plain (-T text), o file di testo con pacchetti
- Keyword trigger: "wireshark", "pcap", "capture", "traffico rete",
  "pacchetti", "network analysis", "tshark", "dump di rete"

## Obiettivo
Produrre un report `WIRESHARK_REPORT.md` strutturato con:
- Panoramica del traffico catturato
- Analisi per protocollo
- Flussi e conversazioni rilevanti
- Anomalie o eventi notevoli
- Statistiche e timeline

---

## Fase 1 — Lettura File (Parent Agent)

```
1. Identifica il file da analizzare:
   - Percorso fornito dall'utente
   - Formato: controlla l'estensione e le prime righe per determinare il tipo
     (.csv → CSV export, .json → tshark JSON, .xml/.pdml → PDML, .txt → text)

2. Stima la dimensione:
   wc -l [file] 2>/dev/null || wc -c [file]

3. Leggi le prime 50 righe per capire il formato e i campi disponibili:
   head -50 [file]

4. Se è un CSV, estrai l'header per conoscere le colonne:
   head -1 [file]

5. Passa formato, campi disponibili e campione al subagent
```

---

## Fase 2 — Analisi Approfondita (Subagent)

Lancia un subagent con il seguente task:

```
Sei un network security analyst esperto. Devi analizzare un dump di traffico
di rete esportato da Wireshark/tshark e produrre un report tecnico completo.

FILE DA ANALIZZARE: [percorso file]
FORMATO: [CSV/JSON/PDML/TXT]
CAMPI DISPONIBILI: [lista colonne/campi]

ISTRUZIONI DI LETTURA:

### Per file CSV (export Wireshark)
Colonne tipiche: No., Time, Source, Destination, Protocol, Length, Info
Leggi tutto il file o campiona righe rappresentative se molto grande (>10k righe):
- Leggi prime 100 righe
- Leggi ultime 100 righe  
- Campiona ogni N righe per avere copertura temporale

### Per file JSON (tshark -T json)
Ogni oggetto ha struttura: {"_source": {"layers": {...}}}
Estrai i layer: eth, ip, tcp/udp, http, dns, ecc.

### Per file TXT (tshark -T text o simile)
Ogni pacchetto è separato da linea vuota
Leggi blocchi di pacchetti sequenzialmente

---

ANALISI DA ESEGUIRE:

### 1. Overview della Cattura
- Numero totale pacchetti
- Finestra temporale (primo pacchetto → ultimo pacchetto)
- Durata totale della cattura
- Volume totale dati (bytes)
- Protocolli presenti e loro percentuale sul traffico

### 2. Analisi per Protocollo
Per ogni protocollo significativo presente:
- **DNS:** query effettuate, domini risolti, errori NXDOMAIN, DNS over TCP
- **HTTP/HTTPS:** metodi (GET/POST/...), status codes, host contattati,
  user agents, eventuali credentials in chiaro
- **TCP:** connessioni, SYN/FIN/RST anomali, retransmission, flag inusuali
- **UDP:** volume, porte usate
- **ARP:** richieste, anomalie (ARP spoofing pattern)
- **ICMP:** ping, traceroute, messaggi di errore
- **TLS/SSL:** versioni usate, cipher suites se visibili, certificati
- Altri protocolli rilevati

### 3. Top Talkers
- Top 5 IP sorgente per numero di pacchetti
- Top 5 IP destinazione per numero di pacchetti
- Top 5 coppie sorgente-destinazione
- Top porte di destinazione

### 4. Flussi e Conversazioni
Identifica i flussi TCP/UDP principali (sorgente:porta → destinazione:porta):
- Durata del flusso
- Volume dati scambiati
- Protocollo applicativo

### 5. Timeline degli Eventi Principali
Elenca in ordine cronologico gli eventi più significativi:
- Primo pacchetto
- Connessioni importanti stabilite
- Anomalie o errori rilevati
- Ultimo pacchetto

### 6. Anomalie e Punti di Interesse
Cerca attivamente:
- Port scanning (molte connessioni verso porte diverse dallo stesso IP)
- Credenziali in chiaro (HTTP Basic Auth, FTP, Telnet)
- Traffico verso IP/domini sospetti o inusuali
- Protocolli inattesi su porte standard (es: non-HTTP su porta 80)
- Retransmission elevate (possibile problema di rete)
- RST anomali
- Broadcast/multicast eccessivi
- Pacchetti malformati o troncati
- Tentativi di connessione falliti ripetuti

### 7. Contesto di Sicurezza
Se rilevante:
- Traffico non cifrato con dati sensibili visibili
- Connessioni verso IP di rete privata inaspettate
- Pattern di C2 (Command & Control): beaconing regolare, long polling
- Data exfiltration pattern (grandi volumi verso un singolo IP)

---

OUTPUT: Scrivi il report in WIRESHARK_REPORT.md usando questo template:

```markdown
# Wireshark Network Analysis Report
**Data analisi:** YYYY-MM-DD HH:MM  
**File analizzato:** [nome file]  
**Formato:** [CSV/JSON/PDML/TXT]  
**Analista:** Claude Code Subagent  

---

## Executive Summary
[3-5 righe: cosa mostra questa cattura, evento principale, anomalie critiche]

## Statistiche Generali
| Metrica | Valore |
|---------|--------|
| Pacchetti totali | N |
| Inizio cattura | timestamp |
| Fine cattura | timestamp |
| Durata | Xs |
| Volume totale | N bytes |

## Distribuzione Protocolli
| Protocollo | Pacchetti | % |
|-----------|-----------|---|

## Top Talkers
### Per Sorgente
| IP Sorgente | Pacchetti | % |
|------------|-----------|---|

### Per Destinazione  
| IP Destinazione | Pacchetti | % |
|----------------|-----------|---|

## Analisi per Protocollo

### DNS
[analisi]

### HTTP/HTTPS
[analisi]

### TCP
[analisi]

[altri protocolli...]

## Conversazioni/Flussi Principali
| Sorgente | Destinazione | Protocollo | Pacchetti | Volume | Durata |
|---------|--------------|-----------|-----------|--------|--------|

## Timeline degli Eventi
| Timestamp | Evento | Dettagli |
|-----------|--------|---------|

## ⚠️ Anomalie e Punti di Interesse
[Se nessuna anomalia: "Nessuna anomalia rilevante rilevata"]

### [Anomalia 1 — Titolo]
**Timestamp:** ...  
**Descrizione:** ...  
**Pacchetti coinvolti:** ...  
**Valutazione:** [benigno/sospetto/critico]  

## Contesto di Sicurezza
[Valutazione complessiva del profilo di sicurezza del traffico]

## Limitazioni dell'Analisi
[Es: file troncato, protocolli cifrati, dati incompleti]

## Raccomandazioni
[Se rilevante: cosa approfondire, filtri da applicare in Wireshark, ecc.]
```
```

---

## Fase 3 — Finalizzazione (Parent Agent)

```
1. Verifica che WIRESHARK_REPORT.md sia stato creato
2. Se ci sono anomalie CRITICHE o SOSPETTE, evidenziale in chat
3. Notifica l'utente con un summary di 2-3 righe
```

---

## Note Operative
- Il subagent legge il file, NON lo esegue
- Per file molto grandi (>100MB), il subagent campiona i dati
- Il report è solo in Markdown (.md)
- Se il file non è leggibile come testo (es: pcap binario non esportato),
  il parent agent avvisa l'utente che deve prima esportare da Wireshark:
  File → Export Packet Dissections → As CSV (o As JSON con tshark)
- I dati personali/IP interni visibili nel report sono trattati con riservatezza
