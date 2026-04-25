import g4f
import json
import os
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Inicializamos el geolocalizador
geolocator = Nominatim(user_agent="crime_heatmap_asuncion_v2")

def geolocalizar(lugar, barrio, ciudad):
    """Convierte texto en coordenadas Lat/Lng para PostGIS."""
    try:
        # Intentamos una búsqueda específica: Lugar + Barrio + Ciudad
        query = f"{lugar}, {barrio}, {ciudad}, Paraguay"
        location = geolocator.geocode(query, timeout=10)
        
        if not location and barrio:
            # Si falla, intentamos solo Barrio + Ciudad
            query = f"{barrio}, {ciudad}, Paraguay"
            location = geolocator.geocode(query, timeout=10)
            
        if location:
            return location.latitude, location.longitude
        return -25.2822, -57.6359  # Coordenadas por defecto (Centro de Asunción) si falla
    except:
        return -25.2822, -57.6359

def procesar_con_ia(texto_noticia):
    """Usa IA para extraer datos estructurados segun nuestro esquema SQL."""
    
        prompt = (
            "Actúa como un analista de seguridad ciudadana en Paraguay. "
            "Extrae la información de la noticia y responde ÚNICAMENTE con un objeto JSON puro. "
            "REGLAS CRÍTICAS DE FORMATO:\n"
            "1. CATEGORÍAS DE DELITO: Solo usa [ASALTO, ROBO, MOTOCHORRO, HOMICIDIO, ACCIDENTE].\n"
            "2. FECHA: Usa SIEMPRE formato 'YYYY-MM-DD'. Si la noticia no menciona una fecha específica, "
            f"usa la fecha de hoy: 2026-04-25. NUNCA uses palabras como 'ayer' o 'lunes'.\n"
            "3. GRAVEDAD: Un número entero del 1 al 10.\n"
            "\n"
            "Formato JSON requerido:\n"
            "{\n"
            "  \"tipo_delito\": \"\",\n"
            "  \"fecha_evento\": \"\",\n"
            "  \"gravedad\": ,\n"
            "  \"ubicacion_texto\": \"\",\n"
            "  \"barrio\": \"\",\n"
            "  \"ciudad\": \"\",\n"
            "  \"resumen\": \"\"\n"
            "}\n"
            f"Noticia a procesar: {texto_noticia[:800]}"
        )

    modelos = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
    
    for modelo in modelos:
        try:
            response = g4f.ChatCompletion.create(
                model=modelo,
                messages=[{"role": "user", "content": prompt}],
            )
            
            # Limpieza de markdown si la IA lo agrega
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].strip()

            return json.loads(response)
        except Exception as e:
            print(f"   ⚠️ Error con modelo {modelo}, probando el siguiente...")
            continue
    return None

def principal():
    entrada = 'data/noticias_raw.json'
    salida = 'data/noticias_mapeadas.json'

    if not os.path.exists(entrada):
        print(f"❌ No existe el archivo de entrada: {entrada}")
        return

    with open(entrada, 'r', encoding='utf-8') as f:
        noticias = json.load(f)

    print(f"🚀 PROCESANDO {len(noticias)} NOTICIAS PARA LA DB SQL...")
    resultados = []

    for i, n in enumerate(noticias):
        print(f"[{i+1}/{len(noticias)}] Analizando: {n['titulo'][:50]}...")
        
        datos_ia = procesar_con_ia(n['texto'])
        
        if datos_ia:
            # Agregamos coordenadas para nuestra columna 'geom' de PostGIS
            lat, lng = geolocalizar(datos_ia['ubicacion_texto'], datos_ia['barrio'], datos_ia['ciudad'])
            
            # Formateamos el objeto final para que el Scraper lo suba directo a SQL
            registro = {
                "url_fuente": n['url'],
                "tipo_delito": datos_ia['tipo_delito'].upper(),
                "fecha_evento": datos_ia['fecha_evento'],
                "gravedad": datos_ia['gravedad'],
                "ubicacion_texto": datos_ia['ubicacion_texto'],
                "barrio": datos_ia['barrio'],
                "ciudad": datos_ia['ciudad'],
                "resumen_breve": datos_ia['resumen'],
                "lat": lat,
                "lng": lng
            }
            resultados.append(registro)
            print(f"   ✅ Estructurado y Geolocalizado en: {lat}, {lng}")
        
        time.sleep(1) # Evitar bloqueos de API

    with open(salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    
    print(f"\n✨ PROCESO COMPLETADO. Datos listos para inyectar en SQL.")

if __name__ == "__main__":
    principal()

from datetime import datetime
fecha_hoy = datetime.now().strftime('%Y-%m-%d')

# Y en el prompt cambias el texto fijo por la variable:
# f"usa la fecha de hoy: {fecha_hoy}. NUNCA uses..."