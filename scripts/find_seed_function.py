#!/usr/bin/env python3
"""
SEED Function Finder - Findet die Security Access Implementierung
Sucht speziell nach:
1. SEED-Generierungs-Funktion (Service 0x27, Level 0x01)
2. Response-Validierungs-Funktion (Service 0x27, Level 0x02)
3. Multiplikations-Code (SEED * KEY)
"""

import struct
import sys

def find_seed_generation_code(firmware):
    """Findet die SEED-Generierungs-Funktion"""
    print("="*70)
    print("  1. SEED-GENERIERUNGS-FUNKTION SUCHEN")
    print("="*70)
    
    # Service 0x27 0x01 = Request Seed
    # Positive Response: 0x67 0x01 <SEED_HI> <SEED_LO>
    
    print("\n📍 Suche nach Positive Response Pattern (67 01)...")
    pattern = b'\x67\x01'
    
    positions = []
    offset = 0
    while offset < len(firmware):
        pos = firmware.find(pattern, offset)
        if pos == -1:
            break
        positions.append(pos)
        offset = pos + 1
    
    print(f"✓ Gefunden: {len(positions)} Vorkommen von 0x67 0x01\n")
    
    # Analysiere jeden Fund
    for i, pos in enumerate(positions[:10]):  # Max 10 anzeigen
        print(f"\n--- Position {i+1}: 0x{pos:06X} ---")
        
        # Zeige Context (256 Bytes davor)
        context_start = max(0, pos - 256)
        context_end = min(len(firmware), pos + 64)
        context = firmware[context_start:context_end]
        
        # Suche nach interessanten Patterns im Context
        has_service_27 = b'\x27' in context
        has_random = b'rand' in context.lower() or b'seed' in context.lower()
        has_mul = b'\x0f\x20' in context or b'\x0e\x20' in context  # MULS.W, MULU.W
        
        print(f"  Context @ 0x{context_start:06X} - 0x{context_end:06X}")
        print(f"  • Service 0x27 nearby: {'✓' if has_service_27 else '✗'}")
        print(f"  • Random/Seed string: {'✓' if has_random else '✗'}")
        print(f"  • Multiply opcode:    {'✓' if has_mul else '✗'}")
        
        # Zeige die Bytes um den Fund herum
        snippet_start = max(0, pos - 32)
        snippet_end = min(len(firmware), pos + 32)
        snippet = firmware[snippet_start:snippet_end]
        
        print(f"\n  Bytes @ 0x{pos:06X}:")
        for j in range(0, len(snippet), 16):
            offset_addr = snippet_start + j
            chunk = snippet[j:j+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            marker = "<<<" if offset_addr <= pos < offset_addr + 16 else ""
            print(f"    {offset_addr:06X}  {hex_str:<48} {ascii_str}  {marker}")

def find_response_validation_code(firmware):
    """Findet die Response-Validierungs-Funktion"""
    print("\n\n" + "="*70)
    print("  2. RESPONSE-VALIDIERUNGS-FUNKTION SUCHEN")
    print("="*70)
    
    # Service 0x27 0x02 = Send Key
    # Success: 0x67 0x02
    # Fail: 0x7F 0x27 0x35 (Invalid Key)
    
    print("\n📍 Suche nach Success Response (67 02)...")
    success_positions = []
    offset = 0
    while offset < len(firmware):
        pos = firmware.find(b'\x67\x02', offset)
        if pos == -1:
            break
        success_positions.append(pos)
        offset = pos + 1
    
    print(f"✓ Gefunden: {len(success_positions)} Vorkommen\n")
    
    print("📍 Suche nach Failure Response (7F 27 35)...")
    fail_positions = []
    offset = 0
    while offset < len(firmware):
        pos = firmware.find(b'\x7F\x27\x35', offset)
        if pos == -1:
            break
        fail_positions.append(pos)
        offset = pos + 1
    
    print(f"✓ Gefunden: {len(fail_positions)} Vorkommen\n")
    
    # Analysiere Success Responses
    print("\n🔍 Analysiere Success Response Bereiche:")
    print("(Hier sollte die Response-Berechnung sein)\n")
    
    for i, pos in enumerate(success_positions[:5]):
        print(f"\n--- Success Response {i+1}: 0x{pos:06X} ---")
        
        # 512 Bytes davor analysieren
        code_start = max(0, pos - 512)
        code_region = firmware[code_start:pos]
        
        # Suche nach Multiplikations-Opcodes
        mul_positions = []
        for opcode, name in [(b'\x0f\x20', 'MULS.W'), (b'\x0e\x20', 'MULU.W'), 
                              (b'\x07\x20', 'MUL.L'), (b'\x17\x20', 'MUL.L')]:
            offset = 0
            while offset < len(code_region):
                mul_pos = code_region.find(opcode, offset)
                if mul_pos == -1:
                    break
                abs_pos = code_start + mul_pos
                mul_positions.append((abs_pos, name))
                offset = mul_pos + 1
        
        if mul_positions:
            print(f"  ✓ Multiplikations-Opcodes gefunden:")
            for mul_pos, name in mul_positions[:3]:
                print(f"    • {name} @ 0x{mul_pos:06X}")
                # Zeige Code um Multiplikation
                ctx_start = max(0, mul_pos - 16)
                ctx_end = min(len(firmware), mul_pos + 16)
                ctx = firmware[ctx_start:ctx_end]
                hex_str = ' '.join(f'{b:02x}' for b in ctx)
                print(f"      Context: {hex_str}")
        else:
            print(f"  ✗ Keine Multiplikations-Opcodes in den 512 Bytes davor")
        
        # Suche nach Key-Table-Referenzen
        key_table_ref = struct.pack('>I', 0x87640)
        if key_table_ref in code_region:
            ref_pos = code_region.find(key_table_ref)
            abs_ref_pos = code_start + ref_pos
            print(f"  ✓ Key-Table Referenz (0x87640) gefunden @ 0x{abs_ref_pos:06X}")
    
    # Analysiere Failure Responses
    print("\n\n🔍 Analysiere Failure Response Bereiche:")
    print("(Hier wird verglichen ob Response == Calculated)\n")
    
    for i, pos in enumerate(fail_positions[:3]):
        print(f"\n--- Failure Response {i+1}: 0x{pos:06X} ---")
        
        # Zeige Context
        ctx_start = max(0, pos - 64)
        ctx_end = min(len(firmware), pos + 32)
        
        print(f"  Context vor Failure (möglicher Vergleich):")
        ctx = firmware[ctx_start:ctx_end]
        for j in range(0, len(ctx), 16):
            offset_addr = ctx_start + j
            chunk = ctx[j:j+16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            marker = "<<<FAIL" if offset_addr <= pos < offset_addr + 16 else ""
            print(f"    {offset_addr:06X}  {hex_str:<48} {ascii_str}  {marker}")

def find_multiplication_regions(firmware):
    """Findet alle Bereiche mit Multiplikations-Code"""
    print("\n\n" + "="*70)
    print("  3. MULTIPLIKATIONS-CODE ANALYSIEREN")
    print("="*70)
    
    mul_opcodes = [
        (b'\x0f\x20', 'MULS.W Rm, Rn'),
        (b'\x0e\x20', 'MULU.W Rm, Rn'),
        (b'\x07\x20', 'MUL.L Rm, Rn'),
    ]
    
    print("\n📍 Suche nach allen Multiplikations-Opcodes...\n")
    
    all_muls = []
    
    for opcode_bytes, name in mul_opcodes:
        offset = 0
        count = 0
        while offset < len(firmware):
            pos = firmware.find(opcode_bytes, offset)
            if pos == -1:
                break
            all_muls.append((pos, name, opcode_bytes))
            count += 1
            offset = pos + 1
        
        print(f"  {name}: {count}x gefunden")
    
    # Sortiere nach Position
    all_muls.sort(key=lambda x: x[0])
    
    print(f"\n✓ Total: {len(all_muls)} Multiplikations-Instruktionen\n")
    
    # Filter: Nur die in der Nähe von Service 0x27 Code
    print("🔍 Filter: Multiplikationen in der Nähe von Service 0x27...\n")
    
    service_27_regions = []
    offset = 0
    while offset < len(firmware):
        pos = firmware.find(b'\x27', offset)
        if pos == -1:
            break
        service_27_regions.append(pos)
        offset = pos + 1
    
    relevant_muls = []
    for mul_pos, mul_name, mul_bytes in all_muls:
        # Prüfe ob innerhalb 1KB von einem Service 0x27
        for s27_pos in service_27_regions:
            if abs(mul_pos - s27_pos) < 1024:
                relevant_muls.append((mul_pos, mul_name, s27_pos))
                break
    
    print(f"✓ {len(relevant_muls)} Multiplikationen nahe bei Service 0x27\n")
    
    # Zeige die relevantesten
    print("📊 Top relevante Multiplikations-Bereiche:\n")
    for i, (mul_pos, mul_name, s27_pos) in enumerate(relevant_muls[:10]):
        distance = mul_pos - s27_pos
        print(f"{i+1}. {mul_name} @ 0x{mul_pos:06X}")
        print(f"   Service 0x27 @ 0x{s27_pos:06X} (Abstand: {distance:+d} Bytes)")
        
        # Zeige Code
        ctx_start = max(0, mul_pos - 8)
        ctx_end = min(len(firmware), mul_pos + 24)
        ctx = firmware[ctx_start:ctx_end]
        hex_str = ' '.join(f'{b:02x}' for b in ctx)
        print(f"   Code: {hex_str}\n")

def create_radare2_analysis_script(firmware):
    """Erstellt ein r2 Script für detaillierte Analyse"""
    print("\n\n" + "="*70)
    print("  4. RADARE2 ANALYSE-SCRIPT")
    print("="*70)
    
    # Finde interessante Adressen
    success_pos = firmware.find(b'\x67\x02')
    fail_pos = firmware.find(b'\x7F\x27\x35')
    
    script = f"""#!/usr/bin/env r2 -i
# Radare2 Script für Husqvarna 701 Security Access Analyse
# Usage: r2 -a sh -b 32 -i analyze_security.r2 241019_701_enduro_Euro3_2016.hex

# Setup
e asm.arch=sh
e asm.bits=32
e cfg.bigendian=true

# Analyse
echo "[*] Starting analysis..."
aaa

# Markiere Key-Tabelle
f SecurityKeyTable @ 0x87640
Cd 64 @ 0x87640

# Markiere bekannte Adressen
"""
    
    if success_pos != -1:
        script += f"f SuccessResponse_67_02 @ 0x{success_pos:X}\n"
    
    if fail_pos != -1:
        script += f"f FailureResponse_7F_27_35 @ 0x{fail_pos:X}\n"
    
    script += """
# Suche nach Multiplikationen
echo "[*] Searching for multiply instructions..."
/x 0f20
/x 0e20
/x 0720

# Suche nach Service 0x27 Handler
echo "[*] Searching for Service 0x27 patterns..."
/x 2701
/x 2702

# Cross-References zur Key-Tabelle
echo "[*] Looking for references to key table..."
/x 00087640

# Disassemble um Success Response
"""
    
    if success_pos != -1:
        script += f"s 0x{max(0, success_pos - 256):X}\n"
        script += "pd 128\n\n"
    
    script += """
# Zeige Functions
echo "[*] Functions list:"
afl

echo "[*] Analysis complete. Use 'pdf @ <address>' to disassemble functions."
"""
    
    script_file = "analyze_security.r2"
    with open(script_file, 'w') as f:
        f.write(script)
    
    print(f"\n✓ Radare2-Script erstellt: {script_file}")
    print("\nUsage:")
    print(f"  r2 -a sh -b 32 -i {script_file} 241019_701_enduro_Euro3_2016.hex")
    print("\nOder interaktiv:")
    print(f"  r2 -a sh -b 32 241019_701_enduro_Euro3_2016.hex")
    print(f"  [0x00000000]> . {script_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_seed_function.py <firmware.hex>")
        sys.exit(1)
    
    firmware_file = sys.argv[1]
    
    print("="*70)
    print("  SEED & RESPONSE FUNCTION FINDER")
    print("  Husqvarna 701 ECU Firmware")
    print("="*70)
    print(f"\nAnalysiere: {firmware_file}\n")
    
    with open(firmware_file, 'rb') as f:
        firmware = f.read()
    
    print(f"Firmware-Größe: {len(firmware)} Bytes (0x{len(firmware):X})\n")
    
    # 1. Finde SEED Generation
    find_seed_generation_code(firmware)
    
    # 2. Finde Response Validation
    find_response_validation_code(firmware)
    
    # 3. Analysiere Multiplikations-Code
    find_multiplication_regions(firmware)
    
    # 4. Erstelle r2 Script
    create_radare2_analysis_script(firmware)
    
    # Zusammenfassung
    print("\n\n" + "="*70)
    print("  ZUSAMMENFASSUNG & NÄCHSTE SCHRITTE")
    print("="*70)
    
    print("""
📝 Was wir jetzt wissen:

1. ✓ Service 0x27 Handler-Bereiche identifiziert
2. ✓ Positive/Negative Response Positionen gefunden
3. ✓ Multiplikations-Code in der Nähe lokalisiert

🎯 Nächste Schritte für vollständige Bestätigung:

1. RADARE2 DEEP DIVE:
   r2 -a sh -b 32 -i analyze_security.r2 241019_701_enduro_Euro3_2016.hex
   
   # Dann im r2:
   s <SuccessResponse_Adresse>   # Zu interessanter Stelle springen
   pdf                           # Function disassemblieren
   V                             # Visual Mode für bessere Übersicht

2. GHIDRA ANALYSE:
   - Öffne Firmware in Ghidra (siehe GHIDRA_TUTORIAL.md)
   - Springe zu den gefundenen Adressen
   - Nutze Decompiler für C-Code
   - Folge Funktions-Calls mit Decompiler

3. MANUELLE INSPEKTION:
   - Schaue dir die Bytes um die Multiplikationen an
   - Identifiziere SEED Parameter (in welchem Register?)
   - Identifiziere KEY Parameter (aus Tabelle oder wo?)
   - Verfolge Datenfluss bis zum Vergleich

4. ERWARTETER ALGORITHMUS (zur Bestätigung):
   
   Assembly (Renesas SH):
   ----------------------
   ; SEED in r4, Key-Table-Pointer in r5
   mov.w   @r5, r6          ; Lade KEY
   muls.w  r4, r6           ; SEED * KEY
   sts     macl, r0         ; Result in r0
   extu.w  r0, r0           ; AND 0xFFFF (nur untere 16 bit)
   
   ; r0 enthält jetzt die erwartete Response
   ; Vergleiche mit empfangener Response
   cmp/eq  r7, r0           ; r7 = empfangene Response
   bt      success          ; Branch if True
   ; else: failure (7F 27 35)

💡 QUICK CHECK:
   Wenn du die Multiplikations-Instruktion findest UND sie liegt zwischen:
   - Einem SEED-Wert (von ECU generiert oder aus Request gelesen)
   - Einem KEY-Wert (aus Tabelle bei 0x87640)
   - Und dem Ergebnis wird mit der empfangenen Response verglichen
   
   → DANN hast du die BESTÄTIGUNG! ✓

🚀 ODER: Teste einfach die Keys mit Hardware!
   python3 ecu_tester.py /dev/tty.usbserial
   
   Wenn ein Key funktioniert = Algorithmus bestätigt! 😉
""")

if __name__ == '__main__':
    main()
