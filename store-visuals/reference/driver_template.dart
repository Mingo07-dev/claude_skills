// MODELLO di pilota per catture e video. Copiare in `integration_test/` e
// riempire i punti segnati con TODO: la struttura, le attese e i gesti sono
// quelli che funzionano, il percorso dentro l'app è l'unica cosa da scrivere.
//
//   flutter drive --driver=test_driver/integration_test.dart \
//     --target=integration_test/promo_video_test.dart -d <device> \
//     --dart-define=SHOT_LANG=it --dart-define=DISABLE_ADS=true
//
// Due usi, stessa impalcatura:
//
// * **catture**: si stampa `SHOTNOW:<nome>` a ogni scena e uno script esterno
//   scatta con `simctl`/`adb` (`scripts/capture_screens.sh`). Non si usa
//   `binding.takeScreenshot`: su iOS congela la superficie e le catture
//   successive escono bianche.
// * **video**: si registra da fuori con `simctl io recordVideo` mentre il
//   pilota naviga, e si stampano i marcatori che il montaggio userà.
//
// **Gesti veri, senza mirino.** `tester.tap` e `fling` fanno disegnare al
// binding un mirino tondo con la croce sul punto toccato; guardando
// `handlePointerEvent` in `flutter_test/src/binding.dart` lo si disegna solo per
// gli eventi con sorgente `test`. Con sorgente **device** — e
// `shouldPropagateDevicePointerEvents` acceso — gli stessi eventi arrivano
// all'app come quelli di un dito (ondine, velocità del trascinamento, fisica dei
// pannelli) e non lasciano traccia sullo schermo.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

// TODO: import dell'app e dei provider/schermate che servono a navigare.
// import 'package:mia_app/main.dart' as app;

const String kLang = String.fromEnvironment('SHOT_LANG', defaultValue: 'it');

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('video dimostrativo', (tester) async {
    // Stato deterministico: tutto ciò che comparirebbe "la prima volta" va
    // spento, altrimenti finisce nelle immagini. Cercale con:
    //   grep -rn "SharedPreferences" lib | grep -iE "seen|asked|done|dismissed"
    SharedPreferences.setMockInitialValues({
      // TODO: 'flutter.onboarding.seen': true,
      // TODO: 'flutter.notif.permissionsAsked': true,
      // TODO: 'flutter.review.done': true,
      // TODO: 'flutter.analytics.promptSeen': true,
      'flutter.app.locale': kLang,
    });

    // TODO: assert che la pubblicità sia spenta a build time, se l'app ne ha.
    // assert(kAdsDisabledAtBuild, 'Lancia con --dart-define=DISABLE_ADS=true');

    // TODO: await app.main();
    await _hold(tester, const Duration(seconds: 14)); // avvio

    // TODO: prendere il ProviderContainer / lo stato che serve a navigare.
    // final container = ProviderScope.containerOf(
    //     tester.element(find.byType(SchermataPrincipale)));

    // I dati devono essere **arrivati** prima di cominciare: aspettare a tempo
    // non basta, si finisce per riprendere schermate a metà caricamento.
    // TODO: await container.read(datiPrincipaliProvider.future);
    // TODO: attendere che eventuali indicatori di aggiornamento si spengano:
    // for (var i = 0; i < 60; i++) {
    //   if (container.read(inAggiornamentoProvider).asData?.value == false) break;
    //   await _hold(tester, const Duration(milliseconds: 500));
    // }

    // Da qui il montaggio comincia a contare: il marcatore sta **dopo** le
    // attese, altrimenti il filmato si apre con quindici secondi di schermata
    // ferma.
    debugPrint('VIDEO:start,${DateTime.now().millisecondsSinceEpoch}');
    await _hold(tester, const Duration(seconds: 2));

    // --- scena 1: il colpo d'occhio -----------------------------------------
    // TODO: la schermata che risponde alla domanda per cui l'app esiste.
    // Se c'è un movimento di camera/scorrimento, annuncialo: il montaggio taglia
    // l'inizio quattro secondi prima di questo marcatore.
    debugPrint('VIDEO:zoom,${DateTime.now().millisecondsSinceEpoch}');
    await _hold(tester, const Duration(seconds: 4));

    // --- scena 2: si apre un contenuto --------------------------------------
    // Il punto da toccare si **calcola**, non si scrive a mano: prendilo
    // dall'albero dei widget o proiettalo (mappe, liste) — così il pallino
    // finisce sul comando e non a caso.
    // TODO: await _tapAt(tester, tester.getCenter(find.byKey(...)));
    await _hold(tester, const Duration(seconds: 6));

    // Evidenzia al massimo due o tre aree in tutto il filmato: più cerchi
    // diventano rumore.
    // TODO: _ring(tester, find.byKey(const Key('cosa-conta')), 5);

    // --- altre scene --------------------------------------------------------
    // TODO: una scena per funzione, con pause generose: un'interfaccia che
    // cambia più in fretta di quanto si legga non racconta niente.

    // Il framework controlla che il flag torni com'era: senza, l'ultima riga
    // del log è un errore invece di "All tests passed".
    tester.binding.shouldPropagateDevicePointerEvents = false;
    debugPrint('VIDEO:end,${DateTime.now().millisecondsSinceEpoch}');
  }, timeout: const Timeout(Duration(minutes: 10)));
}

