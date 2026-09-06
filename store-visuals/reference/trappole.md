# Le trappole, e come si esce

Ognuna di queste è costata una campagna di catture o una registrazione da
rifare. Sono in ordine di quando si incontrano.

## Catture

### Un popup di primo avvio copre metà schermo

L'app gira su un'installazione pulita: tour, permessi, richiesta di
valutazione, invito a installare, consenso alle statistiche, promozioni. Ogni
funzione nuova ne aggiunge uno, e il test delle catture non lo sa.

Prima di ogni campagna:

```bash
grep -rn "SharedPreferences" lib | grep -iE "seen|asked|done|dismissed|prompt"
```

e metti tutte quelle chiavi a `true` nelle preferenze simulate del pilota.

### Su iOS le catture escono bianche

`binding.takeScreenshot` sostituisce la superficie viva con un'immagine statica:
da quel momento tutte le catture successive sono vuote. Si scatta da fuori con
`xcrun simctl io <udid> screenshot`, sincronizzandosi su un marcatore stampato
dal test.

### I dati non ci sono ancora

Con attese a tempo capita di catturare mappe senza contenuto, elenchi vuoti,
indicatori di aggiornamento. Aspetta il **provider**, non i secondi:

```dart
await container.read(datiProvider.future);
for (var i = 0; i < 60; i++) {
  if (container.read(inAggiornamentoProvider).asData?.value == false) break;
  await _hold(tester, const Duration(milliseconds: 500));
}
```

### App Check in "enforce" blocca le build di debug

Se il progetto ha App Check attivo su Firestore, una build di debug su un
dispositivo nuovo riceve `PERMISSION_DENIED` su tutto: niente contenuti dal
database. Le catture restano utilizzabili se l'app ha una sorgente locale di
riserva, ma i contenuti degli utenti (recensioni, segnalazioni) non compaiono.

Verificare lo stato prima di lamentarsi del codice:

```bash
# GET https://firebaseappcheck.googleapis.com/v1/projects/<id>/services
```

Le alternative sono registrare il token di debug in console (cambia a ogni
installazione pulita) o accettare le schermate senza contenuti di terzi.

## Emulatori Android

### L'AVD creato da riga di comando muore dopo il primo scatto

`avdmanager create avd` **senza** profilo dispositivo produce una macchina con
GPU disabilitata e heap da 32 MB: l'app muore di memoria e un fotogramma della
mappa costa oltre un secondo. Da correggere in
`~/.android/avd/<nome>.avd/config.ini`:

```ini
hw.gpu.enabled=yes
hw.gpu.mode=host
vm.heapSize=512
hw.ramSize=4096
hw.lcd.width=1080
hw.lcd.height=1920
hw.lcd.density=420
```

### L'emulatore resta `unauthorized`

Le immagini Play Store chiedono l'autorizzazione ADB con un dialogo che, senza
interazione, non viene mai accettato. Il rimedio pratico: **clonare un AVD già
autorizzato** e cambiargli la sola risoluzione.

```bash
cp -R ~/.android/avd/Base.avd ~/.android/avd/Tablet7.avd
sed 's#Base.avd#Tablet7.avd#' ~/.android/avd/Base.ini > ~/.android/avd/Tablet7.ini
# poi in config.ini: hw.lcd.width/height/density e AvdId/avd.ini.displayname
```

Avviare con `-no-snapshot-load` (non `-no-snapshot`): l'autorizzazione sta in
`/data`, e cancellandola si ricomincia da capo.

### `adb` non si trova

Gli script che lo invocano per nome falliscono se il PATH non contiene
`platform-tools`. Esportalo, oppure usa percorsi assoluti.

## Video

### Un mirino tondo con la croce a ogni tocco

Lo disegna il binding dei test per gli eventi con sorgente `test`
(`handlePointerEvent` in `flutter_test/src/binding.dart`) e non c'è un
interruttore. Usa la sorgente **device**:

```dart
tester.binding.shouldPropagateDevicePointerEvents = true;
tester.binding.handlePointerEventForSource(
  PointerDownEvent(pointer: 42, position: p, timeStamp: _clock.elapsed),
  source: TestBindingEventSource.device,
);
```

Per l'app sono eventi veri (ondine, velocità del trascinamento, fisica dei
pannelli), per il binding non esistono. **Rimetti il flag a `false`** prima
della fine, o il test finisce in errore.

### Una schermata rossa d'errore in mezzo al filmato

Succede chiamando `.of(context)` (che registra una dipendenza) mentre si
attraversa l'albero dei widget: il framework se ne accorge
(`ancestor == this is not true`) e sostituisce il sottoalbero con
`ErrorWidget`. Se ti serve un controller, **leggilo dal widget**:

```dart
tester.widget<FlutterMap>(find.byType(FlutterMap)).mapController!
```

### La scheda si apre dal fondo

Con un `NestedScrollView` le schede condividono la posizione di scorrimento:
arrivando da una scheda scorsa in fondo, la successiva si apre a metà. Riporta
la posizione a zero prima di cambiare scheda.

### Un pannello modale che non si chiude

`Navigator.maybePop()` non sempre chiude un foglio modale (dipende da quale
navigator lo ospita). Chiudilo come farebbe un utente: **un tocco sulla
barriera**, sopra il pannello. E verifica che sia sparito prima di andare
avanti, altrimenti il tocco successivo finisce su un comando del foglio.

### Il pannello si apre due volte

Se il tocco è vero, l'azione la fa l'app: chiamare **anche** la funzione che
apre il pannello lo apre due volte, e alla chiusura sembra che l'app si incarti.
Con i gesti "device" i comandi programmatici vanno tolti.

### `date +%s%3N` su macOS

Stampa `1788710094 3N`: i millisecondi GNU non esistono in BSD. Per i timestamp
usa `python3 -c "import time; print(int(time.time()*1000))"`.

### Le mattonelle della mappa non fanno in tempo

Uno zoom troppo rapido arriva su una mappa bianca. Un secondo di attesa in più
sulla destinazione, prima di proseguire, e il problema sparisce.

## Composizione

### Il telefono incollato a un bordo

Se lo si ancora al lato opposto della didascalia, lo spazio avanzato si accumula
tutto da una parte (misurato: 72 px sopra e 480 sotto). Telefono e testo vanno
trattati come **un blocco unico centrato**, con l'aria dal bordo uguale sopra e
sotto.

### Didascalie enormi sui tablet

Il corpo del testo tarato sulla larghezza diventa sproporzionato dove il
formato è largo e basso. Usa la **media geometrica** fra i due rapporti.

### Le didascalie del video si sfasano

Ogni ripresa dura diverso. Non scrivere i tempi a mano: ricavali dai marcatori
dei tocchi, che segnano il passaggio da una scena all'altra.
