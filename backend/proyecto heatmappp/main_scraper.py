import time
import json
import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
# Palabras clave para filtrar noticias relevantes a inseguridad
KEYWORDS = ["policiales", "robo", "asalto", "detenido", "cae", "crimen", "hurto", "asesinato", "fiscalia", "investigan", "motochorro"]

def es_noticia_relevante(url):
    """Verifica si el link contiene palabras relacionadas a delitos"""
    return any(word in url.lower() for word in KEYWORDS)

def extraer_cuerpo_noticia(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        titulo = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Sin título"
        parrafos = soup.find_all('p')
        texto_completo = " ".join([p.get_text(strip=True) for p in parrafos])
        return {"url": url, "titulo": titulo, "texto": texto_completo}
    except:
        return None

def obtener_links_abc():
    print("🔎 Buscando en ABC Color...")
    res = requests.get("https://www.abc.com.py/policiales/", headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = []
    
    for a in soup.find_all('a', href=True):
        raw_url = a['href'] # Primero capturamos el link del HTML
        
        # 1. Limpiamos el link (quitamos la parte de comentarios si existe)
        clean_url = raw_url.split('#')[0]
        
        # 2. Verificamos que sea de la sección policiales y tenga una longitud lógica
        if '/policiales/' in clean_url and len(clean_url) > 40:
            # 3. Formamos la URL completa si es relativa
            full_url = "https://www.abc.com.py" + clean_url if clean_url.startswith('/') else clean_url
            
            # 4. Evitamos duplicados en nuestra lista
            if full_url not in links:
                links.append(full_url)
    return links

def obtener_links_uh():
    print("🔎 Buscando en Última Hora...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.ultimahora.com/policiales")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    links = []
    for a in soup.find_all('a', href=True):
        url = a['href']
        # Aquí aplicamos el filtro de palabras clave para ÚH que es más desordenado
        if 'ultimahora.com/' in url and es_noticia_relevante(url) and len(url) > 40:
            if url not in links: links.append(url)
    return links

if __name__ == "__main__":
    links_abc = obtener_links_abc()
    links_uh = obtener_links_uh()
    
    # Unimos y filtramos de nuevo por si acaso
    todos_los_links = [l for l in list(set(links_abc + links_uh)) if es_noticia_relevante(l)]
    
    print(f"✅ Encontrados {len(todos_los_links)} links RELEVANTES. Empezando extracción...")

    noticias_finales = []
    # Procesamos los primeros 15 para una prueba más real
    for i, link in enumerate(todos_los_links[:15]): 
        print(f"[{i+1}/{len(todos_los_links[:15])}] Minando: {link}")
        datos = extraer_cuerpo_noticia(link)
        if datos and len(datos['texto']) > 100: # Evitar textos vacíos
            noticias_finales.append(datos)
        time.sleep(1)

    # Guardado robusto
    carpeta = 'data'
    if not os.path.exists(carpeta): os.makedirs(carpeta)
    
    with open(os.path.join(carpeta, 'noticias_raw.json'), 'w', encoding='utf-8') as f:
        json.dump(noticias_finales, f, ensure_ascii=False, indent=4)
    
    print(f"\n¡LISTO! Archivo 'data/noticias_raw.json' actualizado con noticias filtradas.")