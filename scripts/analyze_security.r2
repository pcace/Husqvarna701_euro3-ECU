#!/usr/bin/env r2 -i
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
f SuccessResponse_67_02 @ 0x887C5

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
s 0x886C5
pd 128


# Zeige Functions
echo "[*] Functions list:"
afl

echo "[*] Analysis complete. Use 'pdf @ <address>' to disassemble functions."
