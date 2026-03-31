---
name: code-optimizer
description: >
  Ottimizzazione del codice, ricerca bug e miglioramenti con analisi approfondita.
  Usa quando l'utente dice "ottimizza il codice", "cerca bug", "analizza le performance",
  "trova memory leak", "miglioramenti al codice", "code review approfondita",
  "il codice è lento", "possibili bug", "edge case non gestiti", "ottimizza questa funzione",
  "analizza questo file", "trova problemi", "performance review", "bug hunting",
  "controlla i memory leak", "analisi approfondita", "cosa si può migliorare",
  "code quality", "ottimizza le query", "complessità algoritmica".
  Pipeline a tre subagent con Opus: analisi → piano → fix con conferma umana.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-opus-4-5
---

# Code Optimizer — Pipeline Tre Subagent (Opus)

## Quando Usare
- Il codice ha problemi di performance o lentezza percepita
- Sospetto di memory leak o gestione risorse inefficiente
- Bug silenziosi, edge case non gestiti, comportamenti inattesi
- Code review approfondita prima di un rilascio
- Keyword trigger: "ottimizza", "performance", "lento", "memory leak",
  "bug", "edge case", "analizza", "miglioramenti", "cosa si può migliorare"

## Obiettivo
Identificare e correggere bug, inefficienze e problemi di gestione risorse
attraverso una pipeline a tre subagent specializzati, con **conferma umana
obbligatoria** prima di applicare qualsiasi modifica al codice.

---

## Pipeline Overview

```
Parent Agent
    │
    ├─► Subagent 1: ANALYZER (claude-opus-4-5)
    │   - Legge il codice in profondità
    │   - Identifica bug, inefficienze, memory leak, edge case
    │   - Classifica ogni problema per severità e categoria
    │   - Produce /tmp/code-analysis.md
    │   - NON modifica nulla
    │
    ├─► Subagent 2: PLANNER (claude-opus-4-5)
    │   - Riceve l'analisi dal Subagent 1
    │   - Progetta la soluzione ottimale per ogni problema
    │   - Stima impatto e rischio di ogni fix
    │   - Produce /tmp/optimization-plan.md
    │   - NON modifica nulla
    │
    [⏸ PAUSA — mostra piano all'utente e chiede conferma]
    │
    └─► Subagent 3: EXECUTOR (claude-opus-4-5)
        - Riceve il piano approvato
        - Applica i fix in ordine di priorità
        - Verifica i test dopo ogni modifica (se presenti)
        - Produce OPTIMIZATION_REPORT.md
```

---

## Fase 1 — Ricognizione (Parent Agent)

```bash
# 1. Identifica lo scope dell'analisi
#    - File/directory specificati dall'utente, oppure
#    - File modificati di recente, oppure
#    - Intera codebase

# 2. Raccogli contesto tecnico
cat CLAUDE.md 2>/dev/null | head -60   # convenzioni e stack
cat package.json 2>/dev/null           # dipendenze e versioni
# oppure requirements.txt / go.mod / Cargo.toml / pom.xml

# 3. Baseline test (se esistono)
# Salva l'output per confronto post-fix
npm test 2>&1 | tail -20   # oppure pytest / go test / cargo test

# 4. Mappa i file da analizzare
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \
  -o -name "*.py" -o -name "*.go" -o -name "*.rs" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -not -path "*/dist/*" -not -path "*/__pycache__/*" \
  | head -50
```

---

## Fase 2 — Subagent 1: ANALYZER

Task per il Subagent 1:

