import json
import os
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def generar_mapa():
    # Rutas de archivos
    entrada = 'data/noticias_mapeadas.json'
    salida_mapa = 'mapa_criminalidad.html'

    # Verificar si el archivo procesado por la IA existe
    if not os.path.exists(entrada):
        print(f" No encuentro el archivo: {entrada}")
        print("Asegúrate de ejecutar primero procesador_ia.py")
        return

    with open(entrada, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    # Inicializar el geolocalizador (Nominatim es gratuito y no requiere API Key)
    geolocator = Nominatim(user_agent="heatmap_paraguay_uni_v2")
    
    puntos_calor = []
    
    print(" Geolocalizando puntos en Paraguay...")

    # Creamos un mapa base centrado en Paraguay
    mapa = folium.Map(location=[-25.3007, -57.6359], zoom_start=7, tiles="cartodbpositron")

    for item in datos:
        info = item['datos']
        # Construimos la dirección: Barrio, Ciudad, Paraguay
        direccion_busqueda = f"{info['barrio']}, {info['ciudad']}, Paraguay"
        
        try:
            # Intentamos obtener las coordenadas
            location = geolocator.geocode(direccion_busqueda, timeout=10)
            if location:
                puntos_calor.append([location.latitude, location.longitude])
                # Añadir un marcador rojo con información del delito
                folium.Marker(
                    [location.latitude, location.longitude],
                    popup=f"<b>Delito:</b> {info['delito']}<br><b>Lugar:</b> {info['lugar']}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(mapa)
                print(f"    Ubicado: {info['barrio']} - {info['ciudad']}")
            else:
                # Si no encuentra el barrio, intentamos solo con la ciudad para no perder el punto
                location = geolocator.geocode(f"{info['ciudad']}, Paraguay", timeout=10)
                if location:
                    puntos_calor.append([location.latitude, location.longitude])
                    print(f"    Ubicado solo por Ciudad: {info['ciudad']}")
        except GeocoderTimedOut:
            print(f"    Tiempo de espera agotado para: {direccion_busqueda}")

    # Si encontramos puntos válidos, generamos la capa de calor
    if puntos_calor:
        HeatMap(puntos_calor).add_to(mapa)
        mapa.save(salida_mapa)
        print(f"\n MAPA GENERADO CON ÉXITO: {salida_mapa}")
        print("Busca el archivo 'mapa_criminalidad.html' en tu carpeta y ábrelo con Chrome o Edge.")
    else:
        print("\n No se pudieron geolocalizar puntos suficientes para el mapa.")

if __name__ == "__main__":
    generar_mapa()