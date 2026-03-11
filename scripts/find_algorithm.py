#!/usr/bin/env python3
"""
Algorithm Finder - Findet die Security Access Implementierung in der Firmware

Dieser Script hilft bei der Identifikation:
1. CPU-Architektur (Renesas SH2/SH4, ARM, etc.)
2. Security Access Handler (Service 0x27)
3. Algorithmus-Implementierung
"""

import struct
import sys
from collections import Counter

def identify_cpu_architecture(firmware):
    """Versucht die CPU-Architektur zu identifizieren"""
    print("=== CPU-Architektur Identifikation ===\n")
    
    # 1. Suche nach bekannten Interrupt-Vektoren am Anfang
    print("1. Analyse der Interrupt-Vektor-Tabelle (erste 256 Bytes):")
    vectors = []
    for i in range(0, min(256, len(firmware)), 4):
        addr = struct.unpack('>I', firmware[i:i+4])[0]
        vectors.append(addr)
    
    # Prüfe ob Adressen plausibel sind
    plausible_vectors = [v for v in vectors if 0x00000000 <= v <= 0x00200000]
    print(f"   Plausible Reset/Interrupt Vektoren: {len(plausible_vectors)}//{len(vectors)}")
    
    # 2. Suche nach Opcodes verschiedener Architekturen
    print("\n2. Opcode-Pattern Analyse:")
    
    # Renesas SH2/SH4 (häufig in Keihin ECUs)
    sh_patterns = {
        b'\x09\x00': 'NOP (SH)',
        b'\x00\x09': 'NOP (SH BE)',
        b'\x0b\x00': 'RTS (SH)',
        b'\x2b\x40': 'JMP @R0 (SH)',
    }
    
    # ARM Thumb
    arm_patterns = {
        b'\x00\xbf': 'NOP (ARM Thumb)',
        b'\x70\x47': 'BX LR (ARM Thumb)',
        b'\xfe\xe7': 'B . (ARM Thumb)',
    }
    
    # PowerPC
    ppc_patterns = {
        b'\x60\x00\x00\x00': 'NOP (PowerPC)',
        b'\x4e\x80\x00\x20': 'BLR (PowerPC)',
    }
    
    all_patterns = {**sh_patterns, **arm_patterns, **ppc_patterns}
    
    for pattern, name in all_patterns.items():
        count = firmware.count(pattern)
        if count > 100:  # Mindestens 100 Vorkommen
            print(f"   ✓ {name}: {count}x gefunden")
    
    # 3. Byte-Häufigkeitsanalyse
    print("\n3. Byte-Häufigkeitsanalyse (Code vs. Daten):")
    sample = firmware[0x20000:0x30000]  # Nehme Sample aus der Mitte
    byte_freq = Counter(sample)
    
    # Code hat typischerweise eine gleichmäßigere Verteilung als Daten
    entropy = len([b for b, count in byte_freq.items() if count > 10])
    print(f"   Byte-Diversität: {entropy}/256")
    
    if entropy < 128:
        print("   → Wahrscheinlich komprimierte oder verschlüsselte Daten")
    else:
        print("   → Wahrscheinlich executable Code")
    
    # 4. String-Analyse
    print("\n4. Debug-Strings (geben Hinweise auf Toolchain):")
    strings_to_find = [
        (b'SH', 'Renesas SuperH/SH'),
        (b'ARM', 'ARM Architecture'),
        (b'GCC', 'GNU Compiler Collection'),
        (b'IAR', 'IAR Embedded Workbench'),
        (b'Green', 'Green Hills Compiler'),
        (b'Keil', 'Keil/ARM Compiler'),
    ]
    
    for pattern, desc in strings_to_find:
        positions = []
        offset = 0
        while True:
            pos = firmware.find(pattern, offset)
            if pos == -1:
                break
            positions.append(pos)
            offset = pos + 1
        
        if positions:
            print(f"   ✓ {desc}: {len(positions)}x gefunden (z.B. bei 0x{positions[0]:X})")
    
    print("\n" + "="*60)
    print("VERMUTUNG: Keihin ECUs verwenden typischerweise:")
    print("  - Renesas SH2 oder SH4 CPU")
    print("  - Big-Endian Byte-Order")
    print("  - Compiler: Renesas oder Green Hills")
    print("="*60)

