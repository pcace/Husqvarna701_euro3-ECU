#!/usr/bin/env python3
"""
ECU Security Access Tester
Testet die gefundenen Security Keys auf einer Husqvarna 701 ECU

Hardware-Anforderungen:
- ELM327 oder ähnlicher K-Line/CAN Interface
- Verbindung zur ECU über OBD-Diagnose-Port

Basierend auf dem Forum-Thread:
- Algorithmus: Response = (SEED * KEY) & 0xFFFF
- BMW ECU Adresse: 0x12 (nicht Standard 0x33!)
- Tester Adresse: 0xF1
"""

import serial
import time
import sys

class ECUTester:
    def __init__(self, port='/dev/tty.usbserial-A50285BI', baudrate=38400):
        """
        Initialisiert die Verbindung zur ECU
        
        Für ELM327:
        - Baudrate: typisch 38400 oder 115200
        - Port: /dev/tty.usbserial-... (macOS)
                /dev/ttyUSB0 (Linux)
                COM3 (Windows)
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
        # Gefundene Keys aus der Firmware-Analyse
        self.keys = {
            '0x1D23 (Level 0x20)': (0x1D23, 0x20),
            '0x1D23 (Level 0x40)': (0x1D23, 0x40),
            '0x1D23 (Level 0x50)': (0x1D23, 0x50),
            '0x1B23 (Level 0x20)': (0x1B23, 0x20),
            '0x1B23 (Level 0x40)': (0x1B23, 0x40),
            '0x1B23 (Level 0x50)': (0x1B23, 0x50),
            '0x1923 (Level 0x20)': (0x1923, 0x20),  # BMW G450X Key
            '0x1923 (Level 0x40)': (0x1923, 0x40),
            '0x1923 (Level 0x50)': (0x1923, 0x50),
            '0x1523 (Level 0x21)': (0x1523, 0x21),
            '0x1523 (Level 0x41)': (0x1523, 0x41),
            '0x1523 (Level 0x50)': (0x1523, 0x50),
            '0x1023 (Level 0x20)': (0x1023, 0x20),
            '0x1023 (Level 0x40)': (0x1023, 0x40),
            # Bekannte Husqvarna 449 Keys zum Vergleich
            '0x6AD5 (449 Key 1)': (0x6AD5, 0x00),
            '0x1EC3 (449 Key 2)': (0x1EC3, 0x00),
        }
    
    def connect(self):
        """Verbindet mit dem ELM327/K-Line Interface"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Warte bis Interface bereit ist
            print(f"✓ Verbunden mit {self.port} @ {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"✗ Fehler beim Verbinden: {e}")
            return False
    
    def send_command(self, cmd):
        """Sendet einen AT/OBD Befehl"""
        if self.ser is None:
            return None
        
        self.ser.write((cmd + '\r').encode())
        time.sleep(0.1)
        response = self.ser.read(1000).decode('utf-8', errors='ignore')
        return response.strip()
    
    def init_elm327(self):
        """Initialisiert ELM327 für K-Line Kommunikation mit BMW ECU"""
        print("\n=== Initialisiere ELM327 ===")
        
        commands = [
            ('ATZ', 'Reset ELM327'),
            ('ATE0', 'Echo off'),
            ('ATL0', 'Linefeeds off'),
            ('ATSP5', 'ISO 14230-4 KWP (5 baud init)'),
            ('ATSH 12', 'Setze ECU Header auf 0x12 (BMW Adresse)'),
            ('ATTR 0xF1', 'Setze Tester Adresse auf 0xF1'),
            ('ATAT1', 'Adaptive Timing Auto'),
        ]
        
        for cmd, description in commands:
            print(f"  {description}: {cmd}")
            response = self.send_command(cmd)
            print(f"    -> {response}")
            if 'ERROR' in response:
                print(f"    ⚠ Warnung: Fehler bei {cmd}")
        
        print("✓ ELM327 initialisiert")
    
    def read_ecu_info(self):
        """Liest ECU-Informationen aus"""
        print("\n=== Lese ECU-Informationen ===")
        
        # VIN (Vehicle Identification Number) - Service 0x09, PID 0x02
        print("  Versuche VIN zu lesen...")
        response = self.send_command('0902')
        print(f"    VIN: {response}")
        
        # ECU Identifikation - Service 0x1A (Read ECU Identification)
        print("  Versuche ECU ID zu lesen...")
        response = self.send_command('1A87')  # HW Number
        print(f"    HW: {response}")
        
        response = self.send_command('1A89')  # SW Number
        print(f"    SW: {response}")
    
    def request_seed(self, level=0x01):
        """
        Fordert einen SEED von der ECU an
        Service: 0x27 (Security Access)
        Level: ungerade Zahl (0x01, 0x03, 0x05, etc.) = Request Seed
        """
        cmd = f"27{level:02X}"
        print(f"\n  -> Request SEED (Level 0x{level:02X}): {cmd}")
        response = self.send_command(cmd)
        print(f"  <- Response: {response}")
        
        # Parse Response: Should be 67 <level> <seed_high> <seed_low>
        if response and len(response) >= 10:
            try:
                # Entferne Whitespace und parse Hex
                hex_response = response.replace(' ', '').replace('>', '')
                if hex_response.startswith('67'):
                    seed_hex = hex_response[4:8]  # 2 Bytes SEED
                    seed = int(seed_hex, 16)
                    print(f"  ✓ SEED erhalten: 0x{seed:04X} ({seed})")
                    return seed
            except Exception as e:
                print(f"  ✗ Fehler beim Parsen: {e}")
        
        print(f"  ✗ Kein gültiger SEED erhalten")
        return None
    
    def send_key_response(self, level, response_value):
        """
        Sendet die berechnete Response zurück zur ECU
        Service: 0x27 (Security Access)
        Level: gerade Zahl (0x02, 0x04, 0x06, etc.) = Send Key
        """
        cmd = f"27{level:02X}{response_value:04X}"
        print(f"  -> Send Key (Level 0x{level:02X}): {cmd}")
        response = self.send_command(cmd)
        print(f"  <- Response: {response}")
        
        # Erfolgreiche Antwort: 67 <level>
        # Fehlgeschlagene Antwort: 7F 27 XX (Negative Response)
        if response and '67' in response:
            print(f"  ✓ Security Access erfolgreich!")
            return True
        else:
            print(f"  ✗ Security Access fehlgeschlagen")
            return False
    
    def calculate_response(self, seed, key):
        """Berechnet die Response nach dem bekannten Algorithmus"""
        response = (seed * key) & 0xFFFF
        return response
    
    def test_all_keys(self):
        """Testet alle gefundenen Keys"""
        print("\n=== Teste alle gefundenen Keys ===")
        print("Hinweis: Diese Funktion fordert wiederholt SEEDs von der ECU an.")
        print("Manche ECUs haben eine Verzögerung nach fehlgeschlagenen Versuchen.\n")
        
        successful_keys = []
        
        for key_name, (key_value, level_indicator) in self.keys.items():
            print(f"\n--- Test Key: {key_name} ---")
            
            # Request Level: level_indicator sollte ungerade sein für Request
            # Wenn level_indicator gerade ist, mache es ungerade (Request)
            request_level = level_indicator if (level_indicator % 2 == 1) else (level_indicator - 1)
            if request_level == 0:
                request_level = 0x01
            
            # Response Level: immer Request Level + 1
            response_level = request_level + 1
            
            seed = self.request_seed(request_level)
            if seed is None:
                print(f"  ⚠ Überspringe {key_name} - kein SEED erhalten")
                continue
            
            # Berechne Response
            response_value = self.calculate_response(seed, key_value)
            print(f"  Berechnung: 0x{seed:04X} * 0x{key_value:04X} = 0x{response_value:04X}")
            
            # Sende Response
            success = self.send_key_response(response_level, response_value)
            if success:
                successful_keys.append((key_name, key_value, level_indicator))
            
            time.sleep(1)  # Kurze Pause zwischen Versuchen
        
        # Zusammenfassung
        print("\n" + "="*60)
        print("=== ZUSAMMENFASSUNG ===")
        print("="*60)
        if successful_keys:
            print(f"\n✓ Erfolgreiche Keys gefunden: {len(successful_keys)}\n")
            for key_name, key_value, level in successful_keys:
                print(f"  • {key_name}")
                print(f"    Key: 0x{key_value:04X}")
                print(f"    Level: 0x{level:02X}")
                print()
        else:
            print("\n✗ Keine erfolgreichen Keys gefunden")
            print("\nMögliche Ursachen:")
            print("  - Falsche Port-Konfiguration")
            print("  - ECU verwendet andere Keys")
            print("  - Interface nicht kompatibel")
            print("  - ECU ist gesperrt nach zu vielen Fehlversuchen")

def main():
    print("="*60)
    print("  ECU Security Access Tester")
    print("  Husqvarna 701 Enduro (2016)")
    print("="*60)
    
    # Konfiguration
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = '/dev/tty.usbserial'  # Ändere dies zu deinem Port
        print(f"\nHinweis: Verwendung von Standard-Port: {port}")
        print(f"Verwende: {sys.argv[0]} <port> um einen anderen Port zu verwenden\n")
    
    tester = ECUTester(port=port)
    
    # Test im Dummy-Modus (ohne Hardware)
    if '--dummy' in sys.argv:
        print("\n=== DUMMY MODUS (keine Hardware) ===")
        print("\nGefundene Keys:")
        for key_name, (key_value, level) in tester.keys.items():
            print(f"  {key_name}: 0x{key_value:04X} (Level 0x{level:02X})")
        
        print("\nTest-Berechnung mit SEED 0x1234:")
        for key_name, (key_value, level) in tester.keys.items():
            response = tester.calculate_response(0x1234, key_value)
            print(f"  {key_name}: SEED 0x1234 -> Response 0x{response:04X}")
        return
    
    # Echte Hardware-Tests
    if not tester.connect():
        print("\n✗ Verbindung fehlgeschlagen")
        print(f"\nVerfügbare Ports testen mit: python3 -m serial.tools.list_ports")
        sys.exit(1)
    
    try:
        tester.init_elm327()
        tester.read_ecu_info()
        tester.test_all_keys()
    except KeyboardInterrupt:
        print("\n\n⚠ Test durch Benutzer abgebrochen")
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if tester.ser:
            tester.ser.close()
            print("\n✓ Verbindung geschlossen")

if __name__ == '__main__':
    main()
