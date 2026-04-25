import os

print("--- 1. Extrayendo noticias (Scraper) ---")
# os.system("python scraper.py") 

print("\n--- 2. Procesando con IA y Geolocalizando ---")
os.system("python procesador_ia.py")

print("\n--- 3. Subiendo a la Base de Datos SQL ---")
os.system("python db_injector.py")

print("\n--- 4. Generando Mapa Integrado ---")
os.system("python super_integrador.py")

print("\n🚀 ¡PROCESO TERMINADO! Abre MAPA_FINAL_ENTREGA.html")