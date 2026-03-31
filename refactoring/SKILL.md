---
name: refactoring
description: >
  Refactoring del codice per renderlo human-readable, ben formattato e strutturato.
  Usa quando l'utente dice "refactoring", "refactora", "pulisci il codice",
  "migliora la leggibilità", "codice spaghetti", "hard to read", "troppo complesso",
  "ristruttura", "rinomina variabili", "estrai funzioni", "separa responsabilità",
  "clean code", "code smell", "troppo lungo", "difficile da mantenere".
  Usa una pipeline a due subagent: il primo legge e pianifica, il secondo esegue.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-sonnet-4-5
---

# Refactoring — Pipeline a Due Subagent

## Quando Usare
- Il codice è difficile da leggere o manutenere
- Funzioni troppo lunghe, nomi poco descrittivi, logica aggrovigliata
- Mancanza di struttura chiara (separation of concerns)
- Dopo un'implementazione veloce che ha accumulato debito tecnico
- Keyword trigger: "refactoring", "refactora", "pulisci", "leggeibilità",
  "clean code", "ristruttura", "troppo complesso", "spaghetti"

## Obiettivo
Produrre codice **human-readable**, **well-formatted** e **well-structured**
senza alterare il comportamento — usando una pipeline a due subagent specializzati.

---

## Pipeline Overview

```
Parent Agent
    │
    ├─► Subagent 1: READER/PLANNER
    │   - Legge il codice in profondità
    │   - Identifica tutti i code smell
    │   - Produce un piano di refactoring dettagliato
    │   - NON modifica nulla
    │
    └─► Subagent 2: EXECUTOR  (riceve il piano da Subagent 1)
        - Legge il piano
        - Esegue le modifiche file per file
        - Verifica che i test passino dopo ogni modifica (se presenti)
        - Produce un report delle modifiche
```

---

## Fase 1 — Identificazione Scope (Parent Agent)

```
1. Determina l'ambito del refactoring:
   - File specifici indicati dall'utente, oppure
   - Intera directory/modulo, oppure
   - Tutto il codebase

2. Leggi velocemente i file in scope per stimare complessità

3. Controlla se esistono test (da eseguire prima e dopo come safety net):
   find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" | head -20

4. Se i test esistono, eseguili e salva il risultato baseline

5. Passa tutto al Subagent 1
```

---

## Fase 2 — Subagent 1: READER & PLANNER

Task per il Subagent 1:

```
Sei un senior software engineer specializzato in clean code e code review.
Il tuo compito è SOLO analizzare e pianificare — NON modificare nulla.

SCOPE DEL REFACTORING:
[file/directory da analizzare]

CONTESTO PROGETTO:
[linguaggio, framework, convenzioni da CLAUDE.md se disponibile]

ANALISI RICHIESTA — per ogni file in scope:

### 1. Code Smell Detection
Identifica e documenta:

**Readability Issues:**
- Nomi poco descrittivi (variabili: a, b, tmp, data, val, flag, ecc.)
- Nomi fuorvianti (nome non corrisponde al comportamento)
- Abbreviazioni criptiche
- Magic numbers (numeri hardcoded senza contesto)
- Magic strings
- Commenti inutili ("increment i") o mancanti dove servirebbero

**Structure Issues:**
- Funzioni/metodi troppo lunghi (>20-30 righe)
- Funzioni che fanno troppe cose (violazione SRP)
- Nesting profondo (>3-4 livelli di indentazione)
- Logica duplicata (DRY violations)
- God objects/functions
- Feature envy (un oggetto usa troppo i dati di un altro)

**Formatting Issues:**
- Indentazione inconsistente
- Spaziatura irregolare
- Import/require disorganizzati
- File troppo lunghi (>300-400 righe)

**Design Issues:**
- Responsabilità miste (business logic nel controller, ecc.)
- Dipendenze hardcoded (invece di injection)
- Gestione errori assente o inconsistente
- Return anticipati mancanti (arrow pattern)

### 2. Piano di Refactoring
Per ogni file, produce un piano strutturato in questo formato:

```
FILE: src/path/to/file.ext
PRIORITÀ: ALTA/MEDIA/BASSA
RISCHIO: ALTO/MEDIO/BASSO (rischio di introdurre bug)

MODIFICHE PIANIFICATE:
1. [Rinomina funzione X → nomeDescriptivo]
   Motivazione: X è ambiguo, non descrive il comportamento
   
