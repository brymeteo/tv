import argparse
import datetime
import requests
from bs4 import BeautifulSoup
import json

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
    },
    'gambero-rosso': {
        'url': 'https://guidatv.org/canali/gambero-rosso-hd',
        'name': 'Gambero Rosso',
        'id': 'gambero-rosso',
        'epgName': 'Gambero Rosso',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    }
    # Aggiungi altri canali qui
}

# Funzione per recuperare la data corretta in base all'argomento
def get_data_oggi_o_ieri():
    return datetime.datetime.now().strftime("%Y-%m-%d")

# Funzione per fare lo scraping dei dati EPG da un singolo canale
def scrape_epg(url, canale_info, data_odierna):
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
    ora_corrente = datetime.datetime.now()

    for i, programma in enumerate(programmi):
        # Estrai i dettagli del programma
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"

        descrizione = programma.find('p', class_='program-description text-break mt-2')
        descrizione = descrizione.get_text(strip=True) if descrizione else "Descrizione non disponibile"

        orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else None

        if not orario_inizio:
            continue

        # Combina la data odierna con l'orario di inizio
        orario_inizio_completo = f"{data_odierna}T{orario_inizio}:00.000000Z"

        # Se il programma è in corso, adatta l'orario di inizio all'ora corrente
        orario_inizio_dt = datetime.datetime.strptime(orario_inizio_completo, "%Y-%m-%dT%H:%M:%S.%fZ")
        if ora_corrente >= orario_inizio_dt:
            # Se il programma è già in corso, inizia dall'ora corrente
            orario_inizio_completo = ora_corrente.strftime("%Y-%m-%dT%H:%M:%S.000000Z")

        # Trova l'URL del poster
        poster_img = programma.find('img')
        if poster_img:
            src = poster_img['src']
            poster_url = f"https://guidatv.org{src}" if src.startswith('/_next/image') else src
        else:
            poster_url = None

        # Calcola l'orario di fine basandoti sull'inizio del prossimo programma
        if orario_inizio_precedente:
            dati_programmi[-1]['end'] = (datetime.datetime.strptime(f"{data_odierna}T{orario_inizio}:00.000000Z", "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Crea l'oggetto per il programma corrente
        programma_data = {
            'start': orario_inizio_completo,
            'end': "Ora non disponibile",  # Lo calcoleremo con il prossimo programma
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': poster_url,
            'channel': canale_info['id']
        }

        dati_programmi.append(programma_data)
        orario_inizio_precedente = orario_inizio

    # Per l'ultimo programma, ipotizza una durata di 1 ora e aumenta l'orario di fine di un'ora se non ci sono altri programmi
    if dati_programmi:
        ultimo_programma = dati_programmi[-1]
        try:
            orario_inizio_ultimo = datetime.datetime.strptime(ultimo_programma['start'].split("T")[1][:5], "%H:%M")
            orario_fine_ultimo = orario_inizio_ultimo + datetime.timedelta(hours=1)  # Aggiungi 1 ora all'orario di inizio

            # Sottrai un'ora dall'orario di fine
            orario_fine_ultimo = orario_fine_ultimo - datetime.timedelta(hours=1)

            # Se l'orario di fine è successivo alla mezzanotte, aggiorniamo la data
            if orario_fine_ultimo.day != orario_inizio_ultimo.day:  
                # Incrementiamo la data di un giorno
                data_fine = (orario_inizio_ultimo + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                data_fine = data_odierna  # Se non cambia giorno, manteniamo la data odierna

            # Impostiamo l'orario di fine
            ultimo_programma['end'] = orario_fine_ultimo.strftime(f"{data_fine}T%H:%M:%S.000000Z")
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
    # Determina la data corretta in base all'argomento
    data_odierna = get_data_oggi_o_ieri()

    # Iniziamo a raccogliere i dati di tutti i canali
    dati_canali = []
    for canale_id, canale_info in canali_urls.items():
        url_da_scrapare = canale_info['url']  # URL costante per tutti i canali
        # Scraping per il canale con l'URL appropriato
        dati_canale = scrape_epg(url_da_scrapare, canale_info, data_odierna)
        if dati_canale:
            dati_canali.append(dati_canale)

    # Salva i dati in un file JSON
    salva_dati(dati_canali)

# Avvia lo script
if __name__ == "__main__":
    main()
