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

    # Trova il blocco principale che contiene tutti i programmi
    main_content = soup.find('div', id='maincontent')
    if not main_content:
        print(f"Nessun contenuto trovato in {zam_url}")
        return []

    # Trova tutti i blocchi che contengono descrizioni alternando tra info_box_color e info_box
    description_blocks = main_content.find_all('div', class_=['info_box_color', 'info_box'])

    descriptions = []
    for block in description_blocks:
        # Cerca il div che contiene la descrizione effettiva
        description_div = block.find('div', class_='gen sx')
        if description_div:
            # Estrai il testo completo, compreso il contenuto HTML
            description_text = ''.join([str(element) for element in description_div.find_all(text=True, recursive=True)]).strip()

            # Rimuovi il link "Continua..." se presente
            description_text = description_text.replace('(Continua...)', '').strip()

            descriptions.append(description_text)

    if not descriptions:
        print("Nessuna descrizione trovata. Verifica la struttura HTML del sito.")
    return descriptions


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

    # Variabile per tenere traccia dell'orario di inizio del programma precedente
    orario_inizio_precedente = None

    # Ottieni le descrizioni da tv.zam.it se applicabile
    zam_descriptions = scrape_descriptions(canale_info.get('zam_url')) if 'zam_url' in canale_info else []

    for i, programma in enumerate(programmi):
        # Estrai i dettagli del programma
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"

        # Usa descrizione da tv.zam.it se disponibile, altrimenti da guidatv.org
        descrizione = zam_descriptions[i] if i < len(zam_descriptions) else "Descrizione non disponibile"

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

        # Calcola l'orario di fine basandoti sull'inizio del prossimo programma
        if orario_inizio_precedente:
            dati_programmi[-1]['end'] = f"{data_odierna}T{orario_inizio}:00.000000Z"

        # Crea l'oggetto per il programma corrente
        programma_data = {
            'start': f"{data_odierna}T{orario_inizio}:00.000000Z",
            'end': "Ora non disponibile",  # Lo calcoleremo con il prossimo programma
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': poster_url,
            'channel': canale_info['id']
        }

        dati_programmi.append(programma_data)
        orario_inizio_precedente = orario_inizio

    # Per l'ultimo programma, ipotizza una durata di 1 ora e sottrae un'ora
    if dati_programmi:
        ultimo_programma = dati_programmi[-1]
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
