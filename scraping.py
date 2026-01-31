import argparse
import datetime
import requests
from bs4 import BeautifulSoup
import json

# Lista di URL dei canali TVs da cui fare lo scraping
canali_urls = {
    'rai-1': {
        'url': 'https://guidatv.org/canali/rai-1',
        'name': 'Rai 1',
        'id': 'rai-1',
        'epgName': 'Rai 1',
        'logo': 'https://api.superguidatv.it/v1/channels/123/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-1/stream.m3u8'
    },
    'rai-2': {
        'url': 'https://guidatv.org/canali/rai-2',
        'name': 'Rai 2',
        'id': 'rai-2',
        'epgName': 'Rai 2',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'rai-3': {
        'url': 'https://guidatv.org/canali/rai-3',
        'name': 'Rai 3',
        'id': 'rai-3',
        'epgName': 'Rai 3',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'rete-4': {
        'url': 'https://guidatv.org/canali/rete4',
        'name': 'Rete 4',
        'id': 'rete-4',
        'epgName': 'Rete 4',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'canale-5': {
        'url': 'https://guidatv.org/canali/canale-5',
        'name': 'Canale 5',
        'id': 'canale-5',
        'epgName': 'Canale 5',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'italia-1': {
        'url': 'https://guidatv.org/canali/italia-uno',
        'name': 'Italia 1',
        'id': 'italia-1',
        'epgName': 'Italia 1',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'la7': {
        'url': 'https://guidatv.org/canali/la7',
        'name': 'La7',
        'id': 'la7',
        'epgName': 'La7',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'tv8': {
        'url': 'https://guidatv.org/canali/tv8',
        'name': 'Tv8',
        'id': 'Tv8',
        'epgName': 'Tv8',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'nove': {
        'url': 'https://guidatv.org/canali/nove',
        'name': 'Nove',
        'id': 'nove',
        'epgName': 'Nove',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    '20-mediaset': {
        'url': 'https://guidatv.org/canali/canale-20',
        'name': '20 Mediaset',
        'id': '20-mediaset',
        'epgName': '20 Mediaset',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rai-4': {
        'url': 'https://guidatv.org/canali/rai-4',
        'name': 'Rai 4',
        'id': 'rai-4',
        'epgName': 'Rai 4',
        'logo': 'https://api.superguidatv.it/v1/channels/321/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rai-premium': {
        'url': 'https://guidatv.org/canali/rai-premium',
        'name': 'Rai Premium',
        'id': 'rai-premium',
        'epgName': 'Rai Premium',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'mediaset-27': {
        'url': 'https://guidatv.org/canali/mediaset-27',
        'name': 'Mediaset 27',
        'id': 'mediaset-27',
        'epgName': 'Mediaset 27',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'la-5': {
        'url': 'https://guidatv.org/canali/la-5',
        'name': 'La 5',
        'id': 'la-5',
        'epgName': 'La 5',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'real-time': {
        'url': 'https://guidatv.org/canali/real-time',
        'name': 'Real Time',
        'id': 'real-time',
        'epgName': 'Real Time',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'la7-cinema': {
        'url': 'https://guidatv.org/canali/la7-cinema',
        'name': 'La7-cinema',
        'id': 'la7-cinema',
        'epgName': 'La7-cinema',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2Fla7cinema.png&w=128&q=100',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'mediaset-extra': {
        'url': 'https://guidatv.org/canali/mediaset-extra',
        'name': 'Mediaset Extra',
        'id': 'mediaset-extra',
        'epgName': 'Mediaset Extra',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'topcrime': {
        'url': 'https://guidatv.org/canali/topcrime',
        'name': 'Top Crime',
        'id': 'topcrime',
        'epgName': 'Top Crime',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'discovery': {
        'url': 'https://guidatv.org/canali/discovery',
        'name': 'Discovery',
        'id': 'discovery',
        'epgName': 'Discovery',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2Fdiscovery.png&w=128&q=100',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'dmax': {
        'url': 'https://guidatv.org/canali/dmax',
        'name': 'Dmax',
        'id': 'dmax',
        'epgName': 'Dmax',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'mediaset-italia-due': {
        'url': 'https://guidatv.org/canali/mediaset-italia-due',
        'name': 'Mediaset Italia Due',
        'id': 'mediaset-italia-due',
        'epgName': 'Mediaset Italia Due',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'giallo': {
        'url': 'https://guidatv.org/canali/giallo',
        'name': 'Giallo',
        'id': 'giallo',
        'epgName': 'Giallo',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'cielo': {
        'url': 'https://guidatv.org/canali/cielo',
        'name': 'Cielo',
        'id': 'cielo',
        'epgName': 'Cielo',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'foodnetwork': {
        'url': 'https://guidatv.org/canali/foodnetwork',
        'name': 'Food Network',
        'id': 'foodnetwork',
        'epgName': 'Food Network',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'home-and-garden-tv': {
        'url': 'https://guidatv.org/canali/home-and-garden-tv',
        'name': 'Home And Garden Tv',
        'id': 'home-and-garden-tv',
        'epgName': 'Home And Garden Tv',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'tv2000': {
        'url': 'https://guidatv.org/canali/tv2000',
        'name': 'Tv 2000',
        'id': 'tv2000',
        'epgName': 'Tv 2000',
        'logo': 'https://api.superguidatv.it/v1/channels/218/logo?width=120&theme=dark',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/rai/rai-premium/stream.m3u8'
    },
    'gambero-rosso': {
        'url': 'https://guidatv.org/canali/gambero-rosso-hd',
        'name': 'Gambero Rosso',
        'id': 'gambero-rosso',
        'epgName': 'Gambero Rosso',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'history-channel': {
        'url': 'https://guidatv.org/canali/history-channel',
        'name': 'History Channel',
        'id': 'history-channel',
        'epgName': 'History Channel',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rsi-la1': {
        'url': 'https://guidatv.org/canali/rsi-la1',
        'name': 'RSI LA1',
        'id': 'rsi-la1',
        'epgName': 'RSI LA1',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rsi-la2': {
        'url': 'https://guidatv.org/canali/rsi-la2',
        'name': 'RSI LA2',
        'id': 'rsi-la2',
        'epgName': 'RSI LA2',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'sportitalia': {
        'url': 'https://guidatv.org/canali/sportitalia',
        'name': 'Sport Italia',
        'id': 'sportitalia',
        'epgName': 'Sport Italia',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'iris': {
        'url': 'https://guidatv.org/canali/iris',
        'name': 'Iris',
        'id': 'iris',
        'epgName': 'Iris',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'cine-34': {
        'url': 'https://guidatv.org/canali/cine-34',
        'name': 'Cine 34',
        'id': 'cine-34',
        'epgName': 'Cine 34',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rai-movie': {
        'url': 'https://guidatv.org/canali/rai-movie',
        'name': 'Rai movie',
        'id': 'rai-movie',
        'epgName': 'Rai movie',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'focus': {
        'url': 'https://guidatv.org/canali/focus',
        'name': 'Focus',
        'id': 'focus',
        'epgName': 'Focus',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'motor-trend': {
        'url': 'https://guidatv.org/canali/motor-trend',
        'name': 'Motor Trend',
        'id': 'motor-trend',
        'epgName': 'Motor Trend',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'sky-tg24': {
        'url': 'https://guidatv.org/canali/sky-tg24',
        'name': 'Sky Tg24',
        'id': 'sky-tg24',
        'epgName': 'Sky Tg24',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'tgcom24': {
        'url': 'https://guidatv.org/canali/tgcom24',
        'name': 'Tgcom 24',
        'id': 'tgcom24',
        'epgName': 'Tgcom 24',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rai-news-24': {
        'url': 'https://guidatv.org/canali/rai-news-24',
        'name': 'Rai News 24',
        'id': 'rai-news-24',
        'epgName': 'Rai News 24',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'boing': {
        'url': 'https://guidatv.org/canali/boing',
        'name': 'Boing',
        'id': 'boing',
        'epgName': 'Boing',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'k2': {
        'url': 'https://guidatv.org/canali/k2',
        'name': 'K2',
        'id': 'k2',
        'epgName': 'K2',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rai-gulp': {
        'url': 'https://guidatv.org/canali/rai-gulp',
        'name': 'Rai Gulp',
        'id': 'rai-gulp',
        'epgName': 'Rai Gulp',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rai-yoyo': {
        'url': 'https://guidatv.org/canali/rai-yoyo',
        'name': 'Rai Yoyo',
        'id': 'rai-yoyo',
        'epgName': 'Rai Yoyo',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'frisbee': {
        'url': 'https://guidatv.org/canali/frisbee',
        'name': 'Frisbee',
        'id': 'frisbee',
        'epgName': 'Frisbee',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'cartoonito': {
        'url': 'https://guidatv.org/canali/cartoonito',
        'name': 'Cartoonito',
        'id': 'cartoonito',
        'epgName': 'Cartoonito',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'super': {
        'url': 'https://guidatv.org/canali/super!',
        'name': 'Super',
        'id': 'super',
        'epgName': 'Super',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'deejay-tv': {
        'url': 'https://guidatv.org/canali/deejay-tv',
        'name': 'Deejay Tv',
        'id': 'deejay-tv',
        'epgName': 'Deejay Tv',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'rtl-102.5-tv': {
        'url': 'https://guidatv.org/canali/rtl-102.5-tv',
        'name': 'Rtl 102.5',
        'id': 'rtl-102.5-tv',
        'epgName': 'Rtl 102.5',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'radioitaliatv': {
        'url': 'https://guidatv.org/canali/radioitaliatv',
        'name': 'Radio Italia',
        'id': 'radioitaliatv',
        'epgName': 'Radio Italia',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    },
    'radiofreccia': {
        'url': 'https://guidatv.org/canali/radiofreccia',
        'name': 'Radio Freccia',
        'id': 'radiofreccia',
        'epgName': 'Radio Freccia',
        'logo': 'https://guidatv.org/_next/image?url=https%3A%2F%2Fimg-guidatv.org%2Floghi%2Fb%2F%2F524.png&w=128&q=75',
        'm3uLink': 'http://tvit.leicaflorianrobert.dev/canale5/stream.m3u8'
    }
}

# Funzione per recuperare la data odierna
def get_data_oggi_o_ieri():
    return datetime.datetime.now().strftime("%Y-%m-%d")

# Funzione per fare lo scraping dei dati EPG da un singolo canale
def scrape_epg(url, canale_info, data_odierna):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    # Richiesta HTTP con gestione dei redirect e degli errori
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )
    except requests.exceptions.TooManyRedirects:
        print(f"❌ Troppi redirect, salto canale: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di rete per {url}: {e}")
        return None

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
    orario_inizio_precedente_dt = None

    for i, programma in enumerate(programmi):
        titolo_tag = programma.find('h2', class_='card-title')
        titolo = titolo_tag.get_text(strip=True) if titolo_tag else "Titolo non disponibile"

        descrizione_tag = programma.find('p', class_='program-description text-break mt-2')
        descrizione = descrizione_tag.get_text(strip=True) if descrizione_tag else "Descrizione non disponibile"

        orario_inizio_tag = programma.find('h3', class_='hour ms-3 ms-md-4 mt-3 title-timeline text-secondary')
        orario_inizio = orario_inizio_tag.get_text(strip=True) if orario_inizio_tag else None
        if not orario_inizio:
            continue

        # Combina data e orario e applica l'offset di 1 ora
        orario_inizio_completo = f"{data_odierna}T{orario_inizio}:00.000000Z"
        try:
            orario_inizio_dt = datetime.datetime.strptime(orario_inizio_completo, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.timedelta(hours=1)
        except Exception as e:
            print("Errore nel parsing dell'orario:", e)
            continue

        # Controllo rollover giorno
        if orario_inizio_precedente_dt is not None:
            current_start = orario_inizio_dt
            if current_start <= orario_inizio_precedente_dt:
                current_start += datetime.timedelta(days=1)
            dati_programmi[-1]['end'] = current_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            current_start = orario_inizio_dt

        start_str = current_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        poster_img = programma.find('img')
        if poster_img:
            src = poster_img.get('src')
            poster_url = f"https://guidatv.org{src}" if src.startswith('/_next/image') else src
        else:
            poster_url = None

        programma_data = {
            'start': start_str,
            'end': "Ora non disponibile",
            'title': titolo,
            'description': descrizione,
            'category': "Categoria non disponibile",
            'poster': poster_url,
            'channel': canale_info['id']
        }
        dati_programmi.append(programma_data)
        orario_inizio_precedente_dt = current_start

    # Imposta fine ultimo programma (1 ora di durata)
    if dati_programmi:
        ultimo_programma = dati_programmi[-1]
        try:
            orario_inizio_ultimo = datetime.datetime.strptime(ultimo_programma['start'], "%Y-%m-%dT%H:%M:%S.%fZ")
            orario_fine_ultimo = orario_inizio_ultimo + datetime.timedelta(hours=1)
            ultimo_programma['end'] = orario_fine_ultimo.strftime("%Y-%m-%dT%H:%M:%S.000000Z")
        except Exception as e:
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
    data_odierna = get_data_oggi_o_ieri()
    dati_canali = []
    for canale_id, canale_info in canali_urls.items():
        url_da_scrapare = canale_info['url']
        dati_canale = scrape_epg(url_da_scrapare, canale_info, data_odierna)
        if dati_canale:
            dati_canali.append(dati_canale)
    salva_dati(dati_canali)

if __name__ == "__main__":
    main()
