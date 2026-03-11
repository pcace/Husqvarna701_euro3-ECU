#!/usr/bin/env python3
"""
Disassemble SEED/Response Algorithm
Zeigt die genaue Implementierung der Security Access Algorithmus
"""

# SuperH-2 Instruction Decoder (vereinfacht)
SH_OPCODES = {
    # Multiplikation
    0x200F: ("MULS.W", "R0, R0", "Signed 16-bit multiply: R0 * R0 → MACL"),
    0x210F: ("MULS.W", "R0, R1", "Signed 16-bit multiply: R0 * R1 → MACL"),
    0x220F: ("MULS.W", "R0, R2", "Signed 16-bit multiply: R0 * R2 → MACL"),
    0x230F: ("MULS.W", "R0, R3", "Signed 16-bit multiply: R0 * R3 → MACL"),
    0x240F: ("MULS.W", "R0, R4", "Signed 16-bit multiply: R0 * R4 → MACL"),
    0x250F: ("MULS.W", "R0, R5", "Signed 16-bit multiply: R0 * R5 → MACL"),
    
    0x200E: ("MULU.W", "R0, R0", "Unsigned 16-bit multiply: R0 * R0 → MACL"),
    0x210E: ("MULU.W", "R0, R1", "Unsigned 16-bit multiply: R0 * R1 → MACL"),
    0x220E: ("MULU.W", "R0, R2", "Unsigned 16-bit multiply: R0 * R2 → MACL"),
    
    # Register Operations
    0x6003: ("MOV", "R0, R0", "Move R0 to R0"),
    0x6013: ("MOV", "R1, R0", "Move R1 to R0"),
    0x6023: ("MOV", "R2, R0", "Move R2 to R0"),
    0x6033: ("MOV", "R3, R0", "Move R3 to R0"),
    0x6043: ("MOV", "R4, R0", "Move R4 to R0"),
    
    # MAC Register Access
    0x001A: ("STS", "MACL, R0", "Store MACL to R0 (result)"),
    0x011A: ("STS", "MACL, R1", "Store MACL to R1 (result)"),
    0x021A: ("STS", "MACL, R2", "Store MACL to R2 (result)"),
    
    # Logic Operations
    0x2009: ("AND", "R0, R0", "AND R0 with R0"),
    0x2209: ("AND", "R0, R2", "AND R0 with R2"),
    0x2C09: ("AND", "R0, R12", "AND R0 with R12"),
    
    # Compare
    0x3000: ("CMP/EQ", "R0, R0", "Compare R0 == R0"),
    0x3100: ("CMP/EQ", "R0, R1", "Compare R0 == R1"),
    
    # Branch
    0x8900: ("BT", "label", "Branch if T=1"),
    0x8B00: ("BF", "label", "Branch if T=0"),
    
    0x0009: ("NOP", "", "No operation"),
    0x000B: ("RTS", "", "Return from subroutine"),
}

def decode_sh_instruction(word):
    """Decode SuperH instruction (16-bit little-endian)"""
    # Try exact match
    if word in SH_OPCODES:
        return SH_OPCODES[word]
    
    # Try pattern matching
    opcode_high = (word >> 12) & 0xF
    
    if opcode_high == 0x2 and (word & 0xF) == 0xF:
        rn = (word >> 8) & 0xF
        rm = (word >> 4) & 0xF
        return ("MULS.W", f"R{rm}, R{rn}", f"Signed multiply R{rm} * R{rn} → MACL")
    
    if opcode_high == 0x2 and (word & 0xF) == 0xE:
        rn = (word >> 8) & 0xF
        rm = (word >> 4) & 0xF
        return ("MULU.W", f"R{rm}, R{rn}", f"Unsigned multiply R{rm} * R{rn} → MACL")
    
    if opcode_high == 0x0 and (word & 0xFF) == 0x1A:
        n = (word >> 8) & 0xF
        return ("STS", f"MACL, R{n}", f"Store MACL result to R{n}")
    
    if opcode_high == 0x6 and (word & 0xF) == 0x3:
        rn = (word >> 8) & 0xF
        rm = (word >> 4) & 0xF
        return ("MOV", f"R{rm}, R{rn}", f"Move R{rm} to R{rn}")
    
    if opcode_high == 0x2 and (word & 0xF) == 0x9:
        rn = (word >> 8) & 0xF
        rm = (word >> 4) & 0xF
        return ("AND", f"R{rm}, R{rn}", f"AND R{rm} with R{rn}")
    
    if opcode_high == 0xE:
        n = (word >> 8) & 0xF
        imm = word & 0xFF
        return ("MOV", f"#0x{imm:02X}, R{n}", f"Load immediate 0x{imm:02X} into R{n}")
    
    if opcode_high == 0xC and (word & 0xF00) == 0x900:
        disp = word & 0xFF
        return ("AND", f"#0x{disp:02X}, R0", f"AND immediate 0x{disp:02X} with R0")
    
    return (None, None, None)

