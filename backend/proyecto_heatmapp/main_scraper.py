import psycopg2
from generador_mapa import generar_mapa # Importamos tu función anterior

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "database": "crime_heatmap",
    "user": "adminua",
    "password": "password123",
    "port": "5432"
}

def guardar_en_db(datos_procesados):
    """Inserta los datos clasificados por la IA en la base de datos PostGIS."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        insert_query = """
        INSERT INTO delitos (tipo_delito, fecha_evento, gravedad, ubicacion_texto, resumen_breve, geom, url_fuente)
        VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
        ON CONFLICT (url_fuente) DO NOTHING; 
        """

        # Nota: PostGIS usa (Longitud, Latitud)
        cur.execute(insert_query, (
            datos_procesados['tipo_delito'],
            datos_procesados['fecha_evento'],
            datos_procesados['gravedad'],
            datos_procesados['ubicacion_texto'],
            datos_procesados['resumen_breve'],
            datos_procesados['lng'], 
            datos_procesados['lat'],
            datos_procesados['url_fuente']
        ))

        conn.commit()
        print(f"✅ Guardado con éxito: {datos_procesados['tipo_delito']} en {datos_procesados['ubicacion_texto']}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error al guardar en DB: {e}")

def ejecutar_flujo_completo():
    print("--- INICIANDO SCRAPER DE CRIMINALIDAD ASUNCIÓN ---")

    # SIMULACIÓN: Aquí iría tu lógica de BeautifulSoup/Selenium y luego la IA
    # Supongamos que la IA ya procesó una noticia y te devolvió esto:
    noticia_ejemplo = {
        'tipo_delito': 'MOTOCHORRO',
        'fecha_evento': '2026-04-25',
        'gravedad': 7,
        'ubicacion_texto': 'Cerca de Multiplaza',
        'resumen_breve': 'Asalto violento en parada de bus.',
        'lat': -25.3167,
        'lng': -57.5722,
        'url_fuente': 'https://www.abc.com.py/noticia/12345' 
    }

    # 1. Guardar en la base de datos
    guardar_en_db(noticia_ejemplo)

    # 2. Generar el mapa actualizado con los nuevos datos de la DB
    print("\n--- ACTUALIZANDO MAPA DE CALOR ---")
    generar_mapa()

if __name__ == "__main__":
    ejecutar_flujo_completo()