```
Sei un software engineer senior specializzato in performance engineering,
bug analysis e resource management. Il tuo compito è SOLO analizzare —
NON modificare nulla.

SCOPE: [file/directory da analizzare]
STACK: [linguaggio, framework, versioni]
CONTESTO: [da CLAUDE.md se disponibile]

Esegui un'analisi sistematica focalizzata su tre domini:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMINIO A — PERFORMANCE E COMPLESSITÀ ALGORITMICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Per ogni funzione/metodo significativo, valuta:

**Complessità algoritmica:**
- Identifica loop annidati (O(n²), O(n³)) dove esistono alternative O(n log n) o O(n)
- Query N+1 (loop che eseguono query DB per ogni elemento)
- Ricerche lineari ripetute su strutture dati non indicizzate
- Ricalcoli inutili (stessa operazione costosa chiamata più volte)
- Memoization/caching assente su calcoli ripetitivi

**Operazioni I/O e asincronicità:**
- Operazioni async sequenziali che potrebbero essere parallele (Promise.all)
- Read/write sincroni su file in contesti ad alta concorrenza
- Waterfall di chiamate API che potrebbero essere batched
- Polling inefficiente (invece di event-driven)

**Strutture dati:**
- Array usati per lookup (→ Map/Set/dict più efficiente)
- Oggetti/struct copiati inutilmente invece di passati per reference
- Serializzazione/deserializzazione in hot path
- Concatenazione stringa in loop (→ buffer/join)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMINIO B — MEMORY LEAK E GESTIONE RISORSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Event listener e subscriptions:**
- addEventListener senza removeEventListener corrispondente
- Subscribe senza unsubscribe (RxJS, EventEmitter, WebSocket)
- Interval/timeout non cancellati (clearInterval/clearTimeout mancante)
- Listener registrati dentro loop o funzioni chiamate ripetutamente

**Riferimenti circolari e closures:**
- Closures che catturano oggetti grandi inutilmente
- Riferimenti circolari che impediscono il garbage collection
- Cache o memoization senza limite di dimensione o TTL (crescita illimitata)
- Oggetti globali che accumulano dati nel tempo

**Risorse esterne:**
- Connessioni DB non chiuse (connection leak)
- File descriptor non chiusi (mancanza di finally/defer/with/using)
- Stream non terminati o non gestiti in caso di errore
- Pool di connessioni non rilasciate correttamente

**React/Frontend specifico (se applicabile):**
- useEffect senza cleanup function
- State updates su componenti unmounted
- Ref che trattengono DOM nodes rimossi
- Context provider che ri-renderizzano inutilmente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOMINIO C — BUG LOGICI E EDGE CASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null/undefined e valori limite:**
- Dereferenziazione senza null check (potential null pointer/undefined access)
- Array vuoti non gestiti (primo/ultimo elemento su array vuoto)
- Divisione per zero non verificata
- Integer overflow su contatori o calcoli numerici
- Floating point comparison con == invece di epsilon

**Gestione errori:**
- try/catch che inghiotte silenziosamente gli errori (catch vuoto o solo console.log)
- Promise non gestite (missing .catch() o await in try/catch)
- Errori rilanciati con stack trace perso
- Fallback non definiti per operazioni che possono fallire

**Concorrenza e race condition:**
- Operazioni non atomiche su stato condiviso
- Race condition in operazioni async (due richieste parallele modificano lo stesso dato)
- TOCTOU (Time Of Check To Time Of Use) su file o risorse
- Lock/mutex mancanti in contesti multi-thread

**Validazione input:**
- Input utente usato direttamente senza sanitizzazione
- Assunzioni implicite sul tipo o formato dell'input
- Boundary non verificati (indici array, lunghezze, range numerici)
- Encoding/decoding non gestito (UTF-8, URL encoding)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORMATO OUTPUT — /tmp/code-analysis.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Per ogni problema trovato usa questo schema:

### [ID] — Titolo descrittivo del problema
**Categoria:** PERFORMANCE | MEMORY_LEAK | BUG | EDGE_CASE
**Severità:** CRITICA | ALTA | MEDIA | BASSA
**File:** `path/to/file.ext`
**Riga/e:** 42-67
**Impatto:** [descrizione concreta dell'impatto — lentezza, crash, leak, comportamento errato]

**Codice problematico:**
```[lang]
// snippet del codice incriminato (5-15 righe)
```

**Analisi:**
[Spiegazione tecnica dettagliata del perché è un problema]

**Scenario di manifestazione:**
[Come/quando si manifesta — input specifico, carico, condizione di sistema]

---

Alla fine scrivi un riepilogo:
```
## Riepilogo Analisi
- Totale problemi: N
- CRITICA: N | ALTA: N | MEDIA: N | BASSA: N
- Per categoria: PERFORMANCE: N | MEMORY_LEAK: N | BUG: N | EDGE_CASE: N
- File più critici: [top 3]
```
```

