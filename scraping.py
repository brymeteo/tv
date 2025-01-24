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
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8',
        'zam_url': 'https://tv.zam.it/ch-Rai-Premium'
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

def scrape_zam_details(zam_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(zam_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Errore nel recupero delle descrizioni da {zam_url}, codice di stato: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Trova il blocco principale che contiene tutti i programmi
    main_content = soup.find_all('div', class_='gen')

    program_details = []

    for block in main_content:
        # Estrazione orario
        orario_div = block.find('div', class_='dataz')
        if orario_div:
            orario = orario_div.find('b')
            orario_text = orario.get_text(strip=True) if orario else None
        else:
            orario_text = "Ora non disponibile"
        
        # Estrazione titolo
        titolo_div = block.find('div', class_='gen dataz')
        if titolo_div:
            titolo = titolo_div.find('a')
            titolo_text = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"
        else:
            titolo_text = "Titolo non disponibile"

        # Estrazione descrizione
        descrizione_div = block.find('div', style="padding:5px;")
        if descrizione_div:
            descrizione_text = descrizione_div.get_text(strip=True)
        else:
            descrizione_text = "Descrizione non disponibile"
        
        # Formattazione orario in formato ISO (se disponibile)
        try:
            if orario_text != "Ora non disponibile":
                start_time = datetime.datetime.strptime(orario_text, '%H:%M')
                formatted_start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
            else:
                formatted_start_time = "Ora non disponibile"
        except ValueError:
            formatted_start_time = "Ora non disponibile"

        program_details.append({
            'title': titolo_text,
            'description': descrizione_text,
            'start_time': formatted_start_time
        })
    
    return program_details


def scrape_guidatv_image(guidatv_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(guidatv_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Errore nel recupero dell'immagine da {guidatv_url}, codice di stato: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    # Trova il blocco dell'immagine del programma
    poster_img = soup.find('img', class_='poster')
    if poster_img:
        src = poster_img['src']
        poster_url = f"https://guidatv.org{src}" if src.startswith('/_next/image') else src
        return poster_url
    else:
        return None

def scrape_epg(canale_info):
    # Estrai i dettagli dal sito zam
    zam_program_details = scrape_zam_details(canale_info['zam_url'])

    # Estrai le immagini da guidatv
    guidatv_image = scrape_guidatv_image(canale_info['url'])

    # Sincronizza i dati in un formato finale
    programs = []
    for i, details in enumerate(zam_program_details):
        program_data = {
            'start': f"2025-01-24T{details['start_time']}:00.000000Z",
            'end': "Ora non disponibile",  # Placeholder, aggiornerai questo in seguito
            'title': details['title'],
            'description': details['description'],
            'category': "Categoria non disponibile",  # Placeholder per la categoria
            'poster': guidatv_image,
            'channel': canale_info['id']
        }
        programs.append(program_data)

    return {
        'id': canale_info['id'],
        'name': canale_info['name'],
        'epgName': canale_info['epgName'],
        'logo': canale_info['logo'],
        'm3uLink': canale_info['m3uLink'],
        'programs': programs
    }

def main():
    print("Inizio scraping dei dati EPG da più canali...")

    # Lista per raccogliere i dati da tutti i canali
    tutti_dati_canali = []

    # Itera su ogni URL della lista dei canali
    for canale_id, canale_info in canali_urls.items():
        print(f"Raccogliendo dati da {canale_info['name']}...")

        # Esegui lo scraping dei dati per il canale corrente
        dati_canale = scrape_epg(canale_info)

        if dati_canale:
            tutti_dati_canali.append(dati_canale)
        else:
            print(f"Nessun dato trovato per il canale {canale_info['name']}.")

    # Se abbiamo dei dati, salvali nel file JSON
    if tutti_dati_canali:
        with open('dati_programmi.json', 'w', encoding='utf-8') as json_file:
            json.dump(tutti_dati_canali, json_file, ensure_ascii=False, indent=4)
        print("Dati salvati correttamente nel file dati_programmi.json.")
    else:
        print("Nessun dato trovato o errore durante lo scraping.")

if __name__ == "__main__":
    main()
