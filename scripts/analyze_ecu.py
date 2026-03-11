#!/usr/bin/env python3
"""
ECU Firmware Analyzer - Sucht nach Security Access Keys
Basierend auf dem Forum-Thread: Die Keys sind 16-bit Werte, 
der Algorithmus ist: SEED * KEY mod 0x10000
"""

import sys
import struct

def find_potential_keys(firmware):
    """Findet potenzielle Security Keys in der Firmware"""
    
    # Bekannte Keys von anderen Keihin ECUs
    known_keys = {
        0x5106: "BMW G450X Level 1",
        0x1923: "BMW G450X Level 2", 
        0x6AD5: "Husqvarna 449 (gefunden via brute force)",
        0x1EC3: "Husqvarna 449 Level 2 (gefunden via brute force)"
    }
    
    print("=== Suche nach bekannten Keys ===")
    for key_val, description in known_keys.items():
        # Little Endian
        key_bytes_le = struct.pack('<H', key_val)
        # Big Endian
        key_bytes_be = struct.pack('>H', key_val)
        
        offset = 0
        while True:
            pos_le = firmware.find(key_bytes_le, offset)
            pos_be = firmware.find(key_bytes_be, offset)
            
            if pos_le == -1 and pos_be == -1:
                break
                
            if pos_le != -1:
                print(f"  ✓ 0x{key_val:04X} ({description}) gefunden bei Offset 0x{pos_le:X} (Little Endian)")
                # Zeige Kontext
                start = max(0, pos_le - 16)
                end = min(len(firmware), pos_le + 18)
                context = firmware[start:end]
                print(f"    Kontext: {context.hex(' ')}")
                offset = pos_le + 1
            
            if pos_be != -1 and pos_be != pos_le:
                print(f"  ✓ 0x{key_val:04X} ({description}) gefunden bei Offset 0x{pos_be:X} (Big Endian)")
                offset = pos_be + 1
            
            if pos_le == -1 and pos_be == -1:
                break
    
    print("\n=== Suche nach 'Sec' / 'Security' Strings ===")
    sec_strings = [b'Sec', b'sec', b'Security', b'security', b'seed', b'SEED', b'key', b'KEY']
    for s in sec_strings:
        offset = 0
        while True:
            pos = firmware.find(s, offset)
            if pos == -1:
                break
            print(f"  '{s.decode('latin1')}' gefunden bei Offset 0x{pos:X}")
            # Zeige Kontext
            start = max(0, pos - 16)
            end = min(len(firmware), pos + len(s) + 16)
            context = firmware[start:end]
            print(f"    Kontext: {context.hex(' ')}")
            offset = pos + 1
    
    print("\n=== Suche nach charakteristischen 16-bit Werten ===")
    # Suche nach Werten im Bereich 0x1000-0xFFFF die häufig vorkommen
    # (Keys könnten mehrfach referenziert werden)
    value_counts = {}
    for i in range(0, len(firmware) - 1, 2):
        val_le = struct.unpack('<H', firmware[i:i+2])[0]
        if 0x1000 <= val_le <= 0xFFFF and val_le != 0xFFFF:
            if val_le not in value_counts:
                value_counts[val_le] = []
            value_counts[val_le].append(i)
    
    # Zeige die häufigsten Werte (außer 0xFFFF)
    frequent = sorted([(len(positions), val, positions) for val, positions in value_counts.items()], reverse=True)
    print("  Top 20 häufigste 16-bit Werte (0x1000-0xFFFF, außer 0xFFFF):")
    for count, val, positions in frequent[:20]:
        if count > 5:  # Nur wenn öfter als 5x vorkommt
            print(f"    0x{val:04X}: {count}x gefunden (erste Offsets: {', '.join([f'0x{p:X}' for p in positions[:5]])})")
    
    print("\n=== ECU-Identifier ===")
    # Suche nach den bekannten ECU-Strings
    identifiers = [b'KM270', b'760.41.031', b'Keihin']
    for ident in identifiers:
        pos = firmware.find(ident)
        if pos != -1:
            print(f"  '{ident.decode('latin1')}' gefunden bei Offset 0x{pos:X}")
            start = max(0, pos - 32)
            end = min(len(firmware), pos + len(ident) + 32)
            context = firmware[start:end]
            try:
                print(f"    Kontext (ASCII): {context.decode('latin1', errors='replace')}")
            except:
                print(f"    Kontext (HEX): {context.hex(' ')}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_ecu.py <firmware.hex>")
        sys.exit(1)
    
    firmware_file = sys.argv[1]
    print(f"Analysiere Firmware: {firmware_file}\n")
    
    with open(firmware_file, 'rb') as f:
        firmware = f.read()
    
    print(f"Firmware-Größe: {len(firmware)} Bytes (0x{len(firmware):X})\n")
    
    find_potential_keys(firmware)

if __name__ == '__main__':
    main()
