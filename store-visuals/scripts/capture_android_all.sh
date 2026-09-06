#!/usr/bin/env bash
# Catture Android per gli store: avvia l'emulatore giusto, cattura it+en,
# lo spegne e passa al successivo.
#
#   scripts/capture_android_all.sh              # telefono + entrambi i tablet
#   scripts/capture_android_all.sh SS-Phone     # solo un AVD
#
# Gli AVD sono creati una volta con `avdmanager` e hanno la risoluzione
# forzata in `~/.android/avd/<nome>.avd/config.ini` (hw.lcd.width/height):
#
#   SS-Phone     1080x1920 @420dpi  -> raw/android-phone
#   SS-Tablet7   1200x1920 @320dpi  -> raw/android-tablet7
#   SS-Tablet10  1600x2560 @320dpi  -> raw/android-tablet10
#
# ⚠️ Gli AVD creati da `avdmanager` senza profilo dispositivo nascono con GPU
# spenta e heap da 32 MB, e le immagini Play Store non autorizzano adb: vedi
# reference/trappole.md prima di crearne di nuovi.
#
# La risoluzione **non** è quella nativa dei telefoni moderni di proposito:
# Play rifiuta gli screenshot in cui il lato lungo supera il doppio del corto,
# e 1080x2400 (rapporto 2,22) sfora. Vedi `store/specs.md`.
#
# Serve un JDK: Gradle non parte senza. Su questa macchina sta in Homebrew.
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home}"
SDK="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
EMULATOR="$SDK/emulator/emulator"
ADB="$SDK/platform-tools/adb"

# AVD -> cartella di destinazione.
avd_dir() {
  case "$1" in
    SS-Phone) echo "android-phone" ;;
    SS-Tablet7) echo "android-tablet7" ;;
    SS-Tablet10) echo "android-tablet10" ;;
    *) echo "" ;;
  esac
}

FAILED=""
AVDS=("$@")
if [ ${#AVDS[@]} -eq 0 ]; then
  AVDS=(SS-Phone SS-Tablet7 SS-Tablet10)
fi

for avd in "${AVDS[@]}"; do
  dir="$(avd_dir "$avd")"
  if [ -z "$dir" ]; then echo "AVD sconosciuto: $avd"; exit 2; fi

  echo "== avvio $avd"
  # `-no-snapshot`: uno stato salvato riporterebbe l'app già installata e le
  # preferenze della cattura precedente, che il test si aspetta vuote.
  #
  # GPU **hardware** e finestra visibile, non `-no-window -gpu swiftshader`:
  # con il rendering software un frame della mappa costa oltre un secondo
  # (`app_time_stats avg=1335ms` nei log del 5 set 2026), il pilota va in
  # timeout e le catture escono a metà. La finestra non entra negli screenshot:
  # quelli li prende `adb exec-out screencap` dal framebuffer.
  "$EMULATOR" -avd "$avd" -no-audio -no-boot-anim -no-snapshot -gpu auto \
    >/dev/null 2>&1 &
  EMU_PID=$!

  "$ADB" wait-for-device
  # `sys.boot_completed` arriva prima che il launcher sia davvero pronto: senza
  # l'attesa in più le prime catture escono con lo sfondo del sistema.
  until [ "$("$ADB" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do
    sleep 2
  done
  sleep 15
  SERIAL="$("$ADB" devices | awk '/emulator/{print $1; exit}')"
  echo "== $avd pronto ($SERIAL)"

  # Un fallimento su una lingua non deve far saltare gli AVD successivi: si
  # annota e si va avanti, il riepilogo finale dice cosa manca.
  for lang in it en; do
    if ! scripts/capture_screens.sh android "$SERIAL" "$dir" "$lang"; then
      FAILED="$FAILED $dir/$lang"
    fi
  done

  echo "== spengo $avd"
  "$ADB" -s "$SERIAL" emu kill >/dev/null 2>&1 || kill "$EMU_PID" 2>/dev/null || true
  wait "$EMU_PID" 2>/dev/null || true
  sleep 5
done

if [ -n "$FAILED" ]; then
  echo "== catture Android INCOMPLETE:$FAILED"
  exit 1
fi
echo "== catture Android completate"
