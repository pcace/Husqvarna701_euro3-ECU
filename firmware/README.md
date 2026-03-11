# ECU Firmware Dumps

This directory contains firmware dumps from Husqvarna 701 Enduro ECUs.

## 📦 Files

### `241019_701_enduro_Euro3_2016.hex`

**ECU Details:**
- **Model:** Husqvarna 701 Enduro (2016)
- **Emission:** Euro 3
- **Hardware:** 760.41.031.000
- **Software:** KM270EU15E0301
- **Manufacturer:** Keihin
- **Size:** 1,310,720 bytes (1.25 MB)
- **Format:** Intel HEX

**Key Findings:**
- Contains structured key table at offset 0x87640
- BMW G450X key (0x1923) present
- Two new primary keys discovered (0x1D23, 0x1B23)
- Uses KWP2000 protocol with BMW addressing

## 🔍 Analysis

To analyze this firmware:

```bash
# From scripts directory
cd ../scripts

# Run main analysis
python3 analyze_ecu.py ../firmware/241019_701_enduro_Euro3_2016.hex

# Extract security keys
python3 extract_keys.py ../firmware/241019_701_enduro_Euro3_2016.hex
```

## 🔐 Security Key Locations

| Key      | Offset  | Context                    |
|----------|---------|----------------------------|
| 0x1D23   | 0x87640 | Primary key table entry    |
| 0x1B23   | 0x87640 | Primary key table entry    |
| 0x1923   | 0x87640 | Primary key table entry    |
| 0x1523   | 0x6B9A4 | Secondary reference        |
| 0x1023   | 0x876EE | Secondary reference        |

## 📝 Dump Information

**Extraction Method:** [Specify your method]
- Bench read with programmer
- Via OBD port
- Flash chip read
- etc.

**Date:** October 19, 2024 (from filename)

**Verification:**
- MD5: [To be calculated]
- SHA256: [To be calculated]