2. [Estrai logica di validazione in funzione validateUserInput()]
   Motivazione: riga 45-89 fa validazione dentro una funzione che fa anche saving
   
3. [Sostituisci magic number 86400 → SECONDS_IN_DAY]
   Motivazione: il numero non è autoesplicativo
   
4. [Spezza funzione processOrder() in:
   - validateOrder()
   - calculateTotal()  
   - applyDiscounts()
   - saveOrder()]
   Motivazione: troppo lunga (120 righe), troppe responsabilità

ORDINE DI ESECUZIONE:
[sequenza ottimale per minimizzare conflitti e rischi]

DIPENDENZE TRA MODIFICHE:
[se modifica A dipende da modifica B, specificarlo]
```

### 3. Summary Finale
- Totale file da modificare: N
- Modifiche ad alto rischio: lista
- Modifiche sicure (solo rename/format): lista
- Stima complessità: SEMPLICE / MODERATA / COMPLESSA
- Raccomandazione: eseguire tutto insieme o in batch?

OUTPUT: Scrivi il piano completo in /tmp/refactoring-plan.md
```

---

## Fase 3 — Subagent 2: EXECUTOR

Dopo che il Subagent 1 ha completato, lancia il Subagent 2:

Task per il Subagent 2:

```
Sei un senior software engineer. Devi eseguire un piano di refactoring
già pianificato. La tua priorità è:
1. NON alterare il comportamento del codice
2. Seguire il piano esattamente
3. Mantenere consistenza con le convenzioni del progetto

PIANO DA ESEGUIRE: leggi /tmp/refactoring-plan.md

CONTESTO PROGETTO:
[linguaggio, framework, convenzioni]

REGOLE DI ESECUZIONE:

### Prima di iniziare
- Leggi tutto il piano
- Identifica le modifiche ad alto rischio
- Se i test esistono, eseguili per avere una baseline

### Durante l'esecuzione
Per ogni file nel piano (in ordine di priorità):
1. Leggi il file completo prima di modificarlo
2. Applica le modifiche nel piano in ordine
3. Dopo ogni modifica, verifica che la sintassi sia corretta
4. Se la modifica è ad alto rischio e i test esistono, eseguili
5. NON aggiungere funzionalità non pianificate
6. NON modificare file non nel piano
7. Se trovi un caso non previsto dal piano, documenta e continua

### Regole di qualità
**Naming:**
- Funzioni: verbo + sostantivo descrittivo (getUserById, calculateDiscount)
- Variabili: sostantivo descrittivo (userCount, not cnt)
- Booleani: prefisso is/has/should/can (isActive, hasPermission)
- Costanti: UPPER_SNAKE_CASE
- Evita abbreviazioni (usr → user, cfg → config, res → response)

**Struttura funzioni:**
- Max ~25 righe per funzione (regola generale, non assoluta)
- Un'unica responsabilità
- Return anticipato per early exit (riduce nesting)
- Parametri: max 3-4 (usare oggetti per payload complessi)

**Formatting:**
- Segui le convenzioni del progetto (tab/spaces, quote style)
- Blank lines per separare sezioni logiche
- Import raggruppati e ordinati (stdlib → external → internal)

### Dopo l'esecuzione
1. Esegui i test (se presenti) e verifica che passino
2. Scrivi REFACTORING_REPORT.md con:
   - Lista file modificati con breve descrizione delle modifiche
   - Eventuali deviazioni dal piano (con motivazione)
   - Eventuali test falliti (se presenti)
   - Suggerimenti per refactoring futuro non eseguiti ora
3. Elimina /tmp/refactoring-plan.md
```

---

## Fase 4 — Validazione Finale (Parent Agent)

```
1. Leggi REFACTORING_REPORT.md
2. Se i test esistono: confronta risultato baseline con risultato post-refactoring
3. Notifica l'utente con summary delle modifiche
4. Se ci sono deviazioni dal piano, segnalale esplicitamente
5. Suggerisci next steps (es: "considera di aggiungere test per X ora che il codice è più chiaro")
```

---

## Note Operative
- Il Subagent 1 NON modifica mai nulla — solo legge e pianifica
- Il Subagent 2 NON inventa modifiche non nel piano
- Se il refactoring è molto esteso (>20 file), esegui in batch per categoria
- Mai rinominare simboli pubblici (API pubblica, exports) senza conferma esplicita
- In caso di dubbio su una modifica rischiosa, documentare e saltare
