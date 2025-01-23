def scrape_epg(url, canale_info):
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
        # Estrai i dettagli del programma
        titolo = programma.find('h2', class_='card-title')
        titolo = titolo.get_text(strip=True) if titolo else "Titolo non disponibile"
        
        descrizione = programma.find('p', class_='program-description text-break mt-2')
        descrizione = descrizione.get_text(strip=True) if descrizione else "Descrizione non disponibile"
        
        orario_inizio = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio.get_text(strip=True) if orario_inizio else None
        
        if not orario_inizio:
            continue
        
        # Calcola l'orario di fine basandoti sull'inizio del prossimo programma
        if orario_inizio_precedente:
            dati_programmi[-1]['end'] = f"2025-01-23T{orario_inizio}:00.000000Z"
        
        # Crea l'oggetto per il programma corrente
        programma_data = {
            'start': f"2025-01-23T{orario_inizio}:00.000000Z",
            'end': "Ora non disponibile",  # Lo calcoleremo con il prossimo programma
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': None,  # Implementa il poster se necessario
            'channel': canale_info['id']
        }
        
        dati_programmi.append(programma_data)
        orario_inizio_precedente = orario_inizio
    
    # Per l'ultimo programma, ipotizza una durata di 1 ora
    if dati_programmi:
        ultimo_programma = dati_programmi[-1]
        try:
            orario_inizio_ultimo = datetime.datetime.strptime(ultimo_programma['start'].split("T")[1][:5], "%H:%M")
            orario_fine_ultimo = orario_inizio_ultimo + datetime.timedelta(hours=1)
            ultimo_programma['end'] = orario_fine_ultimo.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
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
