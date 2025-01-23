import requests
from bs4 import BeautifulSoup
import json
import datetime

# Lista di URL dei canali TV da cui fare lo scraping
canali_urls = {
    'rai-premium': {'url': 'https://guidatv.org/canali/rai-premium', 'name': 'Rai Premium', 'id': 'rai-premium', 'epgName': 'Rai Premium', 'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark', 'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'},
    'rai-1': {'url': 'https://guidatv.org/canali/rai-1', 'name': 'Rai 1', 'id': 'rai-1', 'epgName': 'Rai 1', 'logo': 'https://api.superguidatv.it/v1/channels/123/logo?width=120&theme=dark', 'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-1/stream.m3u8'},
    'canale-5': {'url': 'https://guidatv.org/canali/canale-5', 'name': 'Canale 5', 'id': 'canale-5', 'epgName': 'Canale 5', 'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark', 'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'},
    # Aggiungi altri canali qui
}

# Funzione per fare lo scraping dei dati EPG da un singolo canale
def scrape_epg(url, canale_info):
    # Ottieni il contenuto della pagina
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Errore nel recupero dei dati da {url}, codice di stato: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find('div', class_='container mt-2')
    
    if not container:
        print(f"Nessun contenitore trovato per {url}")
        return None
    
    programmi = container.find_all('div', class_='row')
    dati_programmi = []
    
    for programma in programmi:
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"
        
        descrizione = programma.find('p', class_='program-description text-break mt-2')
        descrizione = descrizione.get_text(strip=True) if descrizione else "Descrizione non disponibile"
        
        # Orario di inizio e fine (esempio: '07:15 - 07:30')
        orario_span = programma.find('span')
        if orario_span:
            orario_testo = orario_span.get_text(strip=True)
            try:
                orario_inizio, orario_fine = orario_testo.split(' - ')
                orario_inizio_obj = datetime.datetime.strptime(orario_inizio, "%H:%M")
                orario_fine_obj = datetime.datetime.strptime(orario_fine, "%H:%M")
                
                orario_inizio = orario_inizio_obj.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
                orario_fine = orario_fine_obj.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
            except ValueError:
                orario_inizio = "Ora non disponibile"
                orario_fine = "Ora non disponibile"
        else:
            orario_inizio = "Ora non disponibile"
            orario_fine = "Ora non disponibile"
        
        poster_url = programma.find('img')
        if poster_url:
            src = poster_url['src']
            if src.startswith('/_next/image'):
                poster_url = f'https://guidatv.org{src}'
            else:
                poster_url = src
        else:
            poster_url = None
        
        programma_data = {
            'start': orario_inizio,
            'end': orario_fine,
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': poster_url,
            'channel': canale_info['id']
        }
        
        if programma_data not in dati_programmi:
            dati_programmi.append(programma_data)
    
    return {
        'id': canale_info['id'],
        'name': canale_info['name'],
        'epgName': canale_info['epgName'],
        'logo': canale_info['logo'],
        'm3uLink': canale_info['m3uLink'],
        'programs': dati_programmi
    }

def salva_dati(dati_canali):
    with open('dati_programmi.json', 'w', encoding='utf-8') as json_file:
        json.dump(dati_canali, json_file, ensure_ascii=False, indent=4)

def main():
    print("Inizio scraping dei dati EPG da più canali...")
    tutti_dati_canali = []
    
    for canale_id, canale_info in canali_urls.items():
        print(f"Raccogliendo dati da {canale_info['name']}...")
        dati_canale = scrape_epg(canale_info['url'], canale_info)
        
        if dati_canale:
            tutti_dati_canali.append(dati_canale)
        else:
            print(f"Nessun dato trovato per il canale {canale_info['name']}.")
    
    if tutti_dati_canali:
        salva_dati(tutti_dati_canali)
        print("Dati salvati correttamente nel file dati_programmi.json.")
    else:
        print("Nessun dato trovato o errore durante lo scraping.")

if __name__ == "__main__":
    main()
