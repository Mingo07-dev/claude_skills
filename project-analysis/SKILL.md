---
name: project-analysis
description: >
  Analisi iniziale o aggiornamento completo del progetto. Produce o aggiorna
  CLAUDE.md e ARCHITECTURE.md con diagrammi Mermaid embedded.
  Usa quando l'utente dice "analizza il progetto", "capire la struttura",
  "onboarding", "crea CLAUDE.md", "aggiorna ARCHITECTURE.md", "mappa il codice",
  "prima di iniziare", "dammi una panoramica", "che fa questo progetto",
  "documenta l'architettura", "schema del sistema".
  Lancia un subagent con high effort per esplorazione sistematica.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-sonnet-4-5
---

# Project Analysis — High Effort con Subagent

## Quando Usare
- Inizio di una nuova sessione su un progetto sconosciuto
- CLAUDE.md o ARCHITECTURE.md assenti o obsoleti
- Dopo refactoring maggiori che cambiano la struttura
- Keyword trigger: "analizza", "panoramica", "struttura", "architettura",
  "onboarding", "CLAUDE.md", "ARCHITECTURE.md", "come funziona"

## Obiettivo
Produrre o aggiornare due file:
- `CLAUDE.md` — memoria operativa per Claude Code (comandi, convenzioni, contesto)
- `ARCHITECTURE.md` — documentazione tecnica con diagrammi Mermaid embedded

---

## Fase 1 — Ricognizione Rapida (Parent Agent)

```
1. Leggi i file di configurazione radice:
   - package.json / pyproject.toml / Cargo.toml / go.mod / pom.xml
   - .env.example, docker-compose.yml, Dockerfile
   - README.md (se esiste)
   - CLAUDE.md esistente (se esiste — per capire cosa già si sa)

2. Mappa la struttura directory (max 3 livelli):
   find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' \
          -not -path '*/dist/*' -not -path '*/__pycache__/*' \
          -not -path '*/venv/*' | head -100

3. Identifica:
   - Linguaggio/i principali
   - Framework (React, FastAPI, Express, Django, Rails, Spring, ecc.)
   - Database (PostgreSQL, MongoDB, Redis, SQLite, ecc.)
   - Pattern architetturale (MVC, microservizi, monorepo, serverless, ecc.)
   - Tool di build/test/lint presenti
   - Script npm/make/just disponibili

4. Passa tutto il contesto al subagent
```

## Fase 2 — Analisi Approfondita (Subagent)

Lancia un subagent con il seguente task:

```
Task al subagent:

Sei un software architect esperto. Devi analizzare in profondità questo progetto
e produrre documentazione tecnica precisa e utile.

CONTESTO RACCOLTO DAL PARENT:
[contesto fase 1]

IL TUO COMPITO — esegui in ordine:

### STEP 1 — Analisi Entry Point e Flussi
- Identifica i file main/index/app (entry point dell'applicazione)
- Traccia i flussi principali (request lifecycle, pipeline di dati, ecc.)
- Mappa le API/routes se presenti
- Identifica i modelli di dati core

### STEP 2 — Dipendenze e Integrazioni
- Dipendenze principali e loro ruolo
- Servizi esterni integrati (API, DB, queue, cache)
- Variabili d'ambiente richieste (da .env.example o menzioni nel codice)

### STEP 3 — Convenzioni e Pattern
- Naming conventions (camelCase, snake_case, ecc.)
- Struttura dei file e cartelle (feature-based, layer-based, ecc.)
- Pattern ricorrenti (repository pattern, service layer, middleware, ecc.)
- Standard di testing (unit, integration, e2e — tool usati)

### STEP 4 — Comandi Operativi
- Come avviare in sviluppo
- Come eseguire i test
- Come buildare
- Come fare il deploy (se presente)
- Lint/format comandi

### STEP 5 — Produci i due file

#### FILE 1: CLAUDE.md
Struttura:
```markdown
# [Nome Progetto] — Claude Code Memory

