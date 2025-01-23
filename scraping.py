import requests
from bs4 import BeautifulSoup
import json
import datetime

# Lista di URL dei canali TV da cui fare lo scraping
canali_urls = {
    'rai-premium': 'https://guidatv.org/canali/rai-premium',
    'rai-1': 'https://guidatv.org/canali/rai-1',
    'canale-5': 'https://guidatv.org/canali/canale-5',
    # Aggiungi altri canali qui
}

# Funzione per fare lo scraping dei dati EPG da un singolo canale
def scrape_epg(url):
    # Ottieni il contenuto della pagina
    response = requests.get(url)
    
    # Verifica che la richiesta sia stata eseguita con successo
    if response.status_code != 200:
        print(f"Errore nel recupero dei dati da {url}, codice di stato: {response.status_code}")
        return []
    
    # Usa BeautifulSoup per fare il parsing del contenuto HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Trova il contenitore principale che ha la classe 'container mt-2'
    container = soup.find('div', class_='container mt-2')
    
    # Se non troviamo il contenitore, interrompiamo l'esecuzione
    if not container:
        print(f"Nessun contenitore trovato per {url}")
        return []
    
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
            poster_url = "URL poster non disponibile"
        
        # Creiamo un dizionario con i dati del programma
        programma_data = {
            'titolo': titolo,
            'orario_inizio': orario_inizio,
            'descrizione': descrizione,
            'poster_url': poster_url,
            'canale': url,  # Aggiungi il nome del canale (o URL) ai dati
            'data': str(datetime.datetime.now())  # Data e ora di esecuzione
        }
        
        # Aggiungiamo i dati alla lista
        dati_programmi.append(programma_data)
    
    return dati_programmi

# Funzione per salvare i dati in un file JSON
def salva_dati(dati_programmi):
    with open('dati_programmi.json', 'w', encoding='utf-8') as json_file:
        json.dump(dati_programmi, json_file, ensure_ascii=False, indent=4)

# Funzione principale che esegue lo scraping da tutti i canali e salva i dati
def main():
    print("Inizio scraping dei dati EPG da più canali...")
    
    # Lista per raccogliere i dati da tutti i canali
    tutti_dati_programmi = []
    
    # Itera su ogni URL della lista dei canali
    for nome_canale, url in canali_urls.items():
        print(f"Raccogliendo dati da {nome_canale}...")
        
        # Esegui lo scraping dei dati per il canale corrente
        dati_canale = scrape_epg(url)
        
        if dati_canale:
            tutti_dati_programmi.extend(dati_canale)
        else:
            print(f"Nessun dato trovato per il canale {nome_canale}.")
    
    # Se abbiamo dei dati, salvali nel file JSON
    if tutti_dati_programmi:
        salva_dati(tutti_dati_programmi)
        print("Dati salvati correttamente nel file dati_programmi.json.")
    else:
        print("Nessun dato trovato o errore durante lo scraping.")

if __name__ == "__main__":
    main()
