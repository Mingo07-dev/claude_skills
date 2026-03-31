---
name: test-generator
description: >
  Genera ed esegue test automatici (unit, integration, E2E, API) adattandosi
  automaticamente al linguaggio e al framework del progetto.
  Usa quando l'utente dice "genera i test", "scrivi i test", "aggiungi test",
  "crea unit test", "test per questa funzione", "integration test", "E2E test",
  "API test", "coverage bassa", "mancano i test", "testa questo modulo",
  "scrivi i test per X", "ho bisogno di test", "aggiungi test coverage",
  "test per il checkout", "test per l'autenticazione", "voglio testare X".
  Pipeline tre subagent: analisi stack → generazione test → esecuzione con report.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task
model: claude-sonnet-4-5
---

# Test Generator — Pipeline Tre Subagent

## Quando Usare
- Mancano test per funzionalità nuove o esistenti
- Coverage insufficiente su moduli critici
- Prima di un refactoring (test come safety net)
- Dopo l'implementazione di una feature
- Keyword trigger: "test", "unit test", "integration", "E2E", "coverage",
  "testa", "scrivi test", "genera test", "mancano test"

## Obiettivo
Generare test contestuali e realistici — adattati al linguaggio, framework
e convenzioni del progetto — e poi eseguirli con report dettagliato,
previa conferma esplicita dell'utente.

---

## Tipi di Test Supportati

| Tipo | Scope | Esempi framework |
|------|-------|-----------------|
| **Unit** | Funzione/classe singola, mock dipendenze | Jest, Vitest, pytest, go test, RSpec |
| **Integration** | Più moduli insieme, DB reale o in-memory | Jest + Supertest, pytest + SQLAlchemy |
| **E2E** | Flusso utente completo, browser reale | Playwright, Cypress, Selenium |
| **API** | Endpoint HTTP, request/response | Supertest, httpx, rest-assured |

---

## Pipeline Overview

```
Parent Agent
    │
    ├─► Subagent 1: STACK ANALYZER
    │   - Rileva linguaggio, framework di test, convenzioni esistenti
    │   - Mappa i file da testare e lo scope richiesto
    │   - Produce /tmp/test-context.md
    │
    ├─► Subagent 2: TEST GENERATOR
    │   - Riceve il contesto dallo Subagent 1
    │   - Genera i file di test per ogni tipo richiesto
    │   - Scrive i file nelle posizioni corrette del progetto
    │   - NON esegue nulla
    │
    [⏸ PAUSA — mostra test generati, chiede conferma prima di eseguire]
    │
    └─► Subagent 3: TEST RUNNER
        - Riceve lista file di test generati
        - Esegue ogni suite con il comando corretto
        - Raccoglie output e produce TEST_REPORT.md
```

---

## Fase 1 — Ricognizione (Parent Agent)

```bash
# 1. Identifica lo scope dal prompt utente:
#    - File/funzione specifica ("testa la funzione validatePayment")
#    - Modulo/directory ("test per src/auth/")
#    - Tipo specifico ("integration test per le API")
#    - Generico ("genera i test che mancano")

# 2. Mappa il progetto
cat package.json 2>/dev/null        # JS/TS: dipendenze e scripts test
cat pyproject.toml 2>/dev/null      # Python: tool.pytest, coverage
cat go.mod 2>/dev/null              # Go
cat Cargo.toml 2>/dev/null          # Rust
cat pom.xml 2>/dev/null             # Java/Kotlin Maven
cat build.gradle 2>/dev/null        # Java/Kotlin Gradle

# 3. Cerca test esistenti per capire le convenzioni
find . -type f \( \
  -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" \
  -o -name "*.spec.ts" -o -name "*.spec.tsx" -o -name "*.spec.js" \
  -o -name "test_*.py" -o -name "*_test.go" -o -name "*_test.rs" \
  -o -name "*Spec.java" -o -name "*Test.java" \
\) -not -path "*/node_modules/*" -not -path "*/.git/*" \
| head -20

# 4. Leggi 2-3 test esistenti come riferimento stilistico
# 5. Leggi CLAUDE.md per convenzioni progetto
```

---

## Fase 2 — Subagent 1: STACK ANALYZER