## Panoramica
[1-2 righe: cosa fa il progetto, stack principale]

## Comandi Essenziali
```bash
# Sviluppo
[comando]

# Test
[comando]

# Build
[comando]

# Lint/Format
[comando]
```

## Struttura Directory
```
[albero semplificato con descrizione per ogni cartella chiave]
```

## Convenzioni
- **Naming:** [convenzione]
- **Struttura file:** [pattern]
- **Commit:** [formato se presente]
- **Test:** [pattern naming test files]

## Architettura (sintesi)
[3-5 righe che descrivono il pattern architetturale]

## File Critici
- `[path]` — [cosa fa]
- `[path]` — [cosa fa]
(max 10 file più importanti da conoscere)

## Variabili d'Ambiente Richieste
| Variabile | Descrizione | Esempio |
|-----------|-------------|---------|

## Dipendenze Chiave
| Package | Versione | Ruolo |
|---------|----------|-------|

## Note per Claude
- [gotcha 1: cosa NON fare in questo progetto]
- [gotcha 2: pattern da seguire obbligatoriamente]
- [gotcha 3: side effect / comportamento non ovvio]

## Ultima Analisi
Data: YYYY-MM-DD
```

#### FILE 2: ARCHITECTURE.md
Struttura:
```markdown
# Architettura — [Nome Progetto]

## Overview
[Descrizione architetturale in 3-5 righe]

## Stack Tecnologico
| Layer | Tecnologia | Versione |
|-------|-----------|---------|

## Diagramma Architetturale Generale

```mermaid
graph TD
    [diagramma che mostra i componenti principali e le loro relazioni]
```

## Flusso Request/Response Principale

```mermaid
sequenceDiagram
    [diagramma del flusso principale dell'applicazione]
```

## Modello Dati

```mermaid
erDiagram
    [entità principali e relazioni — se il progetto ha un DB]
```

## Struttura Moduli

```mermaid
graph LR
    [dipendenze tra moduli/packages principali]
```

## Flusso di Deploy (se presente)

```mermaid
graph TD
    [pipeline CI/CD o processo di deploy]
```

## Decisioni Architetturali (ADR)
### ADR-001 — [Titolo]
- **Contesto:** ...
- **Decisione:** ...
- **Conseguenze:** ...

## Interfacce Esterne
[Lista API, servizi, DB con cui il sistema comunica]

## Scalabilità e Limiti Noti
[Eventuali bottleneck o limitazioni dell'architettura attuale]
```

REGOLE PER I DIAGRAMMI MERMAID:
- Sempre embedded nel .md (non file separati)
- Usa nomi in italiano o nel linguaggio del progetto
- Mantieni i diagrammi leggibili (max 15-20 nodi per diagramma)
- Se un aspetto è sconosciuto, ometti il diagramma relativo piuttosto che inventare
- Usa graph TD per architetture, sequenceDiagram per flussi, erDiagram per dati
```

## Fase 3 — Validazione (Parent Agent)

```
1. Verifica che entrambi i file siano stati creati/aggiornati
2. Controlla che i blocchi Mermaid siano sintatticamente corretti
   (cerca eventuali errori comuni: frecce malformate, nodi senza nome)
3. Se CLAUDE.md esisteva già, confronta con la versione precedente e
   assicurati che le informazioni critiche non siano state perse
4. Notifica l'utente con un summary di cosa è stato prodotto
```

---

## Note Operative
- Se il progetto ha già CLAUDE.md e ARCHITECTURE.md, il subagent li aggiorna
  (non sovrascrive da zero — preserva le sezioni esistenti valide)
- Per progetti molto grandi, il subagent analizza prima i moduli core
- Non eseguire mai il codice durante l'analisi — solo leggere
- I diagrammi Mermaid devono riflettere il codice reale, non supposizioni
