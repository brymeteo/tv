import requests
from bs4 import BeautifulSoup
import json
import datetime

# Lista dei canali e delle loro informazioni
canali_urls = {
    'rai-1': {
        'url': 'https://guidatv.org/canali/rai-1',
        'name': 'Rai 1',
        'id': 'rai-1',
        'epgName': 'Rai 1',
        'logo': 'https://api.superguidatv.it/v1/channels/123/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-1/stream.m3u8',
        'tvepgUrl': 'https://tvepg.eu/it/italy/channel/rai_uno'
    }
    # Puoi aggiungere altri canali qui...
}

# Funzione per estrarre descrizione dal sito tvepg.eu
def get_program_description(tvepg_url, program_link):
    try:
        response = requests.get(tvepg_url + program_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            description_tag = soup.find('div', class_='description-text')
            if description_tag:
                return description_tag.get_text(strip=True)
        print(f"Descrizione non trovata per {tvepg_url + program_link}")
    except Exception as e:
        print(f"Errore nel recuperare la descrizione: {e}")
    return "Descrizione non disponibile"

# Funzione per estrarre dati da guidatv.org
def scrape_epg(url, canale_info):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Errore nel recupero dei dati da {url}, codice di stato: {response.status_code}")
            return None

        # Parsing HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.find('div', class_='container mt-2')
        if not container:
            print(f"Nessun contenitore trovato per {url}")
            return None

        programmi = container.find_all('div', class_='row')
        dati_programmi = []

        # Ottieni data odierna
        data_odierna = datetime.datetime.now().strftime("%Y-%m-%d")

        for programma in programmi:
            # Estrai i dati principali
            titolo = programma.find('h2', class_='card-title')
            titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"

            orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
            orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else None

            if not orario_inizio:
                continue

            # Converti l'orario di inizio
            orario_inizio = (datetime.datetime.strptime(orario_inizio, "%H:%M") - datetime.timedelta(hours=1)).strftime("%H:%M")

            # Link al programma per descrizione
            program_link = programma.find('a', href=True)
            program_link = program_link['href'] if program_link else None

            # Poster del programma
            poster_img = programma.find('img')
            poster_url = f"https://guidatv.org{poster_img['src']}" if poster_img and 'src' in poster_img.attrs else None

            # Recupera descrizione da tvepg.eu
            descrizione = get_program_description(canale_info['tvepgUrl'], program_link) if program_link else "Descrizione non disponibile"

            # Aggiungi il programma ai dati
            programma_data = {
                'start': f"{data_odierna}T{orario_inizio}:00.000000Z",
                'title': titolo,
                'description': descrizione,
                'poster': poster_url,
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
    except Exception as e:
        print(f"Errore nello scraping di {url}: {e}")
        return None

# Funzione per salvare i dati in un file JSON
def salva_dati(dati_canali):
    with open('dati_programmi.json', 'w', encoding='utf-8') as json_file:
        json.dump(dati_canali, json_file, ensure_ascii=False, indent=4)

# Funzione principale per eseguire lo scraping
def main():
    print("Inizio scraping dei dati EPG da più canali...")

    # Lista dei dati raccolti
    tutti_dati_canali = []

    for canale_id, canale_info in canali_urls.items():
        print(f"Raccogliendo dati da {canale_info['name']}...")
        dati_canale = scrape_epg(canale_info['url'], canale_info)
        if dati_canale:
            tutti_dati_canali.append(dati_canale)

    if tutti_dati_canali:
        salva_dati(tutti_dati_canali)
        print("Dati salvati correttamente in dati_programmi.json.")
    else:
        print("Errore: nessun dato disponibile.")

if __name__ == "__main__":
    main()
