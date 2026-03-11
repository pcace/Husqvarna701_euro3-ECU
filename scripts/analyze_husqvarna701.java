// Ghidra Script für Husqvarna 701 ECU Analyse
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
        println("\nSearching for references to key table...");
        Address[] refs = findBytes(keyTableAddr, 
            new byte[]{(byte)0x00, (byte)0x08, (byte)0x76, (byte)0x40},
            1000);
        
        for (Address ref : refs) {
            println("  Found reference at: " + ref);
            setEOLComment(ref, "REF to SecurityKeyTable");
        }
        
        // 4. Suche nach Service 0x27 Handlern
        println("\nSearching for Service 0x27 handlers...");
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
        
        println("\n=== Analysis Complete ===");
        println("Hint: Look for MULS/MULU instructions near Service 0x27 handlers");
    }
}
