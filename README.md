# Husqvarna 701 Enduro (2016) - ECU Security Keys Analysis

> Reverse engineering and security key extraction for Husqvarna 701 Euro3 ECU (Keihin KM270)

This repository contains the analysis, tools, and findings for unlocking diagnostic access to the Husqvarna 701 Enduro (2016) ECU via KWP2000 security authentication.

---

## 🔑 Key Findings Summary

**ECU Information:**
- Hardware: `760.41.031.000`
- Software: `KM270EU15E0301`
- Manufacturer: Keihin
- Firmware: 1,310,720 bytes (1.25 MB)
- Protocol: KWP2000 (ISO 14230-4) over K-Line
- ECU Address: `0x12` (BMW-specific, not standard OBD2 `0x33`)

**Discovered Security Keys:**

| Key      | Decimal | Levels           | Status                              | Firmware Location |
|----------|---------|------------------|-------------------------------------|-------------------|
| `0x1D23` | 7459    | 0x20, 0x40, 0x50 | Primary in key table                | 0x87640           |
| `0x1B23` | 6947    | 0x20, 0x40, 0x50 | Primary in key table                | 0x87640           |
| `0x1923` | 6435    | 0x20, 0x40, 0x50 | BMW G450X confirmed key             | 0x87640           |
| `0x1523` | 5411    | 0x21, 0x41, 0x50 | Secondary key                       | 0x6B9A4           |
| `0x1023` | 4131    | 0x20, 0x40       | Secondary key                       | 0x876EE           |

**Key Breakthrough:** A structured key table was found at offset `0x87640` containing multiple security keys with associated level information, separated by the ASCII marker `"kbCdSec"`.

---

## 🔬 Methodology

### 1. Firmware Acquisition
- Extracted firmware dump from ECU (1.25 MB) (Using KESS V3)
- Format: Intel HEX file

### 2. Pattern Analysis
- Searched for known BMW G450X keys (`0x5106`, `0x1923`)
- Identified structured data patterns around key locations
- Located key table at offset `0x87640`

### 3. Key Table Structure
The key table follows a consistent pattern:

```
Offset     Hex Data                                ASCII
--------   ------------------------------------    ----------------
0x87640:   d3 1f 23 40 00 6b 62 43 64 53 65 63    ..#@.kbCdSec
0x8764C:   d3 1d 23 20 d3 1d 23 40 d3 1d 23 50    KEY 0x1D23 (3x)
0x87658:   00 6b 62 43 64 53 65 63                .kbCdSec
```

Each entry contains:
- Prefix byte: `0xd3`
- Key value: 16-bit big-endian
- Level byte: `0x20`, `0x40`, `0x50`, etc.
- Separator: `"kbCdSec"` (ASCII)

### 4. Cross-Reference Validation
- BMW G450X key `0x1923` found in firmware ✅
- Confirms same authentication algorithm
- Same KWP2000 protocol and addressing

---

## 🔐 Authentication Algorithm

