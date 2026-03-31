---
name: plan-manager
description: >
  Crea o aggiorna il file plan.md a partire dal prompt dell'utente.
  Usa quando l'utente dice "aggiorna il plan", "aggiungi uno step al plan",
  "segna come completato", "nuovo task", "aggiorna il piano", "step completato",
  "aggiungi al plan", "modifica il plan", "crea il plan", "inizializza il plan",
  "step in corso", "blocco sul plan", "rischio", "decisione architetturale",
  "aggiorna obiettivo", "sposta step", "riordina task", "prossimo step",
  "cosa devo fare dopo", "aggiorna stato", "ho finito lo step".
  Legge il plan.md esistente, applica le modifiche richieste e lo riscrive.
allowed-tools: Read, Write, Edit, Bash
model: claude-opus-4-5
---

# Plan Manager — Crea e Aggiorna plan.md

## Quando Usare
- L'utente vuole creare un piano di progetto da zero
- L'utente vuole aggiornare step, stati, decisioni o note nel plan esistente
- Fine sessione (in combo con update-docs)
- Keyword trigger: "plan", "step", "completato", "in corso", "blocco",
  "rischio", "decisione", "prossimo task", "cosa faccio dopo", "aggiorna il piano"

## Obiettivo
Mantenere `plan.md` come **fonte di verità operativa** della sessione:
preciso, leggibile, sempre aggiornato, azionabile al prossimo avvio.

---

## Struttura Canonica di plan.md

Questa è la struttura ottimale che la skill crea e mantiene:

```markdown
# plan.md — [Nome Progetto]

## 🎯 Obiettivo
[Descrizione chiara dell'obiettivo principale + scadenza se presente]
Scadenza: YYYY-MM-DD

---

## 📊 Stato Avanzamento
Last updated: YYYY-MM-DD HH:MM

| Fase | Step | Stato | Note |
|------|------|--------|------|
| [Fase] | Step 1: [titolo] | ✅ Completato | [nota opzionale] |
| [Fase] | Step 2: [titolo] | 🔄 In corso | [dettaglio] |
| [Fase] | Step 3: [titolo] | ⏳ Da fare | |
| [Fase] | Step 4: [titolo] | 🚫 Bloccato | [motivo blocco] |
| [Fase] | Step 5: [titolo] | 💡 Idea/Backlog | |

**Avanzamento:** N/M step completati (X%)

---

## 🔜 Prossimo Step
**Step N — [Titolo]**
[Descrizione concisa di cosa fare]

File/componenti coinvolti:
- `path/to/file.ext` — [perché]
- `path/to/other.ext` — [perché]

Acceptance criteria:
- [ ] [criterio 1]
- [ ] [criterio 2]

---

## 🏗️ Decisioni Architetturali
| # | Decisione | Motivazione | Data |
|---|-----------|-------------|------|
| 1 | [cosa] | [perché] | YYYY-MM-DD |

---

## 🚧 Blocchi e Rischi
| Tipo | Descrizione | Impatto | Azione |
|------|-------------|---------|--------|
| BLOCCO | [cosa blocca] | [impatto] | [cosa fare] |
| RISCHIO | [cosa potrebbe andare male] | [impatto] | [mitigazione] |

---

## 📝 Note per la Prossima Sessione
- [nota operativa 1 — concreta e azionabile]
- [nota operativa 2]

---

## 📋 Backlog
- [ ] [idea/task futura non prioritizzata]
```

---

## Logica di Aggiornamento

### Operazioni supportate (riconoscile dal prompt dell'utente):

**1. Crea plan.md da zero**
Trigger: "crea il plan", "inizializza il piano", plan.md non esiste
→ Chiedi all'utente (se non lo ha specificato): obiettivo, scadenza, lista step iniziali
→ Costruisci la struttura canonica completa

**2. Segna step come completato**
Trigger: "ho finito lo step N", "step N completato", "segna X come fatto"
→ Cambia stato da 🔄/⏳ a ✅ Completato
→ Aggiorna "Prossimo Step" con lo step successivo non completato
→ Ricalcola avanzamento percentuale
→ Aggiorna "Last updated"

**3. Segna step come in corso**
Trigger: "sto lavorando su X", "step N in corso", "ho iniziato X"
→ Cambia stato a 🔄 In corso
→ Aggiorna "Prossimo Step" se è quello corrente
→ Aggiorna "Last updated"