// --------------------------------------------------------------------- gesti

final Stopwatch _clock = Stopwatch()..start();
Duration _stamp() => _clock.elapsed;

/// Segna dove il dito ha toccato: la riga viene letta da
/// `scripts/add_touches.py`, che ci disegna il pallino bianco.
void _touch(Offset p) {
  debugPrint('TOUCH:${DateTime.now().millisecondsSinceEpoch},'
      '${p.dx.round()},${p.dy.round()}');
}

/// Area da cerchiare nel montaggio, presa dall'albero dei widget invece che a
/// occhio dai fotogrammi.
void _ring(WidgetTester tester, Finder finder, int seconds,
    {double padX = 16, double padY = 16}) {
  if (finder.evaluate().isEmpty) return;
  var r = tester.getRect(finder.first);
  for (final e in finder.evaluate().skip(1)) {
    r = r.expandToInclude(tester.getRect(find.byWidget(e.widget)));
  }
  r = Rect.fromLTRB(r.left - padX, r.top - padY, r.right + padX, r.bottom + padY);
  debugPrint('RING:${DateTime.now().millisecondsSinceEpoch},'
      '${r.center.dx.round()},${r.center.dy.round()},'
      '${(r.width / 2).round()},${(r.height / 2).round()},$seconds');
}

/// Tocco **vero**: eventi con sorgente `device`, che l'app riceve come quelli di
/// un dito e che il binding non decora con il mirino.
Future<void> _tapAt(WidgetTester tester, Offset p) async {
  _touch(p);
  final b = tester.binding;
  b.shouldPropagateDevicePointerEvents = true;
  const id = 42;
  b.handlePointerEventForSource(
      PointerDownEvent(pointer: id, position: p, timeStamp: _stamp()));
  await tester.pump(const Duration(milliseconds: 90));
  b.handlePointerEventForSource(
      PointerUpEvent(pointer: id, position: p, timeStamp: _stamp()));
  await tester.pump(const Duration(milliseconds: 120));
}

Future<void> _tapText(WidgetTester tester, String text) async {
  final f = find.text(text);
  if (f.evaluate().isEmpty) return;
  await _tapAt(tester, tester.getCenter(f.last));
}

Future<void> _tapIcon(WidgetTester tester, IconData icon) async {
  final f = find.byIcon(icon);
  if (f.evaluate().isEmpty) return;
  await _tapAt(tester, tester.getCenter(f.first));
}

