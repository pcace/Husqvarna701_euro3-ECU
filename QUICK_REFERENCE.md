# Quick Reference - Husqvarna 701 ECU

## 🔑 Security Keys

| Key    | Levels       | Priority |
|--------|--------------|----------|
| 0x1D23 | 20, 40, 50   | NEW      |
| 0x1B23 | 20, 40, 50   | NEW      |
| 0x1923 | 20, 40, 50   | BMW      |
| 0x1523 | 21, 41, 50   | Alt      |
| 0x1023 | 20, 40       | Alt      |

## 🚀 Quick Test

```bash
# Automated test
cd scripts
python3 ecu_tester.py --dummy        # Safe simulation
python3 ecu_tester.py /dev/ttyUSB0   # Real hardware

# Manual test (ELM327)
screen /dev/ttyUSB0 38400
ATZ                    # Reset
ATSP5                  # KWP2000
ATSH 12                # ECU address (⚠️ not 0x33!)
27 01                  # Request seed → 67 01 XX XX
27 02 YY YY            # Send response → 67 02 (success)
```

## 🧮 Algorithm

```python
response = (seed * key) & 0xFFFF
```

**Example:** SEED `0x1234` + KEY `0x1D23` → Response `0x611C`

## 📍 Addresses

```
ECU:    0x12  (BMW-specific, not standard 0x33!)
Tester: 0xF1
```

## 📊 Response Codes

| Code      | Meaning      |
|-----------|--------------|
| `67 02`   | ✅ Success   |
| `7F 27 35`| ❌ Invalid key |
| `7F 27 37`| ⚠️ ECU locked |

## ⚠️ Warnings

- ECU locks after 3-5 failed attempts (~10 min)
- Start with Level `0x20` (safe read-only)
- Avoid Level `0x50` (programming mode)

## 🎯 Test Order

1. `0x1923` @ Level `0x20` (BMW G450X - highest confidence)
2. `0x1D23` @ Level `0x20` (Primary)
3. `0x1B23` @ Level `0x20` (Primary)
