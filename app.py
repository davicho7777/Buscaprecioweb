import os
import csv
import json
import datetime
import logging
from flask import Flask, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import requests
from lxml import etree
import pandas as pd

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMBINACIONES_FILE = os.path.join(BASE_DIR, 'combinaciones.json')
DATOS_FILE = os.path.join(BASE_DIR, 'datos.json')
PRECIO_FILE = os.path.join(BASE_DIR, 'precios.csv')

def obtener_numero(url, selector, es_xpath=False):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.info(f"Intentando obtener precio de: {url}")
        response = requests.get(url, headers=headers)
        logging.debug(f"Código de estado de la respuesta: {response.status_code}")
        
        if response.status_code != 200:
            logging.error(f"Error al obtener la página. Código de estado: {response.status_code}")
            return None

        if es_xpath:
            tree = etree.HTML(response.content)
            elementos = tree.xpath(selector)
            if elementos:
                elemento = elementos[0]
                texto = elemento.text.strip() if elemento.text else ""
            else:
                logging.error(f"No se encontró el elemento con el XPath: {selector}")
                return None
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            elemento = soup.select_one(selector)
            if elemento:
                texto = elemento.text.strip()
            else:
                logging.error(f"No se encontró el elemento con el selector CSS: {selector}")
                return None

        logging.info(f"Texto extraído del elemento: {texto}")
        # Eliminar caracteres no numéricos excepto el punto decimal
        precio = ''.join(c for c in texto if c.isdigit() or c == '.')
        logging.info(f"Precio extraído: {precio}")
        return precio
    except Exception as e:
        logging.exception(f"Error al obtener el número: {e}")
        return None
    
def guardar_datos_en_archivo(precio, fecha_hora, url):
    with open(PRECIO_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([precio, fecha_hora, url])

def guardar_datos_en_json(precio, fecha_hora, url):
    datos = {'precio': precio, 'fecha_hora': fecha_hora, 'url': url}
    with open(DATOS_FILE, 'a', encoding='utf-8') as f:
        json.dump(datos, f)
        f.write('\n')

@app.route('/buscar_elementos', methods=['POST'])
def buscar_elementos():
    data = request.json
    url = data.get('url')
    keywords = data.get('keywords')
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        elementos = soup.find_all(text=True)
        resultados = [elemento.strip() for elemento in elementos if any(keyword in elemento for keyword in keywords)]
        return jsonify(resultados)
    except Exception as e:
        logging.exception(f"Error al buscar elementos: {e}")
        return jsonify({'error': 'Error al buscar elementos'}), 500

@app.route('/obtener_precio', methods=['POST'])
def obtener_precio():
    data = request.json
    url = data.get('url')
    selector = data.get('selector')
    es_xpath = data.get('es_xpath', False)
    logging.info(f"Recibida solicitud para obtener precio. URL: {url}, Selector: {selector}, Es XPath: {es_xpath}")
    
    precio = obtener_numero(url, selector, es_xpath)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if precio:
        logging.info(f"Precio obtenido exitosamente: {precio}")
        # Guardar los datos en cada consulta
        guardar_datos_en_archivo(precio, fecha_hora, url)
        guardar_datos_en_json(precio, fecha_hora, url)
        return jsonify({'precio': precio, 'fecha_hora': fecha_hora, 'url': url})
    else:
        logging.error("No se pudo obtener el precio")
        return jsonify({'error': 'No se pudo obtener el precio'}), 400

@app.route('/guardar_combinacion', methods=['POST'])
def guardar_combinacion():
    data = request.json
    nombre = data.get('nombre')
    url = data.get('url')
    selector = data.get('selector')
    combinacion = {'nombre': nombre, 'url': url, 'selector': selector}
    try:
        with open(COMBINACIONES_FILE, 'r+', encoding='utf-8') as f:
            combinaciones = json.load(f)
            combinaciones.append(combinacion)
            f.seek(0)
            json.dump(combinaciones, f)
            f.truncate()
        logging.info(f"Combinación guardada correctamente: {combinacion}")
        return jsonify({'mensaje': 'Combinación guardada correctamente'})
    except FileNotFoundError:
        with open(COMBINACIONES_FILE, 'w', encoding='utf-8') as f:
            json.dump([combinacion], f)
        logging.info(f"Archivo de combinaciones creado y combinación guardada: {combinacion}")
        return jsonify({'mensaje': 'Combinación guardada correctamente'})
    except Exception as e:
        logging.exception(f"Error al guardar la combinación: {e}")
        return jsonify({'error': 'Error al guardar la combinación'}), 500

@app.route('/obtener_combinaciones', methods=['GET'])
def obtener_combinaciones():
    try:
        with open(COMBINACIONES_FILE, 'r', encoding='utf-8') as f:
            combinaciones = json.load(f)
            logging.info(f"Combinaciones obtenidas exitosamente. Total: {len(combinaciones)}")
            return jsonify(combinaciones)
    except FileNotFoundError:
        logging.warning("Archivo de combinaciones no encontrado. Devolviendo lista vacía.")
        return jsonify([])
    except Exception as e:
        logging.exception(f"Error al obtener las combinaciones: {e}")
        return jsonify({'error': 'Error al obtener las combinaciones'}), 500

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/obtener_datos_grafico/<nombre_combinacion>')
def obtener_datos_grafico(nombre_combinacion):
    try:
        # Leer el archivo de combinaciones
        with open(COMBINACIONES_FILE, 'r', encoding='utf-8') as f:
            combinaciones = json.load(f)
        
        # Buscar la combinación seleccionada
        combinacion = next((c for c in combinaciones if c['nombre'] == nombre_combinacion), None)
        if not combinacion:
            return jsonify({'error': 'Combinación no encontrada'}), 404

        # Leer el archivo CSV de precios
        df = pd.read_csv(PRECIO_FILE, names=['precio', 'fecha_hora', 'url'], parse_dates=['fecha_hora'])
        
        # Filtrar los datos por la URL de la combinación
        df_filtrado = df[df['url'] == combinacion['url']]
        
        # Ordenar por fecha
        df_filtrado = df_filtrado.sort_values('fecha_hora')
        
        # Convertir a listas para la respuesta JSON
        fechas = df_filtrado['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        precios = df_filtrado['precio'].tolist()
        
        return jsonify({
            'fechas': fechas,
            'precios': precios
        })
    except Exception as e:
        logging.exception(f"Error al obtener datos para el gráfico: {e}")
        return jsonify({'error': 'Error al obtener datos para el gráfico'}), 500


if __name__ == '__main__':
    os.makedirs(BASE_DIR, exist_ok=True)
    logging.info(f"Directorio base: {BASE_DIR}")
    app.run(debug=True)