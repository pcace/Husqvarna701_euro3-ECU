#!/usr/bin/env python3
"""
Key Extractor - Extrahiert alle potenziellen Security Keys aus der ECU Firmware
"""

import struct
import sys

def extract_keys_from_table(firmware, offset, length=256):
    """Extrahiert Keys aus der gefundenen Key-Tabelle"""
    print(f"\n=== Key-Tabelle bei Offset 0x{offset:X} ===")
    
    data = firmware[offset:offset+length]
    hex_dump = ' '.join(f'{b:02x}' for b in data)
    print(f"Raw Data: {hex_dump}\n")
    
    keys = []
    i = 0
    while i < len(data) - 3:
        # Suche nach "dSec" Pattern (64 53 65 63)
        if data[i:i+4] == b'dSec':
            print(f"  'dSec' Marker gefunden bei Offset 0x{offset+i:X}")
            # Die nächsten Bytes sollten Keys enthalten
            j = i + 4
            while j < min(i + 20, len(data) - 2):
                if data[j] == 0xd3:  # Möglicher Key-Prefix
                    key_be = struct.unpack('>H', data[j+1:j+3])[0]
                    level = data[j+3] if j+3 < len(data) else 0
                    print(f"    -> Key: 0x{key_be:04X} (level/type: 0x{level:02X}) bei Offset 0x{offset+j:X}")
                    keys.append((key_be, level, offset+j))
                    j += 4
                else:
                    j += 1
            i += 4
        else:
            i += 1
    
    return keys

def search_key_patterns(firmware):
    """Sucht nach allen möglichen Key-Mustern"""
    print("\n=== Suche nach Key-Mustern (d3 XX XX XX) ===")
    
    keys = []
    for i in range(len(firmware) - 3):
        if firmware[i] == 0xd3:
            # Prüfe ob die nächsten 2 Bytes ein sinnvoller Key sein könnten
            key_be = struct.unpack('>H', firmware[i+1:i+3])[0]
            level = firmware[i+3]
            
            # Filtern: Keys sollten im Bereich 0x1000-0xFFFF liegen
            if 0x1000 <= key_be <= 0xFFFF and key_be != 0xFFFF:
                # Prüfe ob der Context sinnvoll aussieht (umgebende Bytes)
                context = firmware[max(0, i-8):min(len(firmware), i+12)]
                if b'dSec' in context or b'Sec' in context:
                    keys.append((key_be, level, i))
    
    # Gruppiere Keys nach Wert
    from collections import defaultdict
    key_groups = defaultdict(list)
    for key, level, offset in keys:
        key_groups[key].append((level, offset))
    
    # Zeige Keys die mehrfach vorkommen oder nahe bei "Sec" sind
    print("\nPotenzielle Security Keys:")
    for key in sorted(key_groups.keys()):
        occurrences = key_groups[key]
        if len(occurrences) >= 2 or any(b'Sec' in firmware[max(0,off-10):off+10] for _, off in occurrences):
            print(f"  0x{key:04X}:")
            for level, offset in occurrences[:5]:  # Zeige max. 5 Vorkommen
                context_start = max(0, offset - 8)
                context_end = min(len(firmware), offset + 12)
                context = firmware[context_start:context_end]
                ascii_context = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
                print(f"    Level: 0x{level:02X}, Offset: 0x{offset:X}, Context: {ascii_context}")

def verify_known_algorithm(seed, key):
    """Verifiziert den bekannten Algorithmus: (SEED * KEY) & 0xFFFF"""
    result = (seed * key) & 0xFFFF
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_keys.py <firmware.hex>")
        sys.exit(1)
    
    firmware_file = sys.argv[1]
    
    with open(firmware_file, 'rb') as f:
        firmware = f.read()
    
    print(f"Analysiere Firmware: {firmware_file}")
    print(f"Firmware-Größe: {len(firmware)} Bytes (0x{len(firmware):X})\n")
    
    # Extrahiere Keys aus der bekannten Tabelle
    table_offset = 0x87640
    keys_from_table = extract_keys_from_table(firmware, table_offset, 128)
    
    # Suche nach weiteren Key-Mustern
    search_key_patterns(firmware)
    
    # Test mit bekanntem Algorithmus
    if keys_from_table:
        print("\n=== Test des Authentifizierungs-Algorithmus ===")
        print("Algorithmus: Response = (SEED * KEY) & 0xFFFF")
        test_seed = 0x1234
        for key, level, offset in set([(k, l, o) for k, l, o in keys_from_table]):
            response = verify_known_algorithm(test_seed, key)
            print(f"  Key 0x{key:04X} (Level 0x{level:02X}): SEED 0x{test_seed:04X} -> Response 0x{response:04X}")
    
    # Zeige Zusammenfassung
    print("\n=== ZUSAMMENFASSUNG ===")
    unique_keys = set([k for k, l, o in keys_from_table])
    print(f"Gefundene eindeutige Keys in der Tabelle: {len(unique_keys)}")
    for key in sorted(unique_keys):
        levels = set([l for k, l, o in keys_from_table if k == key])
        print(f"  0x{key:04X} (Levels: {', '.join(f'0x{l:02X}' for l in sorted(levels))})")

if __name__ == '__main__':
    main()
