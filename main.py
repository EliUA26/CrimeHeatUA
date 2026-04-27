import os
from flask import Flask, send_file


app = Flask(__name__)


ruta_mapa = 'backend/proyecto_heatmapp/MAPA_FINAL_ENTREGA.html'

def ejecutar_pipeline():
    os.system('python3 main_scraper.py')
    os.system('python3 procesador_ia.py')
    os.system('python3 db_injector.py')
    os.system('python3 super_integrador.py') 

@app.route('/')
def mostrar_mapa():
    if not os.path.exists(ruta_mapa):
        return "El mapa aún no ha sido generado. Por favor, ejecuta el pipeline primero."
    return send_file(ruta_mapa)

@app.route('/ejecutar')
def ejecutar():
    ejecutar_pipeline()
    return "Pipeline ejecutado. El mapa se ha actualizado."


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



   