**4. Aggiungi nuovo step**
Trigger: "aggiungi step", "nuovo task", "ho scoperto che devo anche fare X"
→ Inserisci nella tabella nella posizione giusta (in fondo alla fase, o dove indicato)
→ Assegna numero progressivo corretto
→ Stato iniziale: ⏳ Da fare (o quello indicato dall'utente)

**5. Segna step come bloccato**
Trigger: "sono bloccato su X", "blocco su Y", "non riesco a procedere con Z"
→ Cambia stato a 🚫 Bloccato
→ Aggiungi riga nella tabella "Blocchi e Rischi" con motivo e azione suggerita
→ Aggiorna "Prossimo Step" con lo step successivo non bloccato

**6. Aggiungi decisione architetturale**
Trigger: "ho deciso di usare X", "decisione: Y", "architetturalmente abbiamo scelto"
→ Aggiungi riga nella tabella "Decisioni Architetturali"
→ Includi data odierna

**7. Aggiungi nota per la prossima sessione**
Trigger: "ricorda che", "nota importante", "nella prossima sessione", "non dimenticare"
→ Aggiungi bullet in "Note per la Prossima Sessione"
→ Formulazione: concreta, azionabile, con path specifici se rilevanti

**8. Aggiungi rischio**
Trigger: "rischio", "potrebbe essere un problema", "attenzione a", "potremmo avere problemi con"
→ Aggiungi riga nella tabella "Blocchi e Rischi" con tipo RISCHIO

**9. Sposta step in backlog**
Trigger: "questo non è prioritario", "metti nel backlog", "per dopo"
→ Cambia stato a 💡 Idea/Backlog (o sposta in sezione Backlog)

**10. Aggiorna obiettivo o scadenza**
Trigger: "cambia la scadenza", "aggiorna l'obiettivo", "la deadline è"
→ Aggiorna la sezione 🎯 Obiettivo

---

## Regole di Scrittura

**Stile:**
- Ogni step deve avere un titolo chiaro e un verbo d'azione (Implementare, Creare, Configurare, Testare)
- Le note devono essere concrete: includere path di file, nomi componenti, comandi specifici
- Le decisioni devono avere una motivazione (anche breve)
- I blocchi devono avere un'azione suggerita, non solo la descrizione del problema

**Avanzamento percentuale:**
```
Avanzamento = (step ✅) / (step ✅ + step 🔄 + step ⏳ + step 🚫) × 100
Non contare i 💡 Backlog nel denominatore
```

**"Prossimo Step":**
- È sempre il primo step 🔄 (in corso), oppure il primo ⏳ se nessuno è in corso
- Deve essere sufficientemente dettagliato da permettere di riprendere senza rileggere tutto
- Include sempre i file/componenti coinvolti e i criteri di accettazione

**"Last updated":**
- Aggiorna sempre al timestamp corrente ad ogni modifica
- Formato: YYYY-MM-DD (senza orario è sufficiente)

---

## Workflow di Esecuzione

```
1. Leggi plan.md esistente (se presente)

2. Interpreta il prompt dell'utente e identifica l'operazione/i da eseguire
   (possono essere multiple: es. "segna step 3 come fatto e aggiungi step 6")

3. Applica le modifiche mantenendo la struttura canonica

4. Ricalcola:
   - Avanzamento percentuale
   - "Prossimo Step" corretto
   - "Last updated"

5. Riscrivi plan.md con le modifiche

6. Conferma all'utente in chat:
   "[operazione eseguita] → plan.md aggiornato.
    Avanzamento: N/M (X%)
    Prossimo step: [titolo]"
```

---

## Migrazione da Template Minimo

Se il plan.md esistente ha una struttura semplice (checklist senza tabelle),
convertila nella struttura canonica **preservando tutti i contenuti**:

- `- [x] Step N: titolo` → riga tabella con ✅ Completato
- `- [ ] Step N: titolo` → riga tabella con ⏳ Da fare
- `- [ ] Step N: titolo (in corso)` → riga tabella con 🔄 In corso
- Sezione "Blocchi e Rischi" come testo → tabella strutturata
- Sezione "Decisioni" come lista → tabella con data odierna

Chiedi conferma prima di migrare se la struttura esistente è significativamente diversa.

---

## Esempio

**Prompt utente:** "Ho finito lo step 3, sto iniziando il 4. Aggiungi anche una nota: usare la env var STRIPE_WEBHOOK_SECRET dal .env.local"

**Azioni:**
1. Step 3 → ✅ Completato
2. Step 4 → 🔄 In corso
3. "Prossimo Step" aggiornato a Step 4 con dettagli
4. Aggiunta nota: "Usare `STRIPE_WEBHOOK_SECRET` da `.env.local` per il webhook handler"
5. Avanzamento ricalcolato
6. Last updated aggiornato

**Risposta in chat:**
```
✅ plan.md aggiornato:
- Step 3 (UI checkout page) → Completato
- Step 4 (Email conferma pagamento) → In corso
- Nota aggiunta su STRIPE_WEBHOOK_SECRET

Avanzamento: 3/5 (60%)
Prossimo step: Step 4 — Email conferma pagamento
```
