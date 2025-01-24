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
    'gambero-rosso': {
        'url': 'https://guidatv.org/canali/gambero-rosso-hd',
        'name': 'Gambero Rosso',
        'id': 'gambero-rosso',
        'epgName': 'Gambero Rosso',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8',
        'next_day_url': True  # Specifica che supporta il link con /domani
    }
}

# Funzione per costruire il link del giorno successivo
def costruisci_url(canale_info, giorno_successivo):
    if giorno_successivo and canale_info.get('next_day_url'):
        # Aggiunge /domani all'URL principale
        return f"{canale_info['url']}/domani"
    return canale_info['url']

# Funzione per fare lo scraping dei dati EPG da un singolo canale
def scrape_epg(url, canale_info, giorno_successivo=False):
    # Ottieni la data odierna o quella del giorno successivo
    data_odierna = datetime.datetime.now()
    if giorno_successivo:
        data_odierna += datetime.timedelta(days=1)
    data_odierna_str = data_odierna.strftime("%Y-%m-%d")

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

    for i, programma in enumerate(programmi):
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"

        descrizione = programma.find('p', class_='program-description text-break mt-2')
        descrizione = descrizione.get_text(strip=True) if descrizione else "Descrizione non disponibile"

        orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else None

        if not orario_inizio:
            continue

        # Sottrarre un'ora all'orario di inizio
        orario_inizio = (datetime.datetime.strptime(orario_inizio, "%H:%M") - datetime.timedelta(hours=1)).strftime("%H:%M")

        poster_img = programma.find('img')
        if poster_img:
            src = poster_img['src']
            poster_url = f"https://guidatv.org{src}" if src.startswith('/_next/image') else src
        else:
            poster_url = None

        # Calcola l'orario di fine basandoti sull'inizio del prossimo programma
        if orario_inizio_precedente:
            dati_programmi[-1]['end'] = f"{data_odierna_str}T{orario_inizio}:00.000000Z"

        # Crea l'oggetto per il programma corrente
        programma_data = {
            'start': f"{data_odierna_str}T{orario_inizio}:00.000000Z",
            'end': "Ora non disponibile",  # Lo calcoleremo con il prossimo programma
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': poster_url,
            'channel': canale_info['id']
        }

        dati_programmi.append(programma_data)
        orario_inizio_precedente = orario_inizio

    if dati_programmi:
        ultimo_programma = dati_programmi[-1]
        try:
            orario_inizio_ultimo = datetime.datetime.strptime(ultimo_programma['start'].split("T")[1][:5], "%H:%M")
            orario_fine_ultimo = orario_inizio_ultimo - datetime.timedelta(hours=1)
            ultimo_programma['end'] = orario_fine_ultimo.strftime(f"{data_odierna_str}T%H:%M:%S.000000Z")
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

# Funzione principale che esegue lo scraping da tutti i canali e salva i dati
def main():
    print("Inizio scraping dei dati EPG da più canali...")

    tutti_dati_canali = []

    for canale_id, canale_info in canali_urls.items():
        print(f"Raccogliendo dati per il canale {canale_info['name']}...")

        # URL per il giorno corrente
        url_corrente = costruisci_url(canale_info, giorno_successivo=False)
        dati_oggi = scrape_epg(url_corrente, canale_info, giorno_successivo=False)

        # URL per il giorno successivo
        url_domani = costruisci_url(canale_info, giorno_successivo=True)
        dati_domani = scrape_epg(url_domani, canale_info, giorno_successivo=True)

        if dati_oggi:
            tutti_dati_canali.append(dati_oggi)
        if dati_domani:
            tutti_dati_canali.append(dati_domani)

    if tutti_dati_canali:
        salva_dati(tutti_dati_canali)
        print("Dati salvati nel file dati_programmi.json.")
    else:
        print("Nessun dato trovato.")

if __name__ == "__main__":
    main()
