---
name: update-docs
description: >
  Aggiorna i file di documentazione .md prima della chiusura della sessione.
  Usa quando l'utente dice "aggiorna i docs", "chiudi la sessione", "fine sessione",
  "aggiorna CLAUDE.md", "aggiorna ARCHITECTURE.md", "aggiorna plan.md",
  "salva il progresso", "prima di chiudere", "wrap up", "aggiorna la documentazione",
  "sincronizza i file md", "fine lavoro", "documenta quello che abbiamo fatto",
  "chiudiamo", "aggiorna i file prima di smettere".
  Aggiorna CLAUDE.md, ARCHITECTURE.md, plan.md e session-history.md con il contesto della sessione corrente.
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, Task
model: claude-sonnet-4-5
---

# Update Docs — Aggiornamento Fine Sessione

## Quando Usare
- Fine di una sessione di lavoro
- Prima di chiudere Claude Code
- Dopo modifiche significative al progetto
- Keyword trigger: "chiudi sessione", "fine lavoro", "aggiorna docs",
  "aggiorna CLAUDE.md", "aggiorna plan", "wrap up", "salva progresso",
  "prima di chiudere", "chiudiamo", "aggiorna la documentazione"

## Obiettivo
Aggiornare in modo accurato e conciso:
- `CLAUDE.md` — memoria operativa aggiornata con nuove scoperte
- `ARCHITECTURE.md` — riflette cambiamenti strutturali avvenuti nella sessione
- `plan.md` — task completati, in corso, e prossimi passi
- `session-history.md` — log cronologico delle sessioni di lavoro

---

## Fase 1 — Raccolta Contesto Sessione (Parent Agent)

```
1. Recupera la conversazione della sessione corrente per identificare:
   - Cosa è stato implementato/modificato
   - Problemi riscontrati e come sono stati risolti
   - Decisioni tecniche prese
   - Task completati
   - Task rimasti in sospeso o nuovi task emersi

2. Leggi i file correnti (se esistono):
   - CLAUDE.md
   - ARCHITECTURE.md
   - plan.md
   - session-history.md

3. Leggi i file modificati nella sessione:
   git diff --name-only HEAD 2>/dev/null || \
   find . -newer CLAUDE.md -name "*.ts" -o -newer CLAUDE.md -name "*.py" \
          -o -newer CLAUDE.md -name "*.js" -o -newer CLAUDE.md -name "*.go" \
          2>/dev/null | grep -v node_modules | grep -v .git | head -30

4. Passa il contesto al subagent
```

---

## Fase 2 — Aggiornamento (Subagent)

Lancia un subagent con il seguente task:

```
Sei responsabile di mantenere aggiornata la documentazione di progetto.
Devi aggiornare tre file .md riflettendo il lavoro della sessione corrente.

CONTESTO SESSIONE:
[cosa è stato fatto, modificato, deciso nella sessione]

FILE MODIFICATI IN QUESTA SESSIONE:
[lista file]

CONTENUTO ATTUALE DEI FILE:
[contenuto CLAUDE.md, ARCHITECTURE.md, plan.md, session-history.md]

---

### TASK 1: Aggiorna CLAUDE.md

Regole di aggiornamento:
- NON riscrivere da zero — aggiorna le sezioni che cambiano
- AGGIUNGI nuove scoperte, non sovrascrivere quelle valide
- AGGIORNA la data "Ultima Analisi/Aggiornamento" in fondo

Sezioni da aggiornare se necessario:

**Comandi Essenziali:**
Se sono stati usati nuovi comandi o se ne sono aggiornati, aggiorna questa sezione.

**Struttura Directory:**
Se sono state aggiunte/rimosse cartelle o file chiave, aggiorna l'albero.

**Convenzioni:**
Se sono state adottate nuove convenzioni o pattern, documentali.

**File Critici:**
Se nuovi file importanti sono stati creati, aggiungili.

**Note per Claude (IMPORTANTE):**
Questa è la sezione più utile da mantenere. Aggiungi:
- Gotcha scoperti durante la sessione ("attenzione: X causa Y")
- Pattern emersi che Claude deve seguire
- Comportamenti non ovvi del sistema
- Errori ricorrenti da evitare
- Dipendenze implicite scoperte

Formato voce:
`- [SCOPERTO YYYYMMDD] nome-del-gotcha: descrizione concisa`

**Variabili d'Ambiente:**
Se sono state scoperte/aggiunte variabili, aggiorna la tabella.

**Ultima Sessione:**
Aggiungi una sezione (o aggiorna quella esistente):
```
## Ultima Sessione
Data: YYYY-MM-DD
Attività: [elenco puntato di cosa è stato fatto]
Stato: [In progress / Completato / Bloccato su X]
```

---

### TASK 2: Aggiorna ARCHITECTURE.md

Regole di aggiornamento:
- Aggiorna SOLO se ci sono cambiamenti architetturali reali
- NON aggiornare per piccole modifiche implementative
- Aggiorna i diagrammi Mermaid se la struttura è cambiata

Trigger per aggiornamento:
- Nuovi moduli/componenti aggiunti
- Cambio di pattern architetturale
- Nuove integrazioni esterne
- Refactoring strutturale significativo
- Cambio di stack tecnologico

Se nessun cambiamento architetturale è avvenuto, scrivi:
`[ARCHITECTURE.md non necessita aggiornamenti questa sessione]`

Se ci sono cambiamenti, aggiorna:
- Il diagramma architetturale generale (se necessario)
- Le sezioni coinvolte
- Eventuali nuove ADR (Architectural Decision Records)

---

### TASK 3: Aggiorna plan.md

Questo è il file più importante da aggiornare ogni sessione.

Se plan.md non esiste, crealo con questo template:

```markdown
# Plan — [Nome Progetto]
**Ultimo aggiornamento:** YYYY-MM-DD