def find_service_27_handler(firmware):
    """Sucht nach dem Service 0x27 (Security Access) Handler"""
    print("\n\n=== Service 0x27 Handler Suche ===\n")
    
    # Suche nach charakteristischen Byte-Patterns
    patterns = [
        # Service ID 0x27 in verschiedenen Kontexten
        (b'\x27\x01', 'Service 0x27 Level 0x01 (Request Seed)'),
        (b'\x27\x02', 'Service 0x27 Level 0x02 (Send Key)'),
        (b'\x67\x01', 'Positive Response 0x67 Level 0x01'),
        (b'\x67\x02', 'Positive Response 0x67 Level 0x02'),
        (b'\x7F\x27', 'Negative Response für Service 0x27'),
        
        # Typische Vergleiche in Handler-Code
        (b'\x00\x27', 'Service ID Vergleich (0x27)'),
        (b'\x27\x00', 'Service ID Vergleich (0x27 BE)'),
    ]
    
    print("1. Pattern-Suche:")
    service_27_regions = []
    
    for pattern, description in patterns:
        offset = 0
        found_count = 0
        while offset < len(firmware):
            pos = firmware.find(pattern, offset)
            if pos == -1:
                break
            
            found_count += 1
            if found_count <= 5:  # Zeige nur erste 5
                print(f"   {description}: 0x{pos:X}")
                service_27_regions.append(pos)
            
            offset = pos + 1
        
        if found_count > 5:
            print(f"   ... und {found_count - 5} weitere")
    
    # Suche nach der Key-Tabelle (wir wissen sie ist bei 0x87640)
    print("\n2. Cross-Referenz zur Key-Tabelle (0x87640):")
    key_table_addr = 0x87640
    
    # Suche nach Referenzen zu dieser Adresse
    # Big Endian: 0x00087640
    ref_be = struct.pack('>I', key_table_addr)
    # Little Endian: 0x40760800
    ref_le = struct.pack('<I', key_table_addr)
    
    for ref_bytes, endian in [(ref_be, 'BE'), (ref_le, 'LE')]:
        pos = firmware.find(ref_bytes)
        if pos != -1:
            print(f"   ✓ Referenz ({endian}) gefunden bei 0x{pos:X}")
            print(f"     Context:")
            context = firmware[max(0, pos-32):min(len(firmware), pos+36)]
            hex_dump = ' '.join(f'{b:02x}' for b in context)
            print(f"     {hex_dump}")
    
    # 3. Suche nach Multiplikations-Opcodes in der Nähe von Service 0x27
    print("\n3. Suche nach Multiplikations-Operationen:")
    print("   (Der Algorithmus ist: Response = SEED * KEY)")
    
    mul_patterns = [
        (b'\x00\x20', 'MUL.L (SH2)'),
        (b'\x0f\x20', 'MULS.W (SH2)'),
        (b'\x0e\x20', 'MULU.W (SH2)'),
    ]
    
    for pattern, desc in mul_patterns:
        count = firmware.count(pattern)
        if count > 0:
            print(f"   {desc}: {count}x in Firmware")

def analyze_key_table_region(firmware):
    """Analysiert den Bereich um die Key-Tabelle"""
    print("\n\n=== Key-Tabelle Region (0x87640) ===\n")
    
    key_table_offset = 0x87640
    
    # Zeige größeren Context
    start = key_table_offset - 512
    end = key_table_offset + 512
    
    print("Suche nach Code in der Nähe der Key-Tabelle...")
    print("(Code der die Tabelle verwendet, ist wahrscheinlich nahe)")
    
    region = firmware[start:end]
    
    # Suche nach Funktions-Prologues (typisch für Renesas SH)
    # SH Funktionen starten oft mit: MOV.L R14, @-R15; STS.L PR, @-R15
    sh_prologue_patterns = [
        b'\x2f\xe6',  # MOV.L R14, @-R15
        b'\x2f\x46',  # STS.L PR, @-R15
    ]
    
    print("\n1. Funktions-Prologues in der Nähe:")
    for pattern in sh_prologue_patterns:
        offset = 0
        while offset < len(region):
            pos = region.find(pattern, offset)
            if pos == -1:
                break
            abs_pos = start + pos
            print(f"   Mögliche Funktion bei 0x{abs_pos:X}")
            offset = pos + 1
    
    # 2. Zeige die Bytes vor der Tabelle (könnte Code sein)
    print("\n2. Bytes vor der Key-Tabelle (möglicher Handler-Code):")
    pre_table = firmware[key_table_offset - 128:key_table_offset]
    
    print("   Offset    Hex                                      ASCII")
    for i in range(0, len(pre_table), 16):
        offset = key_table_offset - 128 + i
        chunk = pre_table[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"   0x{offset:06X}  {hex_str:<48} {ascii_str}")