/// Trascinamento veloce (per i pannelli che cambiano aggancio solo con una
/// "sberla"): la velocità la calcola il framework dai timestamp, che quindi
/// devono avanzare davvero.
Future<void> _flingUp(WidgetTester tester, Offset from,
    {double step = 34, int steps = 8}) async {
  final b = tester.binding;
  b.shouldPropagateDevicePointerEvents = true;
  const id = 43;
  b.handlePointerEventForSource(
      PointerDownEvent(pointer: id, position: from, timeStamp: _stamp()));
  for (var i = 1; i <= steps; i++) {
    b.handlePointerEventForSource(PointerMoveEvent(
      pointer: id,
      position: from.translate(0, -step * i),
      delta: Offset(0, -step),
      timeStamp: _stamp(),
    ));
    await tester.pump(const Duration(milliseconds: 12));
  }
  b.handlePointerEventForSource(PointerUpEvent(
      pointer: id, position: from.translate(0, -step * steps), timeStamp: _stamp()));
  await tester.pump(const Duration(milliseconds: 400));
}

// ----------------------------------------------------------------- movimenti

/// Scorre il contenuto aperto: qui un gesto non serve e `animateTo` è più
/// preciso. Attenzione: con un `NestedScrollView` le schede condividono la
/// posizione, quindi torna in cima prima di cambiare scheda.
Future<void> _scrollBy(WidgetTester tester, double delta, Duration duration) async {
  final state = _scrollable(tester);
  if (state == null) return;
  final target = (state.position.pixels + delta)
      .clamp(state.position.minScrollExtent, state.position.maxScrollExtent);
  state.position.animateTo(target, duration: duration, curve: Curves.easeInOut);
  await _hold(tester, duration + const Duration(milliseconds: 200));
}

Future<void> _scrollToEnd(WidgetTester tester, Duration duration) async {
  final state = _scrollable(tester);
  if (state == null) return;
  state.position.animateTo(state.position.maxScrollExtent,
      duration: duration, curve: Curves.easeInOut);
  await _hold(tester, duration + const Duration(milliseconds: 200));
}

Future<void> _scrollToTop(WidgetTester tester, Duration duration) async {
  final state = _scrollable(tester);
  if (state == null || state.position.pixels <= 1) return;
  state.position.animateTo(state.position.minScrollExtent,
      duration: duration, curve: Curves.easeInOut);
  await _hold(tester, duration + const Duration(milliseconds: 150));
}

/// L'ultimo `Scrollable` montato è quello del pannello o del foglio aperto.
ScrollableState? _scrollable(WidgetTester tester) {
  final f = find.byType(Scrollable);
  if (f.evaluate().isEmpty) return null;
  return tester.state<ScrollableState>(f.last);
}

/// Lascia scorrere il tempo **reale** continuando a disegnare: `pumpAndSettle`
/// non torna mai se qualcosa anima di continuo (mappe, caricamenti, indicatori).
Future<void> _hold(WidgetTester tester, Duration d) async {
  final end = DateTime.now().add(d);
  while (DateTime.now().isBefore(end)) {
    await tester.pump(const Duration(milliseconds: 16));
  }
}

// ------------------------------------------------------------------- appunti
//
// * Controller di widget di terze parti (mappe, video): leggili dal **widget**
//   (`tester.widget<FlutterMap>(...).mapController`), non con `.of(context)`
//   cercando nell'albero — quella chiamata registra una dipendenza durante la
//   visita e il framework sostituisce il sottoalbero con la schermata rossa.
// * Un foglio modale si chiude con un tocco sulla **barriera**, non con
//   `Navigator.maybePop()`, che a seconda del navigator che lo ospita non fa
//   niente. Verifica che sia sparito prima del gesto successivo.
// * Con i tocchi veri l'azione la fa l'app: non chiamare **anche** la funzione
//   che apre il pannello, o si apre due volte.
// * Schermate dietro autenticazione: con un tocco vero si finisce sul modulo di
//   accesso. Se serve mostrarle, annota il tocco (`_touch`) e apri la rotta
//   direttamente — dichiarandolo a chi commissiona il lavoro.