## ✅ Completati
[task completati, in ordine cronologico]

## 🔄 In Corso
[task attualmente in lavorazione]

## 📋 Prossimi Task
[task pianificati in ordine di priorità]

## 🚧 Bloccati
[task bloccati con motivo]

## 💡 Idee / Backlog
[idee, miglioramenti futuri, non prioritizzati]
```

Se plan.md esiste già, aggiornalo:

**Sposta nella sezione "✅ Completati":**
Ogni task menzionato nella sessione come completato.
Formato: `- [YYYY-MM-DD] descrizione del task completato`

**Aggiorna "🔄 In Corso":**
- Rimuovi task che sono stati completati
- Aggiungi task iniziati ma non finiti
- Aggiorna lo stato di quelli esistenti

**Aggiorna "📋 Prossimi Task":**
- Aggiungi nuovi task emersi durante la sessione
- Riordina per priorità se necessario
- Rimuovi task che non sono più rilevanti

**Aggiorna "🚧 Bloccati":**
- Aggiungi task che si sono rivelati bloccati (con motivo)
- Rimuovi blocchi che sono stati risolti

**Formato task in Prossimi Task:**
```
- [ ] Descrizione chiara del task
      Priorità: ALTA/MEDIA/BASSA
      Contesto: [perché è necessario, dipendenze]
```

---

### TASK 4: Aggiorna session-history.md

Questo file mantiene un log cronologico di tutte le sessioni di lavoro.

**Struttura di una entry:**
```markdown
## Sessione YYYY-MM-DD — [titolo sintetico, max 60 char]

**Obiettivo della sessione:** [cosa si voleva fare]

**Fatto:**
- [azione concreta 1 — con path/componente se rilevante]
- [azione concreta 2]
- ...

**Decisioni prese:**
- [decisione + motivazione breve] (ometti se nessuna)

**Blocchi incontrati:**
- [blocco + come risolto o lasciato aperto] (ometti se nessuno)

**Stato al termine:** [avanzamento: N/M step, X% — oppure descrizione libera]

**Prossimo step:** [titolo e breve descrizione del prossimo step]

---
```

Regole di aggiornamento:
- Le entry sono in ordine **cronologico inverso** (più recente in cima)
- Se session-history.md non esiste, crealo con header:
  `# Session History — [Nome Progetto]`
- Inserisci la nuova entry subito dopo l'header
- Le entry precedenti rimangono intatte sotto
- Il titolo deve essere sintetico e descrivere il tema principale della sessione
- "Fatto" va ricavato dal contesto della sessione: commit git, file modificati, attività discusse
- "Decisioni prese" e "Blocchi incontrati": ometti le sezioni se vuote

---

OUTPUT:
1. File CLAUDE.md aggiornato
2. File ARCHITECTURE.md aggiornato (o nota che non serve)
3. File plan.md aggiornato
4. File session-history.md aggiornato con la nuova entry
5. Stampa un summary di cosa hai modificato in ogni file
```

---

## Fase 3 — Conferma (Parent Agent)

```
1. Verifica che i quattro file siano stati aggiornati
2. Stampa all'utente un summary:
   "✅ Documentazione aggiornata:
   - CLAUDE.md: [cosa è cambiato]
   - ARCHITECTURE.md: [cosa è cambiato / 'nessuna modifica necessaria']
   - plan.md: [N task completati, N nuovi task aggiunti, N in corso]
   - session-history.md: [sessione YYYY-MM-DD aggiunta — titolo]"
3. Se plan.md contiene task BLOCCATI, segnalali esplicitamente
```

---

## Note Operative
- Non modificare mai sezioni di CLAUDE.md che sembrano valide e accurate
- Non eliminare task da plan.md — spostarli in "Completati" o "Backlog"
- I diagrammi Mermaid in ARCHITECTURE.md vanno aggiornati solo se necessario
  (aggiornamenti inutili creano rumore)
- Se un file non esiste ancora, il subagent lo crea partendo dai template
- La sezione "Note per Claude" in CLAUDE.md è la più preziosa: mantenerla accurata
