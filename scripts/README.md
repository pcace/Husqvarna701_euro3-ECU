# Analysis & Testing Scripts

This directory contains all Python, Java, and Radare2 scripts for ECU firmware analysis and hardware testing.

## 📁 Files Overview

### Main Analysis Tools

- **`analyze_ecu.py`** - Primary firmware analysis tool
  - Searches for known security keys
  - Finds patterns and strings related to authentication
  - Identifies frequent 16-bit values
  - Locates ECU identifiers

- **`extract_keys.py`** - Security key extraction utility
  - Extracts keys from identified key table
  - Validates key structure
  - Exports keys in various formats

### Hardware Testing

- **`ecu_tester.py`** - Hardware interface testing tool
  - Tests discovered keys with real ECU
  - Supports ELM327, VAG409, and other K-Line interfaces
  - Includes dummy/simulation mode for safe testing
  - Automatic seed/response calculation

- **`brute_force_keys.py`** - Brute-force key discovery (fallback)
  - Systematically tests 16-bit key space
  - Optimized with known patterns
  - Includes timeout and retry logic
  - Use only as last resort

### Algorithm Analysis

- **`find_algorithm.py`** - Authentication algorithm discovery
  - Locates authentication functions in firmware
  - Pattern matching for seed/key operations
  - Cross-references with known implementations

- **`find_seed_function.py`** - Seed generation analysis
  - Finds seed generation functions
  - Analyzes randomness sources
  - Documents seed behavior

- **`disassemble_algorithm.py`** - Algorithm disassembly
  - Disassembles authentication routines
  - Converts to readable pseudocode
  - Validates against known algorithm

### External Tool Scripts

- **`analyze_husqvarna701.java`** - Ghidra automation script
  - Imports firmware into Ghidra
  - Auto-analyzes key structures
  - Marks important functions
  - See [GHIDRA_TUTORIAL.md](../GHIDRA_TUTORIAL.md) for usage

- **`analyze_security.r2`** - Radare2 script
  - Automated Radare2 analysis
  - Finds authentication functions
  - Generates cross-references

### Analysis Results

- **`analysis_result.txt`** - Output from firmware analysis
  - Contains findings from analyze_ecu.py
  - Key locations and contexts
  - Pattern analysis results

## 🚀 Usage Examples

### Analyze Firmware
```bash
python3 analyze_ecu.py ../firmware/241019_701_enduro_Euro3_2016.hex
```

### Extract Keys
```bash
python3 extract_keys.py ../firmware/241019_701_enduro_Euro3_2016.hex
```

### Test Without Hardware (Safe)
```bash
python3 ecu_tester.py --dummy
```

### Test With Hardware
```bash
# Find your serial port first
python3 -m serial.tools.list_ports

# Then test
python3 ecu_tester.py /dev/tty.usbserial
```

### Brute Force (Last Resort)
```bash
python3 brute_force_keys.py /dev/tty.usbserial --start 0x1000 --end 0x2000
```

## ⚠️ Safety Notes

- Always test with `--dummy` mode first
- Start with Level 0x20 (read-only)
- Wait between attempts to avoid ECU lockout
- Never use on a bike you can't afford to brick

## 📝 Requirements

```bash
pip install pyserial
```

Optional for analysis:
```bash
pip install hexdump
```

## 🔗 See Also

- [Main README](../README.md) - Complete project overview
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) - Fast command lookup
- [REVERSE_ENGINEERING_GUIDE.md](../REVERSE_ENGINEERING_GUIDE.md) - Detailed methodology
