---
name: video-test-analysis
description: >
  Analizza un video di test registrato dall'utente e salvato nel progetto.
  Usa un primo subagent per estrarre i frame e tenere solo quelli utili
  (eliminando frame uguali o quasi uguali), poi un secondo subagent per
  ricostruire problema e test svolto, confrontando le evidenze visive con
  il flusso del codice e producendo un report tecnico.
  Usa quando l'utente dice "analizza questo video", "ho registrato un test",
  "capisci questo bug dal video", "screen recording test", "video bug report",
  "confronta video e code flow", "estrai frame utili", "video debugging".
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-sonnet-4-5
---

# Video Test Analysis - Pipeline a Due Subagent

## Quando Usare
- L'utente ha un video (screen recording) di un test manuale o di un bug
- Serve capire cosa succede nel video senza guardare ogni frame
- Serve eliminare frame duplicati o quasi identici
- Serve confrontare cio' che si vede con il comportamento atteso del codice
- Keyword trigger: "video test", "video bug", "screen recording", "analizza video",
  "estrai frame", "confronta con codice", "debug da video"

## Obiettivo
Produrre una analisi riproducibile in due step:
1. Estrarre e deduplicare i frame del video, mantenendo solo i passaggi utili
2. Analizzare i frame utili rispetto al code flow del progetto e produrre
   un report tecnico con mismatch, ipotesi e next checks

Output finale richiesto:
- `.tmp/video-analysis/FRAME_SELECTION_REPORT.md`
- `VIDEO_TEST_REPORT.md`

---

## Pipeline Overview

```
Parent Agent
    |
    |- Subagent 1: FRAME EXTRACTOR + DEDUP
    |   - Legge il video
    |   - Estrae frame candidati
    |   - Elimina frame uguali/quasi uguali
    |   - Produce frame utili + manifest temporale
    |
    \- Subagent 2: VIDEO -> CODE FLOW ANALYZER
        - Legge frame utili e manifest
        - Ricostruisce test e problema osservato
        - Mappa eventi video sui path del codice
        - Produce report finale con mismatch e ipotesi root cause
```

---

## Fase 1 - Ricognizione (Parent Agent)

```
1. Identifica il video fornito dall'utente (path nel progetto)
   - Supporto consigliato: .mp4, .mov, .mkv, .webm

2. Verifica metadata del video:
   ffprobe -v error \
     -show_entries format=filename,duration,size:stream=codec_name,width,height,r_frame_rate \
     -of default=noprint_wrappers=1 [video]

3. Prepara cartelle di lavoro:
   mkdir -p .tmp/video-analysis/frames_raw
   mkdir -p .tmp/video-analysis/frames_useful
   mkdir -p .tmp/video-analysis/artifacts

4. Determina lo scope codice da confrontare:
   - Se l'utente indica file/modulo specifico: usa quello
   - Altrimenti individua componenti, endpoint e servizi potenzialmente coinvolti

5. Passa percorso video + scope codice al Subagent 1
```

---

## Fase 2 - Subagent 1: FRAME EXTRACTOR + DEDUP

Task per il Subagent 1:

```
Sei un video analysis engineer. Devi estrarre i frame utili da un video
di test, rimuovendo frame ridondanti e mantenendo una timeline leggibile.

INPUT:
- VIDEO_PATH: [path assoluto o relativo]
- OUTPUT_DIR: .tmp/video-analysis

OBIETTIVI:
1) Estrarre frame candidati
2) Rimuovere frame uguali o quasi uguali
3) Salvare una timeline minima ma informativa
4) Generare manifest e report della selezione

PASSI OPERATIVI:

A. Estrazione frame candidati (campionamento iniziale)
   ffmpeg -hide_banner -loglevel error -i "$VIDEO_PATH" \
     -vf "fps=4,scale='min(1600,iw)':-2:flags=lanczos" \
     -q:v 2 .tmp/video-analysis/frames_raw/frame_%06d.jpg

B. Dedup dei frame quasi identici (ffmpeg mpdecimate)
   ffmpeg -hide_banner -loglevel error -i "$VIDEO_PATH" \
     -vf "mpdecimate=hi=768:lo=320:frac=0.10,showinfo,scale='min(1600,iw)':-2:flags=lanczos" \
     -vsync vfr -frame_pts true -q:v 2 \
     .tmp/video-analysis/frames_useful/frame_pts_%010d.jpg \
     2> .tmp/video-analysis/artifacts/mpdecimate.log

C. Estrai timeline (timestamp) dal log showinfo
   - Parse di mpdecimate.log
   - Crea .tmp/video-analysis/frame_manifest.csv con colonne:
     frame_file,timestamp_s,source_step,notes

D. Se il video e' lungo (>10 minuti), applica una seconda riduzione:
   - Mantieni sempre frame che mostrano cambi di stato evidenti
   - Mantieni almeno 1 frame ogni 2-3 secondi per continuita' narrativa

E. Genera report selezione:
   .tmp/video-analysis/FRAME_SELECTION_REPORT.md con:
   - Video metadata
   - Numero frame candidati
   - Numero frame rimossi come ridondanti
   - Numero frame finali mantenuti
   - Timestamp chiave individuati
   - Eventuali limiti (blur, bassa qualita', frame drop)

REGOLE:
- Non alterare i frame mantenuti (no annotazioni distruttive)
- Non spostare file fuori da .tmp/video-analysis
- Se ffmpeg/ffprobe non disponibili, documenta il blocco chiaramente
```

