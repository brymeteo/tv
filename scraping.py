import requests
from bs4 import BeautifulSoup
import json
import datetime

# Lista di URL dei canali TV da cui fare lo scraping
canali_urls = {
    'canale-5': {
        'url': 'https://www.superguidatv.it/programmazione-canale/oggi/guida-programmi-tv-canale-5/187/',
        'name': 'Canale 5',
        'id': 'canale-5',
        'epgName': 'Canale 5',
        'logo': 'https://api.superguidatv.it/v1/channels/187/logo?width=120&theme=light',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    }
    # Aggiungi altri canali qui
}

# Funzione per fare lo scraping dei dati EPG da un singolo canale
def scrape_epg(url, canale_info):
    # Ottieni la data odierna
    data_odierna = datetime.datetime.now().strftime("%Y-%m-%d")

    # Ottieni il contenuto della pagina
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Errore nel recupero dei dati da {url}, codice di stato: {response.status_code}")
        return None

    # Parsing HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    programmi_divs = soup.find_all('div', class_='sgtvchannelplan_divTableRow')
    dati_programmi = []

    for programma in programmi_divs:
        orario_inizio = programma.find('div', class_='sgtvchannelplan_hoursCell')
        if orario_inizio:
            orario_inizio = orario_inizio.get_text(strip=True)

        titolo = programma.find('span', class_='sgtvchannelplan_spanInfoNextSteps')
        if titolo:
            titolo = titolo.get_text(strip=True)

        # Link al dettaglio del programma
        dettaglio_link = programma.find('a', class_='sgtvchannelplan_aNextStep')
        if dettaglio_link:
            dettaglio_url = dettaglio_link['href']
        else:
            dettaglio_url = None

        # Estrai i dettagli del programma se il link esiste
        descrizione = None
        poster_url = None
        if dettaglio_url:
            # Accedi alla pagina del dettaglio del programma
            dettaglio_response = requests.get(dettaglio_url)
            if dettaglio_response.status_code == 200:
                dettaglio_soup = BeautifulSoup(dettaglio_response.content, 'html.parser')
                # Estrai descrizione
                descrizione_div = dettaglio_soup.find('div', class_='sgtvdetails_divContentText')
                if descrizione_div:
                    descrizione = descrizione_div.get_text(strip=True)

                # Estrai immagine del poster
                poster_div = dettaglio_soup.find('div', class_='sgtvdetails_divImagebackdropContainer')
                if poster_div:
                    poster_img = poster_div.find('img')
                    if poster_img:
                        poster_url = poster_img['src']

        # Crea l'oggetto del programma
        programma_data = {
            'start': f"{data_odierna}T{orario_inizio}:00.000000Z" if orario_inizio else "Ora non disponibile",
            'end': "Ora non disponibile",  # Si potrebbe calcolare con un programma successivo
            'title': titolo if titolo else "Titolo non disponibile",
            'description': descrizione if descrizione else "Descrizione non disponibile",
            'category': "Categoria non disponibile",  # Questa parte sarebbe da migliorare se possibile
            'poster': poster_url if poster_url else None,
            'channel': canale_info['id']
        }

        dati_programmi.append(programma_data)

    return {
        'id': canale_info['id'],
        'name': canale_info['name'],
        'epgName': canale_info['epgName'],
        'logo': canale_info['logo'],
        'm3uLink': canale_info['m3uLink'],
        'programs': dati_programmi
    }

# Funzione per salvare i dati in un file JSON
def salva_dati(dati_canali):
    with open('dati_programmi.json', 'w', encoding='utf-8') as json_file:
        json.dump(dati_canali, json_file, ensure_ascii=False, indent=4)

# Funzione principale che esegue lo scraping da tutti i canali e salva i dati
def main():
    print("Inizio scraping dei dati EPG da più canali...")

    # Lista per raccogliere i dati da tutti i canali
    tutti_dati_canali = []

    # Itera su ogni URL della lista dei canali
    for canale_id, canale_info in canali_urls.items():
        print(f"Raccogliendo dati da {canale_info['name']}...")

        # Esegui lo scraping dei dati per il canale corrente
        dati_canale = scrape_epg(canale_info['url'], canale_info)

        if dati_canale:
            tutti_dati_canali.append(dati_canale)
        else:
            print(f"Nessun dato trovato per il canale {canale_info['name']}.")

    # Se abbiamo dei dati, salvali nel file JSON
    if tutti_dati_canali:
        salva_dati(tutti_dati_canali)
        print("Dati salvati correttamente nel file dati_programmi.json.")
    else:
        print("Nessun dato trovato o errore durante lo scraping.")

if __name__ == "__main__":
    main()
