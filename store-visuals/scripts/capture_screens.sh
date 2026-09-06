#!/usr/bin/env bash
# Cattura le schermate per gli store.
#
#   scripts/capture_screens.sh ios     <udid-simulatore>  <cartella> <lingua>
#   scripts/capture_screens.sh android <serial-emulatore> <cartella> <lingua>
#
# es.  scripts/capture_screens.sh ios 4403586F-... ios-iphone69 it
#      scripts/capture_screens.sh android emulator-5554 android-phone en
#
# Come funziona: `integration_test/store_screenshots_test.dart` pilota l'app
# vera e a ogni scena stampa `SHOTNOW:<nome>`; questo script legge il log e
# scatta con `simctl`/`adb`. Non si usa `binding.takeScreenshot` perche' su iOS
# sostituisce la superficie viva con un'immagine statica e le catture escono
# bianche; la cattura di sistema in piu' include la barra di stato reale.
set -eo pipefail

PLATFORM="$1"; TARGET="$2"; DEVICE_DIR="$3"; LANG_CODE="$4"
if [ -z "$PLATFORM" ] || [ -z "$TARGET" ] || [ -z "$DEVICE_DIR" ] || [ -z "$LANG_CODE" ]; then
  sed -n '2,9p' "$0"; exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/${RAW_DIR:-store/screenshots/raw}/$DEVICE_DIR/$LANG_CODE"
LOG="$(mktemp -t app-drive)"
mkdir -p "$OUT"
rm -f "$OUT"/*.png

shoot() {
  if [ "$PLATFORM" = "ios" ]; then
    xcrun simctl io "$TARGET" screenshot "$OUT/$1.png" >/dev/null 2>&1
  else
    # L'emulatore sotto carico fa comparire "System UI isn't responding", che
    # finirebbe in mezzo allo screenshot: lo si chiude prima di scattare.
    adb -s "$TARGET" shell am broadcast \
      -a android.intent.action.CLOSE_SYSTEM_DIALOGS >/dev/null 2>&1 || true
    adb -s "$TARGET" exec-out screencap -p > "$OUT/$1.png"
  fi
  echo "  catturata $DEVICE_DIR/$LANG_CODE/$1.png"
}

echo "== $DEVICE_DIR / $LANG_CODE  (log: $LOG)"
cd "$ROOT"
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/store_screenshots_test.dart \
  -d "$TARGET" \
  --dart-define=SHOT_LANG="$LANG_CODE" \
  --dart-define=DISABLE_ADS=true \
  > "$LOG" 2>&1 &
DRIVE_PID=$!

# Il test attende 5 s dopo ogni marcatore: c'e' tempo per lo scatto.
DONE=""
while kill -0 "$DRIVE_PID" 2>/dev/null; do
  # NIENTE `sort`: i marcatori vanno consumati nell'ordine in cui l'app li
  # stampa, altrimenti si scatta la scena sbagliata (l'app e' gia' andata
  # avanti). `|| true`: senza, con `set -e` il primo grep a vuoto chiude tutto.
  MARKERS=$(grep -o 'SHOTNOW:[0-9a-z-]*' "$LOG" 2>/dev/null | sed 's/SHOTNOW://' || true)
  for scene in $MARKERS; do
    case " $DONE " in
      *" $scene "*) ;;
      *) sleep 0.5; shoot "$scene"; DONE="$DONE $scene" ;;
    esac
  done
  sleep 0.2
done

wait "$DRIVE_PID" || true
COUNT=$(ls -1 "$OUT"/*.png 2>/dev/null | wc -l | tr -d ' ')
echo "== $COUNT catture in store/screenshots/raw/$DEVICE_DIR/$LANG_CODE"
[ "$COUNT" -ge 7 ] || { echo "ATTESE 7 catture — log completo in $LOG"; exit 1; }