```
Sei un senior engineer. Analizza il progetto per determinare il contesto
tecnico completo necessario a generare test corretti e contestuali.

SCOPE RICHIESTO: [file/modulo/tipo indicato dall'utente]
CONTESTO PROGETTO: [output della ricognizione]

DETERMINA:

### A. Stack di Test Rilevato

**Linguaggio principale:** [TypeScript / JavaScript / Python / Go / Rust / Java / ...]

**Framework di test:**
Cerca in questo ordine:
- package.json → "jest", "vitest", "mocha", "jasmine" nelle devDependencies
- pyproject.toml / setup.cfg → pytest, unittest
- go.mod → testing standard library
- Cargo.toml → #[cfg(test)]
- pom.xml / build.gradle → JUnit, TestNG

**Framework E2E (se applicabile):**
- "playwright", "@playwright/test", "cypress", "selenium-webdriver"

**Librerie di assertion/mock:**
- Jest: expect + jest.mock() built-in
- Vitest: expect + vi.mock() built-in
- pytest: assert nativo + pytest-mock / unittest.mock
- Go: testify/assert o standard testing
- Java: AssertJ, Mockito

**Comandi di esecuzione test:**
Cerca in package.json "scripts" → test, test:unit, test:e2e, test:coverage
oppure Makefile, justfile, pyproject.toml [tool.pytest]

**Directory convenzione per i test:**
- Co-located: __tests__/ accanto ai file sorgente
- Separata: /tests, /test, /spec
- Go: stesso package con _test.go
- Python: tests/ o test/ nella root

**Pattern naming file di test:**
- [nome].test.ts / [nome].spec.ts
- test_[nome].py
- [nome]_test.go

### B. File da Testare

Per ogni file nello scope, analizza:
- Funzioni/metodi pubblici esportati (questi vanno testati)
- Dipendenze esterne (da mockare: DB, API, filesystem, timer)
- Complessità: quante branch/path logici ha ogni funzione
- Dati di input/output attesi
- Edge case ovvi (null, vuoto, valori limite, errori)

### C. Infrastruttura Test Esistente

Cerca:
- File di setup/teardown: jest.setup.ts, conftest.py, TestMain in Go
- Mock globali o fixtures esistenti
- Factory functions o test builders
- Helper di test custom (renderWithProviders, createTestDb, ecc.)
- Variabili d'ambiente per i test (.env.test)
- Database di test configurato (SQLite in-memory, testcontainers, ecc.)

### D. Coverage Attuale (se misurabile)

```bash
# JS/TS con Jest
npx jest --coverage --coverageReporters=text-summary 2>/dev/null | tail -10

# Python
python -m pytest --co -q 2>/dev/null | tail -5

# Go
go test ./... -cover 2>/dev/null | grep -E "coverage|ok|FAIL"
```

OUTPUT: scrivi tutto in /tmp/test-context.md con questa struttura:
- Stack tecnico rilevato
- Comandi di esecuzione per tipo di test
- File da testare con analisi funzioni/edge case
- Infrastruttura esistente riutilizzabile
- Coverage attuale (se disponibile)
- Convenzioni naming e posizione file di test
```

---

## Fase 3 — Subagent 2: TEST GENERATOR

```
Sei un senior engineer specializzato in testing. Devi generare test
completi, realistici e immediatamente eseguibili.

CONTESTO: leggi /tmp/test-context.md
SCOPE: [tipo di test e file richiesti dall'utente]

PRINCIPI DI GENERAZIONE:

### Qualità dei test
- Ogni test deve avere un nome descrittivo che spiega COSA testa e PERCHÉ
  Pattern: "should [comportamento atteso] when [condizione]"
  Esempio: "should return null when user email is not found"
- Un test = un'asserzione concettuale (può avere più expect se logicamente legati)
- Usa i dati realistici del dominio (non "foo", "bar", "test123")
- Mock solo le dipendenze esterne — non mockare la logica che stai testando
- Ogni suite deve avere setup/teardown appropriato se necessario

### Struttura per tipo di test

#### UNIT TEST
Focus: una funzione/classe in isolamento.
- Importa solo il file target
- Mocka tutte le dipendenze esterne (DB, API, filesystem, timer, random)
- Testa: happy path, edge case, error case, valori limite
- Per ogni funzione pubblica: minimo 3-5 test case

Struttura Jest/Vitest:
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest' // o jest
import { nomeModulo } from '../path/to/module'

describe('NomeModulo', () => {
  describe('nomeMetodo', () => {
    it('should [comportamento] when [condizione happy path]', () => { ... })
    it('should [comportamento] when [input vuoto/null]', () => { ... })
    it('should throw [errore] when [condizione errore]', () => { ... })
    it('should [comportamento] when [valore limite]', () => { ... })
  })
})
```

