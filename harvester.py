import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from imap_tools import MailBox

# Ladataan salasanat
load_dotenv()

# Määritellään tallennuskansio C-asemalle
BASE_DIR = r"C:\Users\HP\Desktop\Kesko vastaus 3.2.2026"
EML_DIR = os.path.join(BASE_DIR, "Chronological_Logs")
ATTACHMENT_DIR = os.path.join(BASE_DIR, "Repair_Invoices")

# Luodaan kansiot, jos niitä ei vielä ole
for folder in [BASE_DIR, EML_DIR, ATTACHMENT_DIR]:
    os.makedirs(folder, exist_ok=True)

# Avainsanat, joita etsimme (Leave no stone unturned)
KEYWORDS = ["RZS-139", "WAUZZZ4M4JD052978", "kaupanpurku", "virhevastuu", 
            "reklamaatio", "hinaus", "pörhö", "norrlands", "audi center", "k-auto", "kesko"]

accounts = [
    {"nimi": "Fox In The Code", "email": os.getenv("EMAIL_1_ADDRESS"), "pw": os.getenv("EMAIL_1_PASSWORD"), "server": os.getenv("EMAIL_1_IMAP")},
    {"nimi": "Pareto Box", "email": os.getenv("EMAIL_2_ADDRESS"), "pw": os.getenv("EMAIL_2_PASSWORD"), "server": os.getenv("EMAIL_2_IMAP")}
]

def sanitize_filename(name):
    """Puhdistaa tiedostonimestä kielletyt merkit."""
    if not name:
        return "Nimetön"
    keepcharacters = (' ', '.', '_', '-')
    return "".join(c for c in str(name) if c.isalnum() or c in keepcharacters).rstrip()

def harvest_emails():
    print(f"[*] Aloitetaan syväharavointi. Tallennuspaikka: {BASE_DIR}")
    print(f"[*] Etsittävät avainsanat: {', '.join(KEYWORDS)}\n")
    
    # Avataan pääloki-CSV
    csv_path = os.path.join(BASE_DIR, "Master_Index.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(["Päivämäärä", "Tili", "Kansio", "Lähettäjä", "Vastaanottaja", "Aihe", "Liitteet", "EML-Tiedosto"])

        for tili in accounts:
            if not all([tili['email'], tili['pw'], tili['server']]):
                continue
            
            print(f"========================================")
            print(f"[+] Kirjaudutaan: {tili['email']}")
            try:
                with MailBox(tili['server']).login(tili['email'], tili['pw']) as mailbox:
                    # Käydään läpi kaikki kansiot
                    for folder in mailbox.folder.list():
                        mailbox.folder.set(folder.name)
                        print(f"  -> Tutkitaan kansiota: {folder.name}...")
                        
                        # Haetaan viestit ja puretaan data (bulk=True nopeuttaa hakuprosessia)
                        for msg in mailbox.fetch(bulk=True):
                            
                            # Etsitään osumia (Aihe, tekstiosa tai liitteiden nimet)
                            search_text = f"{msg.subject} {msg.text} {msg.html} {' '.join([att.filename for att in msg.attachments if att.filename])}".lower()
                            
                            if any(keyword.lower() in search_text for keyword in KEYWORDS):
                                
                                date_str = msg.date.strftime("%Y-%m-%d_%H-%M") if msg.date else "Tuntematon_Aika"
                                safe_subject = sanitize_filename(msg.subject)[:50]
                                eml_filename = f"{date_str}_{tili['nimi'][:3]}_{safe_subject}.eml"
                                eml_filepath = os.path.join(EML_DIR, eml_filename)
                                
                                # Tallennetaan raaka .eml (oikeustoimikelpoinen metadata)
                                with open(eml_filepath, 'wb') as f:
                                    f.write(msg.obj.as_bytes())
                                
                                # Tallennetaan liitteet (Laskut, PDF:t)
                                attachment_names = []
                                for att in msg.attachments:
                                    if att.filename:
                                        att_filename = f"{date_str}_{sanitize_filename(att.filename)}"
                                        att_filepath = os.path.join(ATTACHMENT_DIR, att_filename)
                                        with open(att_filepath, 'wb') as f:
                                            f.write(att.payload)
                                        attachment_names.append(att.filename)
                                
                                # Kirjataan löydös Master Indexiin
                                writer.writerow([
                                    msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "",
                                    tili['email'],
                                    folder.name,
                                    msg.from_,
                                    ", ".join(msg.to),
                                    msg.subject,
                                    ", ".join(attachment_names),
                                    eml_filename
                                ])
                                print(f"      [LÖYTÖ!] {date_str} - {safe_subject}")

            except Exception as e:
                print(f"[-] Virhe tilin {tili['email']} kanssa: {e}")
                
    print(f"\n[OK] Haravointi valmis! Master Index ja todistusaineisto löytyvät kansiosta:\n{BASE_DIR}")

if __name__ == "__main__":
    harvest_emails()