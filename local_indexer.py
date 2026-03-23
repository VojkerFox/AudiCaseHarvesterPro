import os
import csv
from datetime import datetime

# Määritellään tutkittavat kansiot
TARGET_DIRS = [
    r"C:\Users\HP\Desktop\Kesko vastaus 3.2.2026",
    r"C:\Users\HP\Desktop\K-Auto ja 12.3.2026 tiedot"
]

# Tallennetaan uusi indeksi samaan paikkaan missä skriptiä ajetaan
OUTPUT_CSV = r"C:\Users\HP\Dev\AudiCaseHarvesterPro\Master_Index_Hakemistot.csv"

def format_timestamp(ts):
    """Muuttaa Unix-aikaleiman ihmiselle luettavaan muotoon."""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def index_local_files():
    print("[*] Aloitetaan paikallisten hakemistojen skannaus...")
    
    # Avataan CSV kirjoitustilassa
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        # Kirjoitetaan otsikkorivi
        writer.writerow(["Lähdekansio", "Tiedostonimi", "Tunniste", "Koko (KB)", "Luotu", "Muokattu", "Koko Tiedostopolku"])
        
        total_files = 0
        
        for directory in TARGET_DIRS:
            if not os.path.exists(directory):
                print(f"[-] VAROITUS: Kansiota ei löydy polusta:\n{directory}")
                continue
            
            print(f"[+] Skannataan hakemistoa: {directory}")
            
            # os.walk käy läpi kansion ja kaikki sen sisällä olevat alikansiot automaattisesti
            for root, _, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    try:
                        # Haetaan tiedoston koko ja aikaleimat
                        stat = os.stat(filepath)
                        size_kb = round(stat.st_size / 1024, 2)
                        created = format_timestamp(stat.st_ctime)
                        modified = format_timestamp(stat.st_mtime)
                        
                        # Erotetaan tiedostopääte (esim. .pdf, .eml)
                        _, ext = os.path.splitext(file)
                        
                        # Kirjoitetaan rivi CSV-tiedostoon
                        writer.writerow([
                            os.path.basename(directory), # Päähakemiston nimi
                            file,
                            ext.lower(),
                            size_kb,
                            created,
                            modified,
                            filepath
                        ])
                        total_files += 1
                        
                    except Exception as e:
                        print(f"  [-] Virhe tiedoston {file} kohdalla: {e}")
                        
    print(f"\n[OK] Skannaus valmis! Löydettiin {total_files} tiedostoa.")
    print(f"[OK] Uusi indeksi tallennettiin onnistuneesti: {OUTPUT_CSV}")

if __name__ == "__main__":
    index_local_files()