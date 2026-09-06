# Misure e limiti degli store

Verificate il **6 settembre 2026** sulle documentazioni ufficiali
([Apple](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications/) ·
[Google](https://support.google.com/googleplay/android-developer/answer/9866151)).
Cambiano di anno in anno: **ricontrollarle prima di ogni campagna**.

## Screenshot

| Slot | Misura usata | Obbligatorio |
|---|---|---|
| iPhone 6.9" | **1320 × 2868** (accettati anche 1290×2796, 1260×2736) | Sì, se l'app gira su iPhone |
| iPhone 6.5" | **1284 × 2778** (o 1242×2688) | Solo se manca il set 6.9". ⚠️ Questo slot **rifiuta** i 1320×2868 |
| iPad 13" | **2064 × 2752** (o 2048×2732) | Sì, se l'app gira su iPad (`TARGETED_DEVICE_FAMILY = "1,2"`) |
| Telefono Android | **1080 × 1920** | Sì (minimo 2, massimo 8) |
| Tablet 7" | **1200 × 1920** | No, ma servono ≥4 per il badge "ottimizzata per tablet" |
| Tablet 10" | **1600 × 2560** | idem |

Apple ridimensiona da sé i set 6.9" e 13" per le classi minori: non serve
caricare 6.5", 5.5", 11".

**La trappola del 2:1 su Play.** Il lato lungo non può superare il doppio del
corto. La risoluzione nativa dei telefoni moderni (1080×2400, rapporto 2,22)
viene **rifiutata all'upload**: per questo l'emulatore va configurato a
1080×1920 (1,78).

Formati: PNG o JPEG, RGB, **senza trasparenza**.

## Video

| | App Store (App Preview) | Google Play |
|---|---|---|
| Come si carica | file, fino a 3 per localizzazione | solo URL **YouTube** |
| Durata | 15–30 s | ≤ 30 s di autoplay |
| Misure (6.9" verticale) | 886×1920 o 1080×1920 | libere |
| Contenuto | **solo riprese dell'app**: niente cornici, mani o grafiche aggiunte | libero |

Da qui la doppia uscita della catena: il filmato "nudo" per Apple, quello
vestito per Play, YouTube e i social. Se la ripresa nativa è più lunga di 30 s,
per l'App Preview va tagliata una scena sola, non compressa tutta.

## Icone e grafiche

| Asset | Misura | Note |
|---|---|---|
| Icona App Store | 1024 × 1024 | RGB **senza canale alpha**: con l'alpha l'upload viene rifiutato (`ITMS-90717`). Si estrae dall'asset catalog della build |
| Icona Play | 512 × 512 | PNG 32 bit **con** alpha, max 1 MB |
| Immagine in evidenza Play | 1024 × 500 | JPEG o PNG 24 bit senza alpha |

## Testi

| Campo | App Store | Play |
|---|---|---|
| Nome | 30 | 30 |
| Sottotitolo / descrizione breve | 30 | 80 |
| Descrizione | 4.000 | 4.000 |
| Novità della versione | 4.000 | **500** (tronca) |
| Keyword | 100, separate da virgola **senza spazi** | — |

Le "novità" vanno scritte per il limite più stretto: 500 caratteri valgono per
entrambi gli store senza doverne mantenere due versioni.
