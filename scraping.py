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
        'zam_url': 'https://tv.zam.it/ch-Rai-1',
        'name': 'Rai 1',
        'id': 'rai-1',
        'epgName': 'Rai 1',
        'logo': 'https://api.superguidatv.it/v1/channels/123/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-1/stream.m3u8'
    },
    'canale-5': {
        'url': 'https://guidatv.org/canali/canale-5',
        'zam_url': 'https://tv.zam.it/ch-Canale-5',
        'name': 'Canale 5',
        'id': 'canale-5',
        'epgName': 'Canale 5',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    }
}

def scrape_descriptions(zam_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(zam_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Errore nel recupero delle descrizioni da {zam_url}, codice di stato: {response.status_code}")
        return []

    # Parsing del contenuto HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Trova tutti i programmi con i dettagli
    program_blocks = soup.find_all('div', class_='gen dataz')
    descriptions = []

    for block in program_blocks:
        # Estrai il titolo
        titolo_tag = block.find('a', class_='gen')
        titolo = titolo_tag.get('title') if titolo_tag else "Titolo non disponibile"

        # Estrai l'orario di inizio
        orario_tag = block.find_previous('div', class_='dataz gen')
        orario = orario_tag.find('b').get_text(strip=True) if orario_tag else None

        # Estrai la descrizione (se presente)
        descrizione_tag = block.find('span', class_='gen categoria')
        descrizione = descrizione_tag.get_text(strip=True) if descrizione_tag else "Descrizione non disponibile"

        descriptions.append({
            'title': titolo,
            'start_time': orario,
            'description': descrizione
        })

    return descriptions



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

    # Ottieni le descrizioni da tv.zam.it se applicabile
    zam_descriptions = scrape_descriptions(canale_info.get('zam_url')) if 'zam_url' in canale_info else []

    # Sincronizza le descrizioni con i programmi in base all'orario di inizio
    descrizioni_sincronizzate = []
    for programma in programmi:
        # Estrai i dettagli del programma da guidatv.org
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"

        orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else None

        if not orario_inizio:
            continue

        # Sottrarre un'ora all'orario di inizio
        orario_inizio = (datetime.datetime.strptime(orario_inizio, "%H:%M") - datetime.timedelta(hours=1)).strftime("%H:%M")

        # Trova l'URL del poster
        poster_img = programma.find('img')
        if poster_img:
            src = poster_img['src']
            poster_url = f"https://guidatv.org{src}" if src.startswith('/_next/image') else src
        else:
            poster_url = None

        # Associa la descrizione corretta
        descrizione = "Descrizione non disponibile"
        for zam_description in zam_descriptions:
            if zam_description['title'] == titolo and zam_description['start_time'] == orario_inizio:
                descrizione = zam_description['description']
                break

        programma_data = {
            'start': f"{data_odierna}T{orario_inizio}:00.000000Z",
            'end': "Ora non disponibile",  # Lo calcoleremo con il prossimo programma
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': poster_url,
            'channel': canale_info['id']
        }

        descrizioni_sincronizzate.append(programma_data)
    
    # Sincronizzazione finale dell'orario di fine
    for i, programma in enumerate(descrizioni_sincronizzate[:-1]):
        programma['end'] = descrizioni_sincronizzate[i+1]['start']

    if descrizioni_sincronizzate:
        ultimo_programma = descrizioni_sincronizzate[-1]
        try:
            orario_inizio_ultimo = datetime.datetime.strptime(ultimo_programma['start'].split("T")[1][:5], "%H:%M")
            orario_fine_ultimo = orario_inizio_ultimo - datetime.timedelta(hours=1)
            ultimo_programma['end'] = orario_fine_ultimo.strftime(f"{data_odierna}T%H:%M:%S.000000Z")
        except ValueError:
            ultimo_programma['end'] = "Ora non disponibile"

    return {
        'id': canale_info['id'],
        'name': canale_info['name'],
        'epgName': canale_info['epgName'],
        'logo': canale_info['logo'],
        'm3uLink': canale_info['m3uLink'],
        'programs': descrizioni_sincronizzate
    }




# Funzione per salvare i dati in un file JSON
def salva_dati(dati_canali):
    with open('dati_programmi.json', 'w', encoding='utf-8') as json_file:
        json.dump(dati_canali, json_file, ensure_ascii=False, indent=4)

# Funzione principale che esegue lo scraping da tutti i canali e salva i datii
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
