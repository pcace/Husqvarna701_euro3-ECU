# Husqvarna 701 ECU - Security Keys Visualisierung

## Key-Tabelle Struktur (Offset 0x87640)

```
Offset     Hex Data                                ASCII
--------   ------------------------------------    ----------------
0x87640:   d3 1f 23 40 00 6b 62 43 64 53 65 63    ..#@.kbCdSec
0x8764C:   d3 1d 23 20 d3 1d 23 40 d3 1d 23 50    KEY 0x1D23 (3x)
0x87658:   00 6b 62 43 64 53 65 63                .kbCdSec
0x87660:   d3 1b 23 20 d3 1b 23 40 d3 1b 23 50    KEY 0x1B23 (3x)
0x8766C:   00 6b 62 43 64 53 65 63                .kbCdSec
0x87674:   d3 19 23 20 d3 19 23 40 d3 19 23 50    KEY 0x1923 (3x)
0x87680:   00 6b 00 00                            .k..
```

## Key Pattern Analyse

```
Byte-Muster: [d3] [Key-Hi] [Key-Lo] [Level]
             ^^^^  ^^^^^^^^^^^^^^  ^^^^^^^
           Prefix    16-bit Key    Level Indicator
```

### Beispiel: Key 0x1D23

```
Bytes:  d3  1d  23  20
        │   │   │   └─── Level 0x20 (Request Seed Level)
        │   └───┴─────── Key 0x1D23 (Big Endian)
        └─────────────── Prefix/Opcode
```

## Gefundene Keys Übersicht

```
┌─────────┬─────────┬──────────────┬─────────────────────────┐
│  Key    │ Dezimal │   Levels     │     Beschreibung        │
├─────────┼─────────┼──────────────┼─────────────────────────┤
│ 0x1D23  │  7459   │ 20, 40, 50   │ PRIMÄR - Neu gefunden   │
│ 0x1B23  │  6947   │ 20, 40, 50   │ PRIMÄR - Neu gefunden   │
│ 0x1923  │  6435   │ 20, 40, 50   │ PRIMÄR - BMW G450X Key  │
│ 0x1523  │  5411   │ 21, 41, 50   │ SEKUNDÄR                │
│ 0x1023  │  4131   │ 20, 40       │ SEKUNDÄR                │
└─────────┴─────────┴──────────────┴─────────────────────────┘
```

## Level Bedeutung (Vermutung)

```
┌────────┬───────────────────────────────────────────────────┐
│ Level  │  Wahrscheinliche Bedeutung                        │
├────────┼───────────────────────────────────────────────────┤
│ 0x20   │ Standard Security Access (Lesen)                  │
│ 0x40   │ Erweiterte Funktionen (Kalibrierung)              │
│ 0x50   │ Programming/Schreiben (Gefährlich!)               │
│ 0x21   │ Alternative Access Level                          │
│ 0x41   │ Spezielle Diagnose-Funktionen                     │
└────────┴───────────────────────────────────────────────────┘
```

## Test-Priorität

### 🟢 Höchste Priorität
```
1. Key 0x1923 (Level 0x20) - BMW G450X bestätigter Key
   └─ Test Command: 27 01 (Request), dann Response mit Key
   
2. Key 0x1D23 (Level 0x20) - Erster Key in Tabelle
3. Key 0x1B23 (Level 0x20) - Zweiter Key in Tabelle
```

### 🟡 Mittlere Priorität
```
4. Key 0x1523 (Level 0x21) - Alternative Level
5. Key 0x1023 (Level 0x20) - Zusätzlicher Key
```

### 🔴 Niedrige Priorität (Vorsicht!)
```
6. Level 0x40 Keys - Erweiterte Funktionen
7. Level 0x50 Keys - Programming Level (⚠ Gefährlich!)
```

## Authentifizierungs-Ablauf

```
┌─────────┐                          ┌─────────┐
│  Tool   │                          │   ECU   │
└────┬────┘                          └────┬────┘
     │                                    │
     │  1. Request Seed (Level 0x01)     │
     │────────────────────────────────>  │
     │           27 01                    │
     │                                    │
     │  2. Response mit SEED              │
     │  <────────────────────────────────│
     │      67 01 [SEED_HI] [SEED_LO]    │
     │                                    │
     ├─ 3. Berechne Response:             │
     │    Response = (SEED * KEY) & 0xFFFF
     │                                    │
     │  4. Send Key Response              │
     │────────────────────────────────>  │
     │    27 02 [RESP_HI] [RESP_LO]      │
     │                                    │
     │  5a. SUCCESS: 67 02                │
     │  <────────────────────────────────│
     │                                    │
     │  5b. FEHLER: 7F 27 35              │
     │  <────────────────────────────────│
     │                                    │
```

## Berechnungs-Beispiele

### Mit SEED = 0x1234