Struttura pytest:
```python
import pytest
from unittest.mock import Mock, patch
from path.to.module import nome_funzione

class TestNomeFunzione:
    def test_should_[comportamento]_when_[condizione](self):
        ...

    def test_should_raise_[errore]_when_[condizione](self):
        with pytest.raises(ValueError):
            ...
```

#### INTEGRATION TEST
Focus: più moduli che collaborano, con infrastruttura reale o in-memory.
- Database: usa DB in-memory (SQLite) o testcontainers se disponibile
- HTTP: usa server reale su porta random o mock server
- Setup: crea dati di test nel beforeAll/setup_method
- Teardown: pulizia dati dopo ogni test (rollback transazione o truncate)
- Testa flussi completi: creazione → lettura → aggiornamento → eliminazione

```typescript
// Esempio integration test con DB in-memory
describe('UserRepository Integration', () => {
  let db: TestDatabase

  beforeAll(async () => { db = await createTestDatabase() })
  afterAll(async () => { await db.destroy() })
  afterEach(async () => { await db.truncate('users') })

  it('should persist and retrieve user correctly', async () => { ... })
})
```

#### API TEST (endpoint HTTP)
Focus: request/response degli endpoint reali.
- Usa supertest (Node), httpx (Python), net/http/httptest (Go)
- Testa: status code, struttura risposta, headers, casi di errore
- Include: autenticazione (token valido, token scaduto, non autenticato)
- Include: validazione input (body malformato, campi mancanti, tipi errati)
- Include: casi limite (risorsa non trovata, conflitto, payload troppo grande)

```typescript
// Esempio con supertest
describe('POST /api/payments', () => {
  it('should return 201 with payment id when payload is valid', async () => {
    const res = await request(app)
      .post('/api/payments')
      .set('Authorization', `Bearer ${testToken}`)
      .send({ amount: 1000, currency: 'eur', ... })
    expect(res.status).toBe(201)
    expect(res.body).toMatchObject({ id: expect.any(String) })
  })

  it('should return 401 when authorization header is missing', async () => { ... })
  it('should return 400 when amount is negative', async () => { ... })
  it('should return 422 when currency is not supported', async () => { ... })
})
```

#### E2E TEST
Focus: flusso utente completo nel browser reale (Playwright/Cypress).
- Testa solo i flussi critici del business (login, checkout, signup)
- Usa page object model per evitare duplicazione selettori
- Usa test fixtures per stato iniziale (utente loggato, carrello popolato)
- Evita sleep/wait fissi — usa waitForSelector, waitForResponse
- Snapshot: usa solo per componenti stabili

```typescript
// Esempio Playwright con Page Object
test('user can complete checkout flow', async ({ page }) => {
  await page.goto('/checkout')
  await page.getByRole('button', { name: 'Paga ora' }).click()
  await page.getByLabel('Numero carta').fill('4242424242424242')
  // ...
  await expect(page.getByText('Pagamento confermato')).toBeVisible()
})
```

### Dove salvare i file
Rispetta la convenzione rilevata da Subagent 1.
Se co-located: `src/components/__tests__/ComponentName.test.ts`
Se separata: `tests/unit/componentName.test.ts`
Se Go: stesso package, file `nome_test.go`

### Output atteso
Per ogni file di test generato, annota in /tmp/test-manifest.md:
- Path del file generato
- Tipo di test (unit/integration/E2E/API)
- Funzioni/endpoint coperti
- Numero di test case generati
- Comando per eseguire solo questa suite
```

---

## Fase 4 — Pausa e Conferma (Parent Agent)

Dopo che Subagent 2 ha completato, **fermati** e presenta all'utente:

```
📝 TEST GENERATI — Revisiona prima dell'esecuzione.

File creati:
  - [path] — [tipo] — N test case — copre [funzione/endpoint]
  - [path] — [tipo] — N test case — copre [funzione/endpoint]
  ...

Totale: N file, M test case

Comandi che verranno eseguiti:
  Unit:        [comando]
  Integration: [comando]
  E2E:         [comando]
  API:         [comando]

Puoi aprire i file generati per revisione prima di procedere.

Vuoi che esegua tutti i test, solo una categoria, o preferisci
eseguirli manualmente?
```

Opzioni gestite:
- "esegui tutti" → Subagent 3 esegue tutte le suite
- "solo unit" / "solo E2E" → filtra per tipo
- "no" / "li eseguo io" → termina, i file rimangono

---

## Fase 5 — Subagent 3: TEST RUNNER

Lanciato solo dopo conferma esplicita dell'utente:

```
Sei responsabile dell'esecuzione dei test generati e della produzione
di un report leggibile.

