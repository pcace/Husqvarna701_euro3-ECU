#!/usr/bin/env python3
"""
ECU Security Key Brute Forcer
Brute-forcet 16-bit Security Keys für die Husqvarna 701 ECU

ACHTUNG: 
- Dies kann Stunden dauern (65536 Möglichkeiten)
- ECU könnte nach mehreren Fehlversuchen sperren
- Nur verwenden, wenn bekannte Keys nicht funktionieren!
"""

import serial
import time
import sys
from datetime import datetime, timedelta

class BruteForcer:
    def __init__(self, port, baudrate=38400):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
        # Statistiken
        self.attempts = 0
        self.start_time = None
        self.last_success_time = None
        
        # Smart Ranges - basierend auf bekannten Keihin Keys
        self.smart_ranges = [
            # BMW/Keihin Keys sind typisch im Bereich 0x1000-0x2000
            (0x1000, 0x2000, "Keihin typischer Bereich"),
            # Bereich um bekannte Keys
            (0x1900, 0x1A00, "Um BMW 0x1923"),
            (0x1B00, 0x1E00, "Um gefundene Keys 0x1B23, 0x1D23"),
            (0x6A00, 0x6B00, "Um Husqvarna 449 Key 0x6AD5"),
            # Rest des Keyspaces
            (0x2000, 0x6A00, "Mittlerer Bereich"),
            (0x6B00, 0xFFFF, "Oberer Bereich"),
            (0x0001, 0x1000, "Unterer Bereich"),
        ]
    
    def connect(self):
        """Verbindet mit dem Interface"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)
            print(f"✓ Verbunden mit {self.port}")
            return True
        except Exception as e:
            print(f"✗ Fehler: {e}")
            return False
    
    def send_command(self, cmd, timeout=1):
        """Sendet Befehl und wartet auf Response"""
        if self.ser is None:
            return None
        
        self.ser.write((cmd + '\r').encode())
        time.sleep(timeout)
        response = self.ser.read(1000).decode('utf-8', errors='ignore')
        return response.strip()
    
    def init_elm327(self):
        """Initialisiert ELM327"""
        commands = [
            'ATZ', 'ATE0', 'ATL0', 'ATSP5',
            'ATSH 12',  # BMW ECU Adresse
            'ATTR 0xF1',  # Tester Adresse
            'ATAT1'
        ]
        
        for cmd in commands:
            self.send_command(cmd)
    
    def request_seed(self, level=0x01):
        """Fordert SEED von ECU an"""
        response = self.send_command(f"27{level:02X}", timeout=0.5)
        
        if response and len(response) >= 10:
            try:
                hex_response = response.replace(' ', '').replace('>', '')
                if hex_response.startswith('67'):
                    seed = int(hex_response[4:8], 16)
                    return seed
            except:
                pass
        return None
    
    def test_key(self, seed, key, level=0x02):
        """Testet einen Key"""
        response_value = (seed * key) & 0xFFFF
        cmd = f"27{level:02X}{response_value:04X}"
        response = self.send_command(cmd, timeout=0.5)
        
        self.attempts += 1
        
        # Erfolg?
        if response and '67' in response:
            return True
        
        # ECU gesperrt? (Negative Response Code 0x37 = requiredTimeDelayNotExpired)
        if response and '7F2737' in response.replace(' ', ''):
            return 'LOCKED'
        
        return False
    
    def estimate_time(self, keys_remaining, keys_per_second):
        """Schätzt verbleibende Zeit"""
        if keys_per_second == 0:
            return "Unbekannt"
        
        seconds = keys_remaining / keys_per_second
        td = timedelta(seconds=int(seconds))
        return str(td)
    
    def brute_force_range(self, start, end, description=""):
        """Brute-forcet einen Bereich"""
        print(f"\n=== Teste Bereich: 0x{start:04X} - 0x{end:04X} {description} ===")
        
        range_size = end - start + 1
        range_start_time = datetime.now()
        range_attempts = 0
        
        for key in range(start, end + 1):
            # Request SEED
            seed = self.request_seed(0x01)
            if seed is None:
                print(f"\r⚠ Kein SEED erhalten bei Key 0x{key:04X} - Warte 5 Sekunden...")
                time.sleep(5)
                continue
            
            # Test Key
            result = self.test_key(seed, key, 0x02)
            range_attempts += 1
            
            if result == True:
                print(f"\n\n🎉 ✓ KEY GEFUNDEN! 🎉")
                print(f"Key: 0x{key:04X} ({key})")
                print(f"Nach {self.attempts} Versuchen")
                print(f"Zeit: {datetime.now() - self.start_time}")
                return key
            
            elif result == 'LOCKED':
                print(f"\n⚠ ECU gesperrt bei Key 0x{key:04X}")
                print(f"Warte 60 Sekunden...")
                time.sleep(60)
                continue
            
            # Progress
            if range_attempts % 10 == 0:
                elapsed = (datetime.now() - range_start_time).total_seconds()
                keys_per_sec = range_attempts / elapsed if elapsed > 0 else 0
                keys_remaining = range_size - range_attempts
                eta = self.estimate_time(keys_remaining, keys_per_sec)
                
                print(f"\r  Fortschritt: {range_attempts}/{range_size} "
                      f"({100*range_attempts/range_size:.1f}%) | "
                      f"Aktuell: 0x{key:04X} | "
                      f"Speed: {keys_per_sec:.1f} Keys/s | "
                      f"ETA: {eta}", end='', flush=True)
            
            # Kurze Pause um ECU nicht zu überlasten
            time.sleep(0.1)
        
        print(f"\n  ✗ Kein Key in diesem Bereich gefunden")
        return None
    
    def smart_brute_force(self):
        """Intelligenter Brute-Force mit priorisierten Bereichen"""
        print("\n" + "="*60)
        print("  SMART BRUTE FORCE")
        print("="*60)
        print("\nStrategie: Teste wahrscheinlichste Bereiche zuerst")
        print(f"Gesamter Keyspace: 65536 Keys (0x0000 - 0xFFFF)")
        
        self.start_time = datetime.now()
        
        for start, end, description in self.smart_ranges:
            key = self.brute_force_range(start, end, description)
            if key is not None:
                return key
        
        print("\n\n✗ Kein Key gefunden im gesamten Keyspace!")
        return None
    
    def simple_brute_force(self):
        """Einfacher linearer Brute-Force"""
        print("\n" + "="*60)
        print("  LINEARER BRUTE FORCE")
        print("="*60)
        print("\nWarnung: Dies kann sehr lange dauern!")
        
        self.start_time = datetime.now()
        return self.brute_force_range(0x0000, 0xFFFF, "Kompletter Keyspace")

def main():
    print("="*60)
    print("  ECU Security Key Brute Forcer")
    print("  Husqvarna 701 Enduro (2016)")
    print("="*60)
    print("\n⚠ WARNUNG ⚠")
    print("- Dies kann Stunden dauern")
    print("- ECU kann nach mehreren Fehlversuchen sperren")
    print("- Nur verwenden wenn bekannte Keys nicht funktionieren!")
    print("- Immer erst die gefundenen Keys testen!")
    
    answer = input("\nFortfahren? (yes/NO): ")
    if answer.lower() != 'yes':
        print("Abgebrochen.")
        return
    
    if len(sys.argv) < 2:
        print("\nUsage: python3 brute_force_keys.py <port> [--simple]")
        print("  --simple: Linearer Brute-Force (langsamer)")
        print("\nBeispiel: python3 brute_force_keys.py /dev/tty.usbserial")
        return
    
    port = sys.argv[1]
    simple_mode = '--simple' in sys.argv
    
    forcer = BruteForcer(port)
    
    if not forcer.connect():
        print("\n✗ Verbindung fehlgeschlagen")
        return
    
    try:
        forcer.init_elm327()
        
        if simple_mode:
            key = forcer.simple_brute_force()
        else:
            key = forcer.smart_brute_force()
        
        if key:
            print(f"\n\n{'='*60}")
            print(f"✓ ERFOLG!")
            print(f"{'='*60}")
            print(f"\nGefundener Key: 0x{key:04X} ({key})")
            print(f"Versuche: {forcer.attempts}")
            print(f"Zeit: {datetime.now() - forcer.start_time}")
            print(f"\nBitte dokumentiere dieses Ergebnis!")
    
    except KeyboardInterrupt:
        print("\n\n⚠ Abgebrochen durch Benutzer")
        print(f"Versuche bis jetzt: {forcer.attempts}")
        print(f"Zeit: {datetime.now() - forcer.start_time}")
    
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if forcer.ser:
            forcer.ser.close()
            print("\n✓ Verbindung geschlossen")

if __name__ == '__main__':
    main()