def disassemble_region(firmware, address, count=20):
    """Disassemble region showing SuperH instructions"""
    print(f"\n{'='*70}")
    print(f"Disassembly @ 0x{address:06X}")
    print(f"{'='*70}")
    
    for i in range(count):
        offset = address + (i * 2)
        if offset + 1 >= len(firmware):
            break
        
        # Read 16-bit word (little-endian within word, but bytes stored big-endian)
        b1 = firmware[offset]
        b2 = firmware[offset + 1]
        word = (b2 << 8) | b1  # Little-endian 16-bit word
        
        mnemonic, operands, description = decode_sh_instruction(word)
        
        if mnemonic:
            print(f"0x{offset:06X}:  {b1:02X} {b2:02X}  {mnemonic:8s} {operands:15s}  ; {description}")
        else:
            print(f"0x{offset:06X}:  {b1:02X} {b2:02X}  .word 0x{word:04X}")

def analyze_algorithm_candidates(firmware):
    """Analysiere die beiden Hauptkandidaten für den Algorithmus"""
    
    print("\n" + "="*70)
    print("SECURITY ACCESS ALGORITHM - CODE ANALYSIS")
    print("="*70)
    
    # Kandidat 1: MULS.W @ 0x02A2D6
    print("\n[1] MULS.W @ 0x02A2D6 (949 bytes from Service 0x27)")
    print("    Wahrscheinlich: Response Validation Algorithm")
    print("    Erwartet: (SEED * KEY) & 0xFFFF")
    disassemble_region(firmware, 0x02A2B0, 40)
    
    # Kandidat 2: MULU.W @ 0x02F3DE
    print("\n" + "="*70)
    print("[2] MULU.W @ 0x02F3DE (1020 bytes from Service 0x27)")
    print("    Alternative: Unsigned Multiply")
    disassemble_region(firmware, 0x02F3C0, 40)
    
    # Key-Erkennung Code
    print("\n" + "="*70)
    print("[3] Key Extraction @ 0x87640")
    print("    Die Security Key Tabelle")
    print("="*70)
    offset = 0x87640
    for i in range(10):
        addr = offset + (i * 4)
        if addr + 3 < len(firmware):
            b0, b1, b2, b3 = firmware[addr:addr+4]
            if b0 == 0xd3:  # Key marker
                key = (b1 << 8) | b2
                level = b3
                print(f"0x{addr:06X}: d3 {b1:02X} {b2:02X} {b3:02X}  KEY=0x{key:04X}  Level=0x{level:02X}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 disassemble_algorithm.py <firmware.hex>")
        sys.exit(1)
    
    with open(sys.argv[1], 'rb') as f:
        firmware = f.read()
    
    print(f"Firmware: {sys.argv[1]} ({len(firmware)} bytes)")
    
    analyze_algorithm_candidates(firmware)
    
    # Zusammenfassung
    print("\n" + "="*70)
    print("INTERPRETATION:")
    print("="*70)
    print("""
Die MULS.W Instruktion @ 0x02A2D6 ist höchstwahrscheinlich der
Response-Validierungs-Code:

1. ECU sendet SEED (Service 0x27 0x01 → Response 0x67 0x01 [SEED_HI] [SEED_LO])
2. Fahrzeug lädt KEY aus Tabelle @ 0x87640
3. Fahrzeug berechnet: Response = (SEED * KEY) & 0xFFFF
4. Fahrzeug sendet Response (Service 0x27 0x02 [RESP_HI] [RESP_LO])
5. ECU validiert mit MULS.W: Berechnet (SEED * empfangener_KEY) in MACL
6. ECU vergleicht MACL & 0xFFFF mit erwartetem Response
7. Bei Übereinstimmung: 0x67 0x02 (Success), sonst 0x7F 0x27 0x35 (Failure)

Für vollständige Code-Analyse: Verwende Ghidra zur Decompilierung!

Nächste Schritte:
- Ghidra: Importiere Firmware mit SuperH:LE:32:default
- Navigiere zu 0x02A2D6 und analysiere Funktion
- Hardware-Test: python3 ecu_tester.py mit echtem ECU
""")

if __name__ == '__main__':
    main()