MANIFEST TEST: leggi /tmp/test-manifest.md
SUITE DA ESEGUIRE: [indicate dall'utente]
STACK: [da /tmp/test-context.md]

### Processo di esecuzione

Per ogni suite (nell'ordine: unit → integration → API → E2E):

1. Esegui il comando con output completo
2. Cattura exit code (0 = pass, non-0 = fail)
3. Parsa l'output per estrarre: test passati, falliti, saltati, durata
4. Per ogni test fallito: estrai il messaggio di errore e lo stack trace

Gestione errori comuni:
- "Cannot find module" → dipendenza mancante, suggerisci npm install / pip install
- "Connection refused" → servizio non avviato (DB, server), segnala all'utente
- Timeout E2E → browser non disponibile o app non in esecuzione
- Syntax error nei test generati → segnala il file e la riga

### Scrittura TEST_REPORT.md

```markdown
# Test Report
**Data:** YYYY-MM-DD HH:MM
**Generati da:** claude-sonnet-4-5
**Progetto:** [nome]

## Riepilogo

| Suite | Test Totali | ✅ Passati | ❌ Falliti | ⏭️ Saltati | Durata |
|-------|------------|-----------|-----------|-----------|--------|
| Unit | N | N | N | N | Xs |
| Integration | N | N | N | N | Xs |
| API | N | N | N | N | Xs |
| E2E | N | N | N | N | Xs |
| **Totale** | **N** | **N** | **N** | **N** | **Xs** |

## ❌ Test Falliti

### [Nome test fallito]
**File:** `path/to/test.ts:42`
**Errore:**
```
[messaggio di errore]
[stack trace rilevante]
```
**Causa probabile:** [analisi del perché il test fallisce]
**Suggerimento:** [come fixare — codice o test]

---
[ripeti per ogni test fallito]

## ✅ Coverage Aggiunta
[Lista funzioni/endpoint ora coperti che prima non lo erano]

## ⚠️ Problemi di Setup Rilevati
[Es: variabili d'ambiente mancanti, servizi non raggiungibili, ecc.]

## Raccomandazioni
- [test aggiuntivi suggeriti che non sono stati generati]
- [fixture o helper comuni da estrarre]
- [configurazione CI/CD per eseguire queste suite]
```

Dopo il report, elimina /tmp/test-context.md e /tmp/test-manifest.md.
```

---

## Fase 6 — Riepilogo Finale (Parent Agent)

```
✅ Esecuzione completata.

Risultato: N/M test passati (X%)
  ✅ Unit:        N/N
  ✅ Integration: N/N
  ❌ API:         N-F/N  (F falliti)
  ✅ E2E:         N/N

[Se ci sono fallimenti:]
⚠️  F test falliti — vedi TEST_REPORT.md per dettagli e suggerimenti.

[Se tutti passano:]
🎉 Tutti i test passano. Coverage aggiunta: [lista funzioni coperte]

Prossimi step consigliati:
- [aggiungere alla CI/CD pipeline]
- [test aggiuntivi suggeriti da TEST_REPORT.md]
```

---

## Rilevamento Automatico Stack

La skill si adatta automaticamente a questi stack senza configurazione:

| Linguaggio | Framework Test | E2E | Comando Default |
|------------|---------------|-----|-----------------|
| TypeScript/JS | Jest | Playwright | `npx jest` / `npx playwright test` |
| TypeScript/JS | Vitest | Playwright | `npx vitest` |
| TypeScript/JS | Mocha | Cypress | `npx mocha` |
| Python | pytest | Playwright | `python -m pytest` |
| Python | unittest | — | `python -m unittest` |
| Go | testing std | — | `go test ./...` |
| Rust | cargo test | — | `cargo test` |
| Java | JUnit 5 | Selenium | `mvn test` / `gradle test` |
| Ruby | RSpec | Capybara | `bundle exec rspec` |

---

## Note Operative
- I test generati usano dati di dominio realistici — non placeholder generici
- Se esistono test precedenti, la skill ne legge 2-3 per allinearsi allo stile
- Per E2E: la skill verifica che l'app sia in esecuzione prima di lanciare
  Playwright/Cypress; se non lo è, avvisa l'utente invece di fallire
- I test di integrazione non toccano mai il DB di produzione —
  cercano sempre `.env.test` o configurazione di test dedicata
- Se mancano dipendenze di test (es. `@playwright/test` non installato),
  la skill lo segnala con il comando di installazione prima di procedere
- La pausa in Fase 4 è obbligatoria — non avviare il runner senza conferma