---

## Fase 3 - Subagent 2: VIDEO -> CODE FLOW ANALYZER

Dopo il completamento del Subagent 1, lancia il Subagent 2:

```
Sei un debugging analyst senior. Devi analizzare i frame utili di un test video
e confrontare cio' che accade con il flusso del codice del progetto.

INPUT:
- FRAME_DIR: .tmp/video-analysis/frames_useful
- MANIFEST: .tmp/video-analysis/frame_manifest.csv
- FRAME_REPORT: .tmp/video-analysis/FRAME_SELECTION_REPORT.md
- CODE_SCOPE: [file/moduli da analizzare]

OBIETTIVO:
Capire che test e' stato eseguito, quale problema emerge nel video,
e dove il comportamento osservato diverge dal flusso previsto del codice.

ANALISI RICHIESTA:

1. Ricostruzione timeline test
   - Per ogni timestamp chiave identifica:
     a) azione utente osservata
     b) risposta UI/app osservata
     c) eventuale segnale di errore (messaggio, freeze, loop, timeout)

2. Mappatura sul code flow
   - Collega ogni step osservato ai punti di codice probabili:
     - UI component / route / handler
     - API endpoint chiamato (se deducibile)
     - service/use-case/backend logic
     - validazioni e side effect attesi

3. Confronto osservato vs atteso
   - Per ogni step classifica: MATCH | MISMATCH | INCONCLUSIVO
   - Evidenzia dove il video suggerisce una regressione o bug

4. Ipotesi root cause
   - Formula 1-3 ipotesi tecniche ordinate per confidenza
   - Cita per ogni ipotesi: evidenza frame + porzione di flusso codice
   - Evita conclusioni assolute se l'evidenza e' incompleta

5. Raccomandazioni operative
   - Logging o tracing da aggiungere
   - Test automatici da introdurre (unit/integration/e2e)
   - Verifiche mirate per confermare/smentire ipotesi

OUTPUT: scrivi VIDEO_TEST_REPORT.md con questo template:

```markdown
# Video Test vs Code Flow Report
**Data analisi:** YYYY-MM-DD HH:MM
**Video analizzato:** [path video]
**Frame utili analizzati:** N
**Scope codice:** [file/moduli]

---

## Executive Summary
[3-6 righe su test svolto, comportamento osservato, criticita' principale]

## Timeline del Test
| Timestamp | Frame | Azione osservata | Risposta osservata | Stato |
|-----------|-------|------------------|--------------------|-------|

## Mapping Video -> Code Flow
| Step | Evidenza video | Punto codice probabile | Comportamento atteso | Esito |
|------|----------------|------------------------|----------------------|-------|

## Mismatch Rilevati
### Mismatch 1 - [titolo]
- Evidenza: [frame + timestamp]
- Expected (code flow): [...]
- Observed (video): [...]
- Impatto: [utente/business/tecnico]

## Ipotesi Root Cause (ordinate per confidenza)
1. [Ipotesi 1]
   - Confidenza: Alta/Media/Bassa
   - Evidenze: [...]
   - Contro-evidenze: [...]

## Verifiche Consigliate
- [check 1]
- [check 2]
- [check 3]

## Test da Automatizzare
- [test case 1]
- [test case 2]

## Allegati
- .tmp/video-analysis/FRAME_SELECTION_REPORT.md
- .tmp/video-analysis/frame_manifest.csv
- elenco frame chiave utilizzati
```
```

---

## Fase 4 - Finalizzazione (Parent Agent)

```
1. Verifica output prodotti:
   - .tmp/video-analysis/FRAME_SELECTION_REPORT.md
   - VIDEO_TEST_REPORT.md
   - .tmp/video-analysis/frame_manifest.csv

2. Se mancano output, segnala il punto di blocco (tool non disponibile,
   formato video non supportato, scope codice ambiguo)

3. Comunica all'utente un summary breve con:
   - numero frame mantenuti
   - mismatch principali trovati
   - prima ipotesi root cause
```

---

## Note Operative
- Questa skill lavora su video gia' presenti nel progetto (non scarica contenuti esterni)
- Per video molto grandi, preferire campionamento progressivo per evitare tempi eccessivi
- I frame deduplicati riducono rumore ma possono perdere micro-variazioni: dichiararlo nel report
- Se il code scope non e' chiaro, il parent agent deve esplicitare le assunzioni nel report