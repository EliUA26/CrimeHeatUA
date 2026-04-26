import json
import os
import pandas as pd
import folium
from folium.plugins import HeatMap, MarkerCluster
import psycopg2
import requests
import io

# Configuración de tu DB local (Docker)
DB_CONFIG = {
    "host": "localhost",
    "database": "crime_heatmap",
    "user": "adminua",
    "password": "password123",
    "port": "5432"
}

def integrar_todo():
    # URL del repositorio grupal de Eliana
    url_grupo = "https://raw.githubusercontent.com/EliUA26/CrimeHeatUA/main/data/processed_crimes.csv"
    salida_final = 'MAPA_FINAL_ENTREGA.html'
    
    puntos_totales = []
    
    # 1. Crear el mapa base centrado en Asunción
    mapa = folium.Map(location=[-25.2822, -57.6359], zoom_start=13, tiles="cartodbpositron")
    
    # Creamos capas separadas para que se puedan apagar y prender
    capa_calor = folium.FeatureGroup(name="Mapa de Calor (Densidad)")
    capa_marcadores = MarkerCluster(name="Incidentes Individuales").add_to(mapa)

    print("🚀 INICIANDO INTEGRACIÓN TOTAL - FASE 1")

    # --- PARTE 1: OBTENER TUS DATOS DESDE POSTGRESQL (LOCAL) ---
    print("📡 Conectando a tu base de datos SQL local...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = "SELECT tipo_delito, resumen_breve, ST_Y(geom), ST_X(geom) FROM delitos WHERE geom IS NOT NULL;"
        cur.execute(query)
        mis_datos = cur.fetchall()
        
        for tipo, resumen, lat, lng in mis_datos:
            puntos_totales.append([lat, lng])
            folium.Marker(
                [lat, lng],
                popup=f"<b>TUS DATOS (IA):</b> {tipo}<br>{resumen}",
                icon=folium.Icon(color='blue', icon='robot', prefix='fa')
            ).add_to(capa_marcadores)
        
        print(f"✅ Se integraron {len(mis_datos)} registros de tu base de datos local.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Nota: No se pudo conectar a la DB local. ¿Está prendido Docker? ({e})")

    # --- PARTE 2: INTEGRAR DATOS DEL REPOSITORIO GRUPAL (GITHUB) ---
    print("🌐 Conectando con los datos del equipo en GitHub...")
    try:
        res = requests.get(url_grupo)
        if res.status_code == 200:
            df = pd.read_csv(io.StringIO(res.text))
            
            # Buscamos columnas de latitud y longitud sin importar mayúsculas
            lat_col = next((c for c in df.columns if 'lat' in c.lower()), None)
            lon_col = next((c for c in df.columns if 'lon' in c.lower()), None)

            if lat_col and lon_col:
                conteo_grupo = 0
                for _, row in df.iterrows():
                    if pd.notnull(row[lat_col]) and pd.notnull(row[lon_col]):
                        lat, lon = row[lat_col], row[lon_col]
                        puntos_totales.append([lat, lon])
                        
                        tipo = row.get('Type', row.get('type', 'Incidente'))
                        
                        folium.Marker(
                            [lat, lon],
                            popup=f"<b>GRUPO:</b> {tipo}",
                            icon=folium.Icon(color='red', icon='users', prefix='fa')
                        ).add_to(capa_marcadores)
                        conteo_grupo += 1
                print(f"✅ Se integraron {conteo_grupo} puntos del CSV grupal.")
        else:
            print(f"❌ Error al bajar el CSV de GitHub: Código {res.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión con GitHub: {e}")

    # --- PARTE 3: GENERACIÓN DE CAPA DE CALOR Y GUARDADO ---
    if puntos_totales:
        HeatMap(puntos_totales, radius=15, blur=10).add_to(capa_calor)
        capa_calor.add_to(mapa)
        
        # Añadir control de capas (para que el profe pueda activar/desactivar el calor o los puntos)
        folium.LayerControl().add_to(mapa)
        
        mapa.save(salida_final)
        print(f"\n✨ PROYECTO INTEGRADO CON ÉXITO")
        print(f"📂 Archivo generado: {salida_final}")
    else:
        print("\n❌ Error: No se encontraron puntos para graficar. Revisa la DB y el CSV.")

if __name__ == "__main__":
    integrar_todo()