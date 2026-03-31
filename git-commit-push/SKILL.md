---
name: git-commit-push
description: >
  Esegui git commit e push su GitHub con messaggio dettagliato in formato
  Conventional Commits. Usa quando l'utente dice "committa", "fai il commit",
  "pusha", "commit e push", "salva su git", "manda su github", "committa i progressi",
  "aggiorna il repo", "push su main", "commit con messaggio", "fai il push",
  "salva le modifiche su github", "committa tutto", "git commit", "git push".
  Genera automaticamente un messaggio Conventional Commits dettagliato analizzando
  diff, plan.md e contesto di sessione. Supporta branch specificato dal prompt.
allowed-tools: Bash, Read
model: claude-sonnet-4-5
---

# Git Commit & Push — Conventional Commits con Corpo Dettagliato

## Quando Usare
- L'utente vuole committare e/o pushare il lavoro corrente
- Fine sessione o milestone completata
- Keyword trigger: "committa", "push", "salva su git", "github", "commit",
  "manda sul repo", "aggiorna il branch", "git commit", "git push"

## Obiettivo
Produrre un commit Git con:
- **Subject line** in formato Conventional Commits (max 72 caratteri)
- **Corpo** strutturato con file modificati, step completati, decisioni e comandi
- Push sul branch corretto (corrente o specificato dall'utente)
- Rispetto degli hooks `prevent-git-commit-push` già configurati

---

## Fase 1 — Raccolta Contesto

```bash
# 1. Verifica stato repository
git status
git diff --cached --stat          # file già in staging
git diff --stat                   # file modificati non ancora in staging

# 2. Ottieni il diff completo per capire cosa è cambiato
git diff --cached                 # diff staged
git diff                          # diff unstaged

# 3. Branch corrente e remote configurato
git branch --show-current
git remote -v

# 4. Leggi plan.md se esiste (per step completati e decisioni)
cat plan.md 2>/dev/null || echo "[plan.md non trovato]"

# 5. Ultimi commit per mantenere coerenza di stile
git log --oneline -5
```

---

## Fase 2 — Analisi e Costruzione del Messaggio

### Determina il tipo Conventional Commits

Scegli il tipo analizzando il diff:

| Tipo | Quando usarlo |
|------|--------------|
| `feat` | Nuova funzionalità, nuovo componente, nuova route/API |
| `fix` | Correzione di un bug, comportamento errato |
| `refactor` | Ristrutturazione codice senza cambio funzionalità |
| `docs` | Modifiche a .md, commenti, documentazione |
| `chore` | Dipendenze, config, build, script, file non-src |
| `test` | Aggiunta o modifica di test |
| `style` | Formatting, whitespace (zero logica) |
| `perf` | Ottimizzazione performance |
| `ci` | Pipeline CI/CD, GitHub Actions |

Se le modifiche coprono più tipi, scegli quello **dominante** per il subject
e dettaglia gli altri nel corpo.

### Determina lo scope (opzionale ma consigliato)

Lo scope è il modulo/area coinvolta: `feat(auth)`, `fix(checkout)`, `docs(api)`.
Ricavalo dal path dei file modificati o dal contesto del prompt utente.

### Costruisci il Subject Line

```
<tipo>(<scope>): <descrizione imperativa, presente, minuscolo>

Regole:
- Max 72 caratteri totali
- Verbo imperativo: "add", "fix", "update", "remove", "implement", "configure"
- NO maiuscola iniziale dopo i due punti
- NO punto finale
- In italiano se il progetto usa italiano, inglese altrimenti
```

Esempi corretti:
```
feat(checkout): implement Stripe Elements payment form
fix(webhook): handle idempotency key collision on retry
refactor(auth): extract token validation into separate service
docs(plan): update progress — step 3 completed
chore(deps): upgrade stripe-js to 4.2.0
```

### Costruisci il Corpo del Commit

Il corpo segue dopo una riga vuota dal subject. Include queste sezioni
**solo se hanno contenuto rilevante**:

```
<riga vuota>
## Modifiche
<lista file modificati con breve descrizione del perché>

## Step Completati
<step da plan.md marcati come completati in questa sessione>

## Decisioni Architetturali
<decisioni prese durante questa sessione — da plan.md o dal contesto>

## Comandi Rilevanti Eseguiti
<comandi non ovvi eseguiti che hanno impatto sul repo o sull'ambiente>

## Note
<informazioni aggiuntive utili per chi legge il commit in futuro>
```

**Regole per il corpo:**
- Ogni sezione è omessa se vuota (non inserire intestazioni senza contenuto)
- Lista file: raggruppa per area funzionale, non elencare tutto meccanicamente
- Max ~25 righe totali nel corpo — sii conciso ma completo
- Usa path relativi dalla root del progetto
- I comandi rilevanti sono quelli con side effect (migrazioni DB, install dipendenze,
  generazione file, setup ambiente) — NON listare `git status`, `ls`, ecc.

---

## Fase 3 — Staging e Branch

### Gestione staging

```bash
# Se l'utente ha specificato file specifici → staged solo quelli
git add <file specificati>

# Se l'utente dice "committa tutto" / non specifica → staged tutto
git add -A

# Mostra sempre il diff finale prima di procedere
git diff --cached --stat
```

### Gestione branch

**Estrai il branch dal prompt dell'utente:**
- "pusha su main" → `main`
- "pusha su develop" → `develop`
- "push sul branch feature/checkout" → `feature/checkout`
- nessun branch specificato → usa branch corrente (`git branch --show-current`)

**Verifica che il branch esista:**
```bash
# Branch corrente
CURRENT=$(git branch --show-current)

# Branch target (da prompt o corrente)
TARGET="<branch estratto>"

# Se TARGET != CURRENT, chiedi conferma esplicita all'utente prima di switchare
```

**Regola di sicurezza:** se il branch target è `main` o `master` e il branch
corrente è diverso, avvisa esplicitamente l'utente prima di procedere:
```
⚠️  Stai per pushare direttamente su [main/master].
    Branch corrente: [branch]
    Vuoi procedere o preferisci aprire una PR?
```

---

## Fase 4 — Esecuzione

L'hook `prevent-git-commit-push` bloccherà automaticamente il commit e il push
chiedendo conferma. Questo è il comportamento atteso — la skill prepara il
comando, l'hook garantisce la doppia conferma umana.

```bash
# Sequenza di esecuzione
git add <target>
git commit -m "<subject>" -m "<corpo formattato>"
git push origin <branch>
```

**Formato del -m per commit con corpo:**
```bash
git commit \
  -m "feat(checkout): implement Stripe Elements payment form" \
  -m "## Modifiche
src/app/checkout/page.tsx — nuova pagina checkout con layout principale
src/components/CheckoutForm.tsx — form Stripe Elements con validazione
src/components/PriceCard.tsx — card prezzi riutilizzabile
src/components/OrderSummary.tsx — riepilogo ordine pre-pagamento
src/lib/stripe.ts — inizializzazione client Stripe lato browser

## Step Completati
- Step 3: UI checkout page ✅

## Decisioni Architetturali
- Stripe Elements (non Stripe Checkout hosted) per controllo UI completo
- Pagamento one-time, no subscription per questa release

## Comandi Rilevanti Eseguiti
- npm install @stripe/stripe-js @stripe/react-stripe-js

## Note
Design di riferimento: /designs/checkout.fig
Componente Card importato da shadcn/ui"
```

---

## Fase 5 — Conferma Post-Push

Dopo l'esecuzione, mostra all'utente:

```
✅ Commit e push completati.

Branch: [branch]
Remote: [remote URL]
Commit: [hash abbreviato] — [subject]

Riepilogo:
- N file modificati
- Step completati inclusi nel messaggio: [lista]
- Prossimo step: [da plan.md se disponibile]
```

---

## Casi Speciali

**Solo commit, no push:**
Trigger: "committa ma non pushare", "solo commit", "commit locale"
→ Esegui solo `git add` + `git commit`, salta il push

**Solo push:**
Trigger: "pusha", "manda su github", "push" (senza "commit")
→ Verifica che ci siano commit da pushare (`git log origin/<branch>..HEAD`)
→ Se sì, esegui solo il push
→ Se no, avvisa l'utente che non ci sono commit locali da pushare

**Repository non inizializzato:**
→ Avvisa l'utente: "Questo progetto non ha un repository git.
   Vuoi che esegua `git init` e configuri il remote?"
   NON inizializzare autonomamente senza conferma.

**Working tree pulito (nulla da committare):**
→ Avvisa: "Nessuna modifica da committare. Working tree pulito."
→ Se l'utente vuole pushare comunque, verifica commit locali non pushati.

**Conflitti o push rejected:**
→ Non fare force push autonomamente
→ Mostra l'errore e suggerisci le opzioni (`git pull --rebase`, aprire una PR)
→ Attendi istruzioni esplicite dall'utente

---

## Note Operative
- Il subject line deve essere in inglese se il resto del progetto usa inglese,
  italiano se il progetto è in italiano — segui la convenzione dei commit esistenti
- Non includere mai secrets, token o credenziali nel commit message
- Se plan.md non esiste, ometti semplicemente le sezioni "Step Completati"
  e "Decisioni Architetturali"
- L'hook `prevent-git-commit-push` è il safety net finale — non bypassarlo
