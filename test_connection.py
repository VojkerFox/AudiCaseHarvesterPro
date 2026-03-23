import os
from dotenv import load_dotenv
from imap_tools import MailBox

# Ladataan .env -tiedoston salasanat ja tunnukset ohjelman käyttöön
load_dotenv()

# Rakennetaan lista tileistä, jotta ohjelma voi testata molemmat kerralla
accounts = [
    {
        "nimi": "Fox In The Code",
        "email": os.getenv("EMAIL_1_ADDRESS"),
        "salasana": os.getenv("EMAIL_1_PASSWORD"),
        "palvelin": os.getenv("EMAIL_1_IMAP")
    },
    {
        "nimi": "Pareto Box",
        "email": os.getenv("EMAIL_2_ADDRESS"),
        "salasana": os.getenv("EMAIL_2_PASSWORD"),
        "palvelin": os.getenv("EMAIL_2_IMAP")
    }
]

def testaa_yhteydet():
    print("Käynnistetään IMAP-tiedustelu...\n" + "="*40)

    for tili in accounts:
        print(f"[*] Yritetään yhdistää: {tili['nimi']} ({tili['email']})")
        
        # Varmistetaan, ettei .env -tiedostosta puutu tietoja
        if not all([tili['email'], tili['salasana'], tili['palvelin']]):
            print("[!] Virhe: Kaikkia tietoja ei löytynyt .env -tiedostosta tälle tilille.\n")
            continue

        try:
            # Otetaan yhteys ja kirjaudutaan sisään
            with MailBox(tili['palvelin']).login(tili['email'], tili['salasana']) as mailbox:
                print("[+] Yhteys onnistui! Kirjautuminen OK.")
                print("[*] Haetaan postilaatikon kansiorakenne...")
                
                # Listataan kaikki kansiot
                kansiot = mailbox.folder.list()
                for kansio in kansiot:
                    print(f"    - {kansio.name}")
            print("-" * 40)
            
        except Exception as e:
            print(f"[-] Yhteys EPÄONNISTUI! Virhekoodi:\n{e}\n" + "-" * 40)

if __name__ == "__main__":
    testaa_yhteydet()