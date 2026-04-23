import g4f
import json
import os
import time

def principal():
    # Rutas de archivos
    entrada = 'data/noticias_raw.json'
    salida = 'data/noticias_mapeadas.json'

    # Verificar existencia del archivo de entrada
    if not os.path.exists(entrada):
        print(f"❌ No se encontró el archivo: {entrada}")
        return

    with open(entrada, 'r', encoding='utf-8') as f:
        noticias = json.load(f)

    print(f"🚀 INICIANDO PROCESAMIENTO INTELIGENTE")
    print(f"Se analizarán {len(noticias)} noticias.\n")
    
    resultados = []
    
    for i, n in enumerate(noticias):
        print(f"[{i+1}/{len(noticias)}] Analizando: {n['titulo'][:45]}...")
        
        # Prompt optimizado para recibir JSON puro
        prompt = (
            f"Actúa como un analista de datos. Extrae la información de la siguiente noticia "
            f"y responde ÚNICAMENTE con un objeto JSON (sin texto extra) con este formato: "
            f"{{\"delito\": \"\", \"lugar\": \"\", \"barrio\": \"\", \"ciudad\": \"\"}}. "
            f"Noticia: {n['texto'][:600]}"
        )
        
        exito = False
        # Intentamos con una lista de modelos comunes por si alguno falla
        modelos_a_probar = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "claude-3-haiku"]
        
        for modelo in modelos_a_probar:
            if exito: break
            try:
                # Llamada simplificada sin especificar proveedor para evitar AttributeError
                response = g4f.ChatCompletion.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                )
                
                if not response or len(response) < 10:
                    continue

                # Limpieza de formato Markdown
                texto_limpio = response
                if "```json" in texto_limpio:
                    texto_limpio = texto_limpio.split("```json")[1].split("```")[0].strip()
                elif "```" in texto_limpio:
                    texto_limpio = texto_limpio.split("```")[1].strip()
                
                # Validar JSON
                datos_ia = json.loads(texto_limpio)
                
                resultados.append({
                    "url": n['url'],
                    "titulo": n['titulo'],
                    "datos": datos_ia
                })
                print(f"   ✅ OK (Modelo: {modelo})")
                exito = True
                
            except Exception:
                # Si falla este modelo, el bucle sigue al siguiente automáticamente
                continue
        
        if not exito:
            print("   ⚠️ No se pudo procesar esta noticia con ningún modelo. Saltando...")
            resultados.append({
                "url": n['url'],
                "titulo": n['titulo'],
                "datos": {"delito": "No detectado", "lugar": "Desconocido", "barrio": "N/A", "ciudad": "N/A"}
            })
        
        # Pausa para evitar bloqueos
        time.sleep(1)

    # Guardar resultados
    with open(salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
        
    print(f"\n✨ PROCESO COMPLETADO")
    print(f"Datos listos para el mapa de calor en: {salida}")

if __name__ == "__main__":
    principal()