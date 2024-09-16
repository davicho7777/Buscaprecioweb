# Buscaprecioweb
Este proyecto es un rastreador de precios web desarrollado con Python y Flask. Permite a los usuarios buscar elementos en páginas web, extraer precios utilizando selectores CSS o XPath, guardar combinaciones de URL y selectores, y visualizar la evolución de los precios a lo largo del tiempo mediante gráficos.

# Rastreador de Precios Web

Este proyecto es una aplicación web para rastrear precios de productos en línea. Permite a los usuarios buscar elementos en páginas web, extraer precios utilizando selectores CSS o XPath, guardar combinaciones de URL y selectores, y visualizar la evolución de los precios a lo largo del tiempo.

## Características

- Búsqueda de elementos en páginas web
- Extracción de precios utilizando selectores CSS o XPath
- Guardado de combinaciones de URL y selectores
- Visualización de la evolución de precios mediante gráficos
- Interfaz web simple y fácil de usar

## Tecnologías utilizadas

- Python
- Flask
- BeautifulSoup
- lxml
- Pandas
- HTML/CSS/JavaScript

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/rastreador-precios-web.git
   ```

2. Navega al directorio del proyecto:
   ```
   cd rastreador-precios-web
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

1. Inicia la aplicación:
   ```
   python app.py
   ```

2. Abre tu navegador y ve a `http://localhost:5000`

3. Utiliza la interfaz web para:
   - Buscar elementos en páginas web
   - Obtener precios utilizando selectores
   - Guardar combinaciones de URL y selectores
   - Visualizar gráficos de precios

## Estructura del proyecto

- `app.py`: Contiene la lógica principal de la aplicación Flask
- `index.html`: Interfaz de usuario de la aplicación web
- `combinaciones.json`: Almacena las combinaciones guardadas de URL y selectores
- `datos.json`: Almacena los datos de precios extraídos
- `precios.csv`: Almacena el historial de precios en formato CSV