def create_ghidra_script(firmware):
    """Erstellt ein Ghidra-Script für die Analyse"""
    print("\n\n=== Ghidra Script Generator ===\n")
    
    script = """// Ghidra Script für Husqvarna 701 ECU Analyse
// To use: Load firmware in Ghidra, then run this script

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;

public class AnalyzeHusqvarna701 extends GhidraScript {
    
    @Override
    public void run() throws Exception {
        println("=== Husqvarna 701 ECU Analysis ===");
        
        // 1. Markiere Key-Tabelle
        Address keyTableAddr = toAddr(0x87640);
        createLabel(keyTableAddr, "SecurityKeyTable", true);
        setEOLComment(keyTableAddr, "Security Access Key Table");
        
        // Markiere einzelne Keys
        createLabel(toAddr(0x8764C), "Key_1D23_Level20", false);
        createLabel(toAddr(0x87660), "Key_1B23_Level20", false);
        createLabel(toAddr(0x87674), "Key_1923_Level20", false);
        
        // 2. Markiere ECU-Identifier
        Address ecuIdentAddr = toAddr(0x13FFD6);
        createLabel(ecuIdentAddr, "ECU_Identifier_KM270", true);
        
        // 3. Suche nach Cross-References zur Key-Tabelle
        println("\\nSearching for references to key table...");
        Address[] refs = findBytes(keyTableAddr, 
            new byte[]{(byte)0x00, (byte)0x08, (byte)0x76, (byte)0x40},
            1000);
        
        for (Address ref : refs) {
            println("  Found reference at: " + ref);
            setEOLComment(ref, "REF to SecurityKeyTable");
        }
        
        // 4. Suche nach Service 0x27 Handlern
        println("\\nSearching for Service 0x27 handlers...");
        Address start = toAddr(0x20000);
        Address end = toAddr(0x100000);
        
        // Suche nach 0x27 Pattern
        byte[] pattern27 = new byte[]{0x27};
        Address current = start;
        
        while (current != null && current.compareTo(end) < 0) {
            Address found = find(current, pattern27);
            if (found == null || found.compareTo(end) >= 0) break;
            
            // Prüfe Context
            byte nextByte = getByte(found.add(1));
            if (nextByte == 0x01 || nextByte == 0x02) {
                println("  Possible Service 0x27 handler at: " + found);
                setEOLComment(found, "Service 0x27?");
            }
            
            current = found.add(1);
        }
        
        println("\\n=== Analysis Complete ===");
        println("Hint: Look for MULS/MULU instructions near Service 0x27 handlers");
    }
}
"""
    
    script_path = "analyze_husqvarna701.java"
    with open(script_path, 'w') as f:
        f.write(script)
    
    print(f"✓ Ghidra Script erstellt: {script_path}")
    print("\nUsage:")
    print("  1. Öffne Firmware in Ghidra")
    print("  2. Gehe zu Window > Script Manager")
    print("  3. Klicke auf 'Create New Script'")
    print("  4. Kopiere den Script-Inhalt")
    print("  5. Run Script")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_algorithm.py <firmware.hex>")
        sys.exit(1)
    
    firmware_file = sys.argv[1]
    
    print("="*60)
    print("  Algorithm Finder")
    print("  Husqvarna 701 ECU Firmware Analysis")
    print("="*60)
    print(f"\nAnalysiere: {firmware_file}\n")
    
    with open(firmware_file, 'rb') as f:
        firmware = f.read()
    
    print(f"Firmware-Größe: {len(firmware)} Bytes (0x{len(firmware):X})\n")
    
    # 1. Identifiziere CPU
    identify_cpu_architecture(firmware)
    
    # 2. Finde Service 0x27 Handler
    find_service_27_handler(firmware)
    
    # 3. Analysiere Key-Tabelle Region
    analyze_key_table_region(firmware)
    
    # 4. Erstelle Ghidra Script
    create_ghidra_script(firmware)
    
   
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
