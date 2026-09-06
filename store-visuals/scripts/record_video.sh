#!/usr/bin/env bash
# Registra il video dimostrativo dal simulatore iPhone.
#
#   scripts/record_video.sh <udid-simulatore> [lingua] [cartella-video]
#
# Come funziona: `integration_test/promo_video_test.dart` (dal modello in reference/) pilota l'app vera con
# tempi lenti e leggibili, mentre `simctl io recordVideo` registra da fuori. Non
# si usa la registrazione interna a Flutter: catturerebbe solo il layer Flutter,
# senza barra di stato, e su iOS congela la superficie.
#
# La pubblicità è spenta a build time (`--dart-define=DISABLE_ADS=true`): senza,
# il modulo di consenso UMP si aprirebbe in mezzo al filmato.
#
# Il file esce in `<cartella-video>/promo-<lang>-raw.mov` a risoluzione nativa
# del simulatore. È materiale grezzo: lo rifinisce `scripts/add_touches.py`.
set -eo pipefail

UDID="$1"; LANG_CODE="${2:-it}"; OUT_DIR="${3:-store/video}"
if [ -z "$UDID" ]; then sed -n '2,6p' "$0"; exit 2; fi

ROOT="$(pwd)"
OUT="$ROOT/$OUT_DIR"
mkdir -p "$OUT"
RAW="$OUT/promo-$LANG_CODE-raw.mov"
LOG="$(mktemp -t app-video)"
rm -f "$RAW"

echo "== registrazione $LANG_CODE su $UDID (log: $LOG)"
xcrun simctl io "$UDID" recordVideo --codec=h264 --force "$RAW" &
REC_PID=$!
sleep 2
# Istante in cui la registrazione è partita davvero: i marcatori del pilota sono
# in millisecondi epoch, e questa è l'origine da cui contarli nel filmato.
# `date +%s%3N` è GNU: su macOS stampa "17887100943N" e manda a monte la
# sincronizzazione dei pallini. Si usa python, che c'è di sicuro.
python3 -c "import time; print(int(time.time()*1000))" > "$OUT/promo-$LANG_CODE-recstart.txt"

set +e
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/promo_video_test.dart \
  -d "$UDID" \
  --dart-define=SHOT_LANG="$LANG_CODE" \
  --dart-define=DISABLE_ADS=true \
  > "$LOG" 2>&1
DRIVE_RC=$?
set -e

# SIGINT: è il modo con cui simctl chiude e finalizza il file .mov.
kill -INT "$REC_PID" 2>/dev/null || true
wait "$REC_PID" 2>/dev/null || true
sleep 1

if [ "$DRIVE_RC" -ne 0 ]; then
  echo "ATTENZIONE: il pilota è uscito con codice $DRIVE_RC — log in $LOG"
fi
if [ ! -s "$RAW" ]; then
  echo "Nessun filmato prodotto. Log completo in $LOG"; exit 1
fi
# I marcatori del pilota (`VIDEO:start`, `TOUCH:<ms>,<x>,<y>`) servono al passo
# successivo, che disegna i pallini bianchi: si conservano accanto al filmato.
grep -oE '(VIDEO|TOUCH|RING):[0-9a-z,.-]+' "$LOG" > "$OUT/promo-$LANG_CODE-touches.txt" || true
echo "== marcatori: $(wc -l < "$OUT/promo-$LANG_CODE-touches.txt" | tr -d ' ') righe in $OUT/promo-$LANG_CODE-touches.txt"
ffprobe -v error -show_entries format=duration:stream=width,height \
  -of default=noprint_wrappers=1 "$RAW" 2>/dev/null || true
echo "== filmato grezzo: $RAW"