Based on gobtald's reverse engineering of BMW G450X:
(https://www.cafehusky.com/threads/449-511-communication-with-ecu.39593/page-2)

```python
def calculate_response(seed: int, key: int) -> int:
    """
    Calculate security access response
    
    Args:
        seed: 16-bit random number from ECU
        key: 16-bit security key from firmware
        
    Returns:
        16-bit response for ECU
    """
    return (seed * key) & 0xFFFF
```

### Example
```
SEED from ECU:  0x1234
KEY:            0x1D23
Calculation:    0x1234 * 0x1D23 = 0x022F611C
Response:       0x611C (lower 16 bits)
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python dependencies
pip install pyserial

# For analysis (optional)
pip install hexdump
```

### Test Without Hardware (Simulation)
```bash
cd scripts
python3 ecu_tester.py --dummy
```

### Test With Hardware
```bash
# List available serial ports
python3 -m serial.tools.list_ports

# Connect ELM327 or VAG409 interface
python3 ecu_tester.py /dev/tty.usbserial

# On Linux
python3 ecu_tester.py /dev/ttyUSB0

# On Windows
python3 ecu_tester.py COM3
```

---

## 📡 KWP2000 Communication

### Critical Configuration

- **Protocol:** KWP2000 (ISO 14230-4)
- **ECU Address:** `0x12` (⚠️ BMW-specific, NOT standard `0x33`)
- **Tester Address:** `0xF1`
- **Baud Rate:** Typically 10400 or 9600

### Service 0x27 - Security Access

**Step 1: Request Seed**
```
TX: 27 01              (Request seed for level 0x01)
RX: 67 01 XX XX        (ECU returns SEED)
```

**Step 2: Send Key Response**
```
Calculate: Response = (SEED * KEY) & 0xFFFF

TX: 27 02 XX XX        (Send calculated response)
RX: 67 02              ✅ Success!
RX: 7F 27 35           ❌ Invalid key
RX: 7F 27 37           ⚠️ ECU locked (too many attempts)
```

### Security Levels

| Level  | Description                        | Risk   |
|--------|------------------------------------|--------|
| `0x20` | Standard read access               | Low    |
| `0x40` | Extended functions (calibration)   | Medium |
| `0x50` | Programming/write access           | High |
| `0x21` | Alternative access level           | Low    |
| `0x41` | Special diagnostic functions       | Medium |

---

## 🧪 Testing Strategy

### Recommended Test Sequence

1. **Test Known BMW Key (0x1923) at Level 0x20**
   - Highest confidence
   - Confirmed in G450X
   - Present in 701 firmware

2. **Test New Primary Keys**
   - `0x1D23` (Level 0x20)
   - `0x1B23` (Level 0x20)
   - First entries in key table

3. **Test Secondary Keys**
   - `0x1523` (Level 0x21)
   - `0x1023` (Level 0x20)

4. **Fallback: Brute Force**
   - Use `brute_force_keys.py`
   - ~65,536 possibilities (16-bit)
   - Optimized: ~8,000-10,000 attempts

---

## 🛠️ Tools Included

### Analysis Tools
- **`analyze_ecu.py`** - Main firmware analysis, finds keys and patterns
- **`extract_keys.py`** - Extracts security keys from firmware
- **`find_algorithm.py`** - Locates authentication algorithm
- **`disassemble_algorithm.py`** - Disassembles auth functions

### Testing Tools
- **`ecu_tester.py`** - Hardware testing with ELM327/VAG409
- **`brute_force_keys.py`** - Brute-force key discovery (last resort)

### Reverse Engineering
- **`analyze_husqvarna701.java`** - Ghidra script for deep analysis
- **`analyze_security.r2`** - Radare2 automation script

---

## 📖 Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Fast lookup for keys and commands
- **[KEYS_VISUAL.md](KEYS_VISUAL.md)** - Visual guide to key table structure
- **[forum.md](forum.md)** - Original CafeHusky research thread

---

## 🤝 Credits & Acknowledgments

This work builds upon the brilliant reverse engineering by the CafeHusky community:

- **gobtald** - Reverse engineered BMW G450X authentication algorithm using Raspberry Pi logic analyzer and BMW EDIABAS decompilation
- **tacotruck** - Created BESTDIS decompiler for BMW .prg files
- **Normann** - Confirmed GS-911 compatibility with G450X
- **Dangermouse449** - Initial 449 brute-force key discovery (0x6AD5, 0x1EC3)
- **CafeHusky Forum** - ["449/511 communication with ECU" thread](https://www.cafehusky.com/threads/449-511-communication-with-ecu.46084/)

---

## 📄 License & Disclaimer

**For Educational and Research Purposes Only**

⚠️ **Legal Disclaimer:**
- Modifying ECU software may void warranty
- May violate emissions regulations or road legality
- Can cause engine damage if done incorrectly
- May be illegal in your jurisdiction

**USE AT YOUR OWN RISK**

The authors and contributors are not responsible for any damage, legal issues, or consequences arising from the use of this information or tools.

---

## 🔮 Future Work

- [ ] Hardware validation of discovered keys
- [ ] Map security level functions after successful authentication
- [ ] Document ECU functions accessible at each level
- [ ] Develop safe diagnostic tool for community use
- [ ] Analyze firmware for tuning/mapping capabilities

---

## 📮 Contributing

Found additional keys or tested these successfully? Contributions welcome!

Please share findings in:
1. This repository (open an issue)
2. CafeHusky forum thread
3. Husqvarna/BMW enthusiast communities

---

**Status:** 🔬 Research Phase - Hardware Testing Needed
