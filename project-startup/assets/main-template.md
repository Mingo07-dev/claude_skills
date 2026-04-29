# .agent/main.md

## Scopo e obiettivo del progetto
- <scopo sintetico>
- <obiettivo misurabile>

## Funzionamento di alto livello
- <flusso principale>
- <componenti chiave>

## Regole operative
- Se il prompt richiede un minor bug fix o una modifica piccola (es. colore di un bottone), NON salvare un piano in .agent/plans/.
- Per task multi-step o che richiedono ragionamento profondo, leggi .agent/planning.md ed esegui le istruzioni contenute; salva poi il piano in .agent/plans/.
- A ogni prompt, fai domande se mancano informazioni utili o indispensabili, anche se l'utente non lo ha richiesto.
- Se prevedi modifiche che possono alterare le info in .agent/main.md, aggiorna il file alla fine e avvisa l'utente.
- Al primo avvio, se sono presenti repo git, salva numero e data del commit corrente e tienili aggiornati.
- Se l'utente chiede di verificare se i dati dei file .md sono aggiornati, usa il commit registrato in .agent/main.md per controllare le modifiche nei commit successivi e le modifiche non salvate; se ci sono differenze aggiorna i file .md, altrimenti aggiorna solo il commit corrente.

## Stato git
- Commit: <hash> | Data: <YYYY-MM-DD>

## Struttura codebase
- <path/>: <descrizione>

## Documentazione chiave
- <path/doc>: <cosa contiene>

## Modelli, strutture e formati
- <regole o standard da seguire>
