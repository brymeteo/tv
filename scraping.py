import requests
from bs4 import BeautifulSoup
import json
import datetime

# Lista di URL dei canali TV da cui fare lo scraping
canali_urls = {
    'rai-premium': {
        'url': 'https://guidatv.org/canali/rai-premium',
        'name': 'Rai Premium',
        'id': 'rai-premium',
        'epgName': 'Rai Premium',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'rai-1': {
        'url': 'https://guidatv.org/canali/rai-1',
        'name': 'Rai 1',
        'id': 'rai-1',
        'epgName': 'Rai 1',
        'logo': 'https://api.superguidatv.it/v1/channels/123/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-1/stream.m3u8'
    },
    'canale-5': {
        'url': 'https://guidatv.org/canali/canale-5',
        'name': 'Canale 5',
        'id': 'canale-5',
        'epgName': 'Canale 5',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    }
    # Aggiungi altri canali qui
}

# Funzione per ottenere la descrizione dal sito tvepg.eu
def get_tvepg_description(program_url):
    base_url = 'https://tvepg.eu'
    url = base_url + program_url
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Errore nel recupero della pagina del programma: {url}")
        return None
    
    # Parsing della pagina HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    description_div = soup.find('div', class_='description-text')
    
    if description_div:
        description = description_div.get_text(strip=True)
        return description
    else:
        print(f"Descrizione non trovata per il programma: {url}")
        return "Descrizione non disponibile"

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
    container = soup.find('div', class_='container mt-2')
    if not container:
        print(f"Nessun contenitore trovato per {url}")
        return None

    programmi = container.find_all('div', class_='row')
    dati_programmi = []

    for programma in programmi:
        # Estrai i dettagli del programma
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"

        orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else None

        if not orario_inizio:
            continue

        # Costruisci l'URL della pagina di dettaglio su tvepg.eu
        link_programma = programma.find('a', href=True)
        if link_programma:
            program_url = link_programma['href']
            descrizione = get_tvepg_description(program_url)
        else:
            descrizione = "Descrizione non disponibile"

        # Aggiungi la descrizione al programma
        programma_data = {
            'start': f"{data_odierna}T{orario_inizio}:00.000000Z",
            'end': "Ora non disponibile",  # Lo calcoleremo con il prossimo programma
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': "URL del poster",  # Puoi estrarre il poster se è necessario
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