```python
KEY 0x1D23:  0x1234 * 0x1D23 = 0x022F611C  → Response: 0x611C
KEY 0x1B23:  0x1234 * 0x1B23 = 0x020CF91C  → Response: 0xF91C
KEY 0x1923:  0x1234 * 0x1923 = 0x01DC911C  → Response: 0x911C
KEY 0x1523:  0x1234 * 0x1523 = 0x0187C11C  → Response: 0xC11C
KEY 0x1023:  0x1234 * 0x1023 = 0x011EBD1C  → Response: 0xBD1C
```

### Mit SEED = 0xABCD

```python
KEY 0x1D23:  0xABCD * 0x1D23 = 0x131DBBBF  → Response: 0xBBBF
KEY 0x1B23:  0xABCD * 0x1B23 = 0x120B23BF  → Response: 0x23BF
KEY 0x1923:  0xABCD * 0x1923 = 0x10D88BBF  → Response: 0x8BBF
KEY 0x1523:  0xABCD * 0x1523 = 0x0ED6F3BF  → Response: 0xF3BF
KEY 0x1023:  0xABCD * 0x1023 = 0x0AC55BBF  → Response: 0x5BBF
```

## Kommandos für manuellen Test

### Mit ELM327 über Terminal

```bash
# 1. Verbinde und initialisiere
screen /dev/tty.usbserial 38400

# 2. Setup
ATZ          # Reset
ATE0         # Echo off
ATSP5        # KWP2000 Protocol
ATSH 12      # ECU Adresse 0x12 (wichtig!)

# 3. Request Seed
27 01        # Level 0x01

# Erwarte Response: 67 01 XX XX (XX XX = SEED)
# Beispiel: 67 01 12 34 → SEED = 0x1234

# 4. Berechne Response mit Python
python3 -c "print(hex((0x1234 * 0x1D23) & 0xFFFF))"
# → 0x611c

# 5. Send Response
27 02 61 1C  # Level 0x02, Response 0x611C

# Erwarte: 67 02 (Erfolg!) oder 7F 27 35 (Fehler)
```

## Fehler-Codes

```
┌──────────┬─────────────────────────────────────────────┐
│   Code   │  Bedeutung                                  │
├──────────┼─────────────────────────────────────────────┤
│ 7F 27 12 │ Sub-function not supported                  │
│ 7F 27 13 │ Incorrect message length                    │
│ 7F 27 22 │ Conditions not correct                      │
│ 7F 27 24 │ Request sequence error                      │
│ 7F 27 31 │ Request out of range                        │
│ 7F 27 35 │ Invalid key (⭐ häufigster Fehler)          │
│ 7F 27 36 │ Exceed number of attempts                   │
│ 7F 27 37 │ Required time delay not expired (Locked!)   │
└──────────┴─────────────────────────────────────────────┘
```

## Hardware Setup

```
┌──────────────┐         USB          ┌─────────────┐
│              │  ◄────────────────►  │             │
│   Computer   │                      │   ELM327    │
│              │                      │   Interface │
└──────────────┘                      └──────┬──────┘
                                             │
                                        K-Line (6-Pin)
                                             │
                                      ┌──────▼──────┐
                                      │             │
                                      │  ECU (0x12) │
                                      │  Keihin     │
                                      │  KM270      │
                                      │             │
                                      └─────────────┘
```

## Code-Snippet: Response-Berechnung

```python
def calculate_security_response(seed: int, key: int) -> int:
    """
    Berechnet die Security Access Response
    
    Args:
        seed: 16-bit Zufallszahl von der ECU
        key: 16-bit Security Key aus Firmware
        
    Returns:
        16-bit Response für die ECU
    """
    # Multiplikation und Modulo 2^16 (untere 2 Bytes)
    response = (seed * key) & 0xFFFF
    return response


# Beispiel
seed = 0x1234
key = 0x1D23
response = calculate_security_response(seed, key)
print(f"SEED: 0x{seed:04X}, KEY: 0x{key:04X} → Response: 0x{response:04X}")
# Output: SEED: 0x1234, KEY: 0x1D23 → Response: 0x611C
```

## Weiterführende Informationen

### Forum-Thread Highlights

1. **gobtald's Durchbruch** (Post #28)
   - Hat den Authentifizierungs-Algorithmus reverse-engineered
   - Verwendete Raspberry Pi als Logic Analyzer
   - Decompilierte BMW EDIABAS .prg Files

2. **Wichtige Erkenntnis**
   - ECU verwendet **BMW-spezifische Adresse 0x12**
   - Standard OBD2-Tools mit Adresse 0x33 funktionieren nicht!
   - GS-911 Tool ist kompatibel (laut Normann)

3. **449er Keys (zum Vergleich)**
   - Wurden via Brute-Force gefunden
   - 0x6AD5 und 0x1EC3
   - ~8000 Versuche bis zum Erfolg

### Firmware-Struktur

```
0x000000 - 0x01FFFF:  Boot/Startup Code
0x020000 - 0x0FFFFF:  Hauptprogramm
0x100000 - 0x13FFFF:  Daten/Kalibrierung/Maps
0x13FFD6:             ECU-Identifier (KM270EU15E0301)
0x87640:              Security Key Tabelle ⭐
0x6B9A0:              Sekundäre Key-Referenz
```
