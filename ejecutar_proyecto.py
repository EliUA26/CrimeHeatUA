import os

print("--- 1. Extrayendo noticias (Scraper) ---")
os.system("python backend/proyecto_heatmapp/main_scraper.py") 

print("\n--- 2. Procesando con IA y Geolocalizando ---")
os.system("python3 backend/proyecto_heatmapp/procesador_ia.py")

print("\n--- 3. Subiendo a la Base de Datos SQL ---")
os.system("python3 backend/proyecto_heatmapp/db_injector.py")

print("\n--- 4. Generando Mapa Integrado ---")
os.system("python3 backend/proyecto_heatmapp/super_integrador.py")

print("\n--- 4. Generando Mapa Integrado ---")
os.system("python3 backend/proyecto_heatmapp/generador_mapa.py")

print("\n🚀 ¡PROCESO TERMINADO! Abre MAPA_FINAL_ENTREGA.html")