---

## Fase 3 — Subagent 2: PLANNER

Dopo che Subagent 1 ha completato, lancia Subagent 2:

```
Sei un software architect senior. Hai ricevuto un'analisi di problemi
nel codice. Il tuo compito è progettare le soluzioni ottimali per ciascuno —
NON modificare nulla.

ANALISI RICEVUTA: leggi /tmp/code-analysis.md
STACK: [linguaggio, framework, versioni]
CONTESTO: [da CLAUDE.md]

Per ogni problema nell'analisi, progetta la soluzione:

### Criteri di progettazione
- La soluzione deve risolvere il problema senza introdurne altri
- Preferisci la soluzione minima efficace (no over-engineering)
- Considera le dipendenze tra fix (se fix A abilita o dipende da fix B)
- Stima il rischio di regressione per ogni modifica
- Se esistono test, indica quali potrebbero essere impattati

### Per ogni problema produce questa scheda:

```
### Fix [ID] — [Titolo dal problema]
**Priorità di esecuzione:** 1..N (ordine consigliato)
**Dipende da:** [ID fix prerequisiti, se presenti]
**Rischio regressione:** ALTO | MEDIO | BASSO
**Complessità fix:** SEMPLICE (< 10 righe) | MODERATA | COMPLESSA

**Soluzione proposta:**
[Descrizione chiara dell'approccio]

**Codice corretto:**
```[lang]
// implementazione completa del fix
// commentata dove non ovvia
```

**Perché questa soluzione:**
[Motivazione tecnica — perché questo approccio vs alternative]

**Test da eseguire/aggiungere:**
- [test esistente da verificare]
- [nuovo test case da aggiungere se necessario]

**Side effect attesi:**
[Cambiamenti di comportamento osservabili dopo il fix — es. "la funzione ora
 lancia eccezione invece di ritornare null su input vuoto"]
```

### Alla fine, produci una sezione di sintesi:

```
## Piano di Esecuzione

### Ordine consigliato
[Lista ordinata dei fix con stima tempo e rischio]

### Fix da eseguire insieme (stesso file/modulo)
[Raggruppa fix correlati per minimizzare il numero di modifiche]

### Fix da rimandare (backlog)
[Fix BASSA severità che potrebbero essere fatti in futuro]

### ⚠️ Attenzione prima di procedere
[Eventuali avvertenze critiche — es. "il Fix-003 cambia un'interfaccia pubblica"]
```

OUTPUT: scrivi il piano completo in /tmp/optimization-plan.md
```

---

## Fase 4 — Pausa e Conferma (Parent Agent)

Dopo che Subagent 2 ha completato, **il Parent Agent si ferma** e presenta
il piano all'utente:

```
📋 ANALISI COMPLETATA — Piano di ottimizzazione pronto.

Trovati N problemi:
  🔴 CRITICA: N  🟠 ALTA: N  🟡 MEDIA: N  🟢 BASSA: N

Categorie:
  ⚡ Performance: N  |  🧠 Memory Leak: N  |  🐛 Bug: N  |  ⚠️ Edge Case: N

Ordine di fix proposto:
  1. [ID] — [titolo] (severità, rischio regressione)
  2. [ID] — [titolo] (severità, rischio regressione)
  ...

File che verranno modificati:
  - path/to/file1.ext
  - path/to/file2.ext

Per vedere il piano completo: leggi /tmp/optimization-plan.md

Vuoi che proceda con tutti i fix, solo quelli CRITICA/ALTA,
o vuoi selezionare quali applicare?
```

**Attendi la risposta esplicita dell'utente prima di lanciare Subagent 3.**
Opzioni gestite:
- "procedi con tutto" → Subagent 3 esegue tutti i fix del piano
- "solo critici" / "solo alta" → filtra per severità
- "fai solo il fix N, M" → esegue solo i fix specificati
- "no" / "annulla" → termina, i file /tmp rimangono per consultazione

---

## Fase 5 — Subagent 3: EXECUTOR

Lanciato **solo dopo conferma esplicita dell'utente**:

```
Sei un software engineer senior. Devi applicare un piano di fix
già approvato dall'utente. La tua priorità è:
1. Applicare esattamente i fix nel piano — niente di più, niente di meno
2. Mantenere consistenza stilistica con il codice esistente
3. NON modificare file non inclusi nel piano
4. Verificare i test dopo ogni fix ad alto rischio

PIANO APPROVATO: leggi /tmp/optimization-plan.md
FIX DA APPLICARE: [lista fix approvati dall'utente]
STACK: [linguaggio, framework]

### Processo per ogni fix (in ordine di priorità):

1. Rileggi la scheda del fix nel piano
2. Leggi il file target nella sua versione corrente
3. Applica la modifica
4. Se il fix ha rischio regressione ALTO e i test esistono → eseguili
5. Annota l'esito in OPTIMIZATION_REPORT.md

### Gestione anomalie durante l'esecuzione:
- Se il codice nel file è diverso dallo snippet nell'analisi (es. è stato
  modificato nel frattempo) → documenta la discrepanza e salta il fix,
  NON improvvisare
- Se un fix causa test failure → documenta, annulla la modifica (git checkout
  sul file), continua con il prossimo fix
- Se un fix dipende da un altro non ancora applicato → rispetta l'ordine

### Output finale — OPTIMIZATION_REPORT.md:

```markdown
# Optimization Report
**Data:** YYYY-MM-DD
**Modello:** claude-opus-4-5
**Fix applicati:** N/M

## Risultati per Fix

| ID | Titolo | Stato | Note |
|----|--------|-------|------|
| Fix-001 | ... | ✅ Applicato | |
| Fix-002 | ... | ✅ Applicato | test ok |
| Fix-003 | ... | ⏭️ Saltato | codice modificato, discrepanza |
| Fix-004 | ... | ❌ Rollback | test failure su UserService.test.ts |

## Fix Applicati — Dettaglio
[Per ogni fix applicato: file, righe modificate, descrizione breve]

## Fix Saltati o Rollback
[Motivazione per ogni fix non completato]

## Test Results
[Output rilevante dei test se eseguiti]

## Raccomandazioni Post-Fix
[Eventuali follow-up suggeriti: test da aggiungere, monitoring, ecc.]
```

Dopo aver scritto il report, elimina /tmp/code-analysis.md
e /tmp/optimization-plan.md.
```

---

## Fase 6 — Riepilogo Finale (Parent Agent)

```
✅ Ottimizzazione completata.

Applicati N/M fix:
  ✅ Completati: N
  ⏭️ Saltati: N  (motivazione in OPTIMIZATION_REPORT.md)
  ❌ Rollback: N  (motivazione in OPTIMIZATION_REPORT.md)

Performance attesa:
  [se rilevante — es. "rimossi N+1 query su UserRepository"]

Prossimi step consigliati:
  [da OPTIMIZATION_REPORT.md — test da aggiungere, monitoring, ecc.]
```

---

## Note Operative
- Tutti e tre i subagent usano `claude-opus-4-5` per massimizzare la qualità
  dell'analisi e la correttezza dei fix
- Subagent 1 e 2 non modificano mai nulla — solo leggono e scrivono in /tmp
- La pausa in Fase 4 è **obbligatoria** — non avviare Subagent 3 senza
  conferma esplicita dell'utente nel chat
- Se lo scope è molto grande (>30 file), il Subagent 1 analizza prima i file
  ad alto rischio (autenticazione, pagamenti, gestione file, query DB)
- Questa skill è complementare a `refactoring`: refactoring migliora
  leggibilità e struttura, code-optimizer si focalizza su correttezza,
  performance e sicurezza della memoria
