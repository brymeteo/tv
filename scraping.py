import requests
from bs4 import BeautifulSoup
import json
import datetime
import re

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
    
    # Verifica che la richiesta sia stata eseguita con successo
    if response.status_code != 200:
        print(f"Errore nel recupero dei dati da {url}, codice di stato: {response.status_code}")
        return None
    
    # Usa BeautifulSoup per fare il parsing del contenuto HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Trova il contenitore principale che ha la classe 'container mt-2'
    container = soup.find('div', class_='container mt-2')
    
    # Se non troviamo il contenitore, interrompiamo l'esecuzione
    if not container:
        print(f"Nessun contenitore trovato per {url}")
        return None
    
    # Troviamo tutti i div con la classe 'row' che contengono i programmi
    programmi = container.find_all('div', class_='row')  # Ora cerchiamo la classe 'row'
    
    dati_programmi = []
    
    # Esegui un loop per raccogliere informazioni su ogni programma
    for programma in programmi:
        # Titolo del programma (h2 con class 'card-title')
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"
        
        # Descrizione del programma (p con class 'program-description text-break mt-2')
        descrizione = programma.find('p', class_='program-description text-break mt-2')
        descrizione = descrizione.get_text(strip=True) if descrizione else "Descrizione non disponibile"
        
        # Orario di inizio (h3 con class 'hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else "Ora non disponibile"
        
        # Se l'orario di inizio non è valido, salta questo programma
        if orario_inizio == "Ora non disponibile":
            continue
        
        # Orario di fine e durata
        orario_fine_str = programma.find('div', class_='d-flex align-items-center gap-3 flex-wrap text-light fs-6').find_all('span')[0].get_text(strip=True)
        durata_str = programma.find('div', class_='d-flex align-items-center gap-3 flex-wrap text-light fs-6').find_all('span')[1].get_text(strip=True)
        
        # Estrai l'orario di fine dal formato '07:15 - 07:30'
        orario_inizio_obj = datetime.datetime.strptime(orario_inizio, "%H:%M")
        orario_fine_obj = datetime.datetime.strptime(orario_fine_str, "%H:%M")
        
        # Estrai la durata in minuti (ad esempio "15 min" diventa 15)
        durata_minuti = int(re.search(r'(\d+)', durata_str).group(1))  # Usando regex per estrarre il numero
        
        # Calcola il nuovo orario di fine aggiungendo la durata
        orario_fine_obj = orario_inizio_obj + datetime.timedelta(minutes=durata_minuti)
        
        # Format della data di fine in stringa
        orario_fine = orario_fine_obj.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        
        # Poster immagine
        poster_url = programma.find('img')
        if poster_url:
            src = poster_url['src']
            # Se l'URL dell'immagine è relativo, aggiungi il prefisso
            if src.startswith('/_next/image'):
                poster_url = f'https://guidatv.org{src}'
            else:
                poster_url = src
        else:
            poster_url = None
        
       from datetime import datetime

# Ottieni la data corrente nel formato "YYYY-MM-DD"
data_corrente = datetime.now().strftime("%Y-%m-%d")

# Usa la data corrente per l'orario di inizio
programma_data = {
    'start': f"{data_corrente}T{orario_inizio}:00.000000Z",  # Usa la data corrente
    'end': orario_fine,
    'title': titolo,
    'description': descrizione,
    'category': "Categoria non disponibile",  # Aggiungere una categoria predefinita o modificarla
    'poster': poster_url,
    'channel': canale_info['id']
}

        
        # Aggiungiamo i dati alla lista, ma solo se non è già presente
        if programma_data not in dati_programmi:
            dati_programmi.append(programma_data)
    
    # Restituisci i dati per il canale con la lista dei programmi
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
