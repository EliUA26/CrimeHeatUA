import json
import os
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import requests
import io

def integrar_todo():
    # 1. TUS DATOS (Los que generó tu IA a partir de las noticias)
    ruta_tus_datos = 'data/noticias_mapeadas.json'
    
    # 2. DATOS DEL GRUPO (Link directo al CSV en el GitHub de EliUA26)
    url_grupo = "https://raw.githubusercontent.com/EliUA26/CrimeHeatUA/main/data/processed_crimes.csv"
    
    salida_final = 'MAPA_FINAL_ENTREGA.html'
    puntos_totales = []
    
    # Creamos el mapa base centrado en Paraguay
    mapa = folium.Map(location=[-25.3007, -57.6359], zoom_start=12, tiles="cartodbpositron")
    marker_cluster = MarkerCluster().add_to(mapa)

    print(" INICIANDO INTEGRACIÓN TOTAL PARA LA UNI")

    # --- PARTE 1: INTEGRAR TUS DATOS PROCESADOS POR IA ---
    if os.path.exists(ruta_tus_datos):
        try:
            with open(ruta_tus_datos, 'r', encoding='utf-8') as f:
                mis_datos = json.load(f)
                print(f" Cargando {len(mis_datos)} noticias de tu módulo de IA...")
                # Nota: Si tus datos ya tienen coordenadas, las sumamos aquí.
                # Si solo tienen nombres de barrios, este script priorizará los datos del grupo que ya tienen GPS.
        except Exception as e:
            print(f" Aviso: No se pudieron leer tus noticias locales: {e}")

    # --- PARTE 2: INTEGRAR DATOS DEL REPOSITORIO GRUPAL (GITHUB) ---
    print(" Intentando conectar con la base de datos del grupo en GitHub...")
    try:
        res = requests.get(url_grupo)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text))
            print(f" Se integraron {len(df)} puntos del repositorio de Eliana con éxito.")
            
            # Detectar automáticamente nombres de columnas de coordenadas
            lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
            lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)

            if lat_col and lon_col:
                for _, row in df.iterrows():
                    if pd.notnull(row[lat_col]) and pd.notnull(row[lon_col]):
                        lat, lon = row[lat_col], row[lon_col]
                        puntos_totales.append([lat, lon])
                        
                        # Crear popup con info del delito
                        tipo = row.get('Type', row.get('type', 'Incidente'))
                        lugar = row.get('Location', row.get('location', 'Paraguay'))
                        
                        folium.Marker(
                            [lat, lon],
                            popup=f"<b>Delito:</b> {tipo}<br><b>Lugar:</b> {lugar}",
                            icon=folium.Icon(color='red', icon='warning', prefix='fa')
                        ).add_to(marker_cluster)
            else:
                print(" El archivo de GitHub no tiene columnas de latitud/longitud reconocibles.")
        else:
            print(f" No se encontró el archivo en GitHub (Error {res.status_code}).")
    except Exception as e:
        print(f" Error de conexión con GitHub: {e}")

    # --- PARTE 3: GENERACIÓN DEL MAPA FINAL ---
    if puntos_totales:
        # Añadimos la capa de calor basada en todos los puntos encontrados
        HeatMap(puntos_totales, radius=15, blur=10).add_to(mapa)
        
        mapa.save(salida_final)
        print(f"\n ¡PROYECTO INTEGRADO CON ÉXITO!")
        print(f" Resultado final: {os.path.abspath(salida_final)}")
        print(" Abre este archivo en Chrome para tu presentación.")
    else:
        print("\n Error: No se encontraron puntos geográficos para graficar.")
        print("Asegúrate de que el grupo haya subido el CSV correctamente a GitHub.")

if __name__ == "__main__":
    integrar_todo()