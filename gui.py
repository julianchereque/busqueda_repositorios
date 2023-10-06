import requests
import json
import pandas as pd
from guizero import App, TextBox, PushButton, Text
import sys
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, ConceptsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def buscar_en_google_scholar(query):
    url = f"https://scholar.google.com/scholar?q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        resultados = []
        for resultado in soup.find_all('div', class_='gs_ri'):
            titulo = resultado.find('h3', class_='gs_rt').text
            autores = resultado.find('div', class_='gs_a').text
            resumen = resultado.find('div', class_='gs_rs').text

            resultados.append({
                "Título": titulo,
                "Autores": autores,
                "Resumen": resumen,
                "Enlace": url,  # Puedes agregar el enlace si es posible obtenerlo
            })

        return resultados

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a Google Scholar: {e}")
        return []

def search_pubmed(query):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        # Procesa los resultados de PubMed aquí
        resultados = []
        for pmid in data["esearchresult"]["idlist"]:
            url = f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"
            resultados.append({
                "Título": f"PubMed ID: {pmid}",
                "Resumen": "",  # Puedes obtener el resumen si lo deseas
                "Enlace": url
            })
        return resultados
    else:
        print(f"Error en PubMed: {response.status_code}")
        return []
# Define una función para buscar en la API de CORE
def search_core(query):
    base_url = "https://core.ac.uk:443/api-v2/search/"
    params = {
        "apiKey": "AEu2JYsPDfKd8WiCzvXcaFQUr10NhklO", 
        "q": query,
    }
    response = requests.get(base_url, params=params)
    # Comprueba si la respuesta es exitosa (código 200)
    if response.status_code == 200:
        try:
            data = response.json()
            if "data" in data:
                # Procesa los resultados de CORE aquí
                resultados = []
                for item in data["data"]:
                    resultados.append({
                        "Título": item.get("title", ""),
                        "Resumen": item.get("description", ""),
                        "Enlace": item.get("pdf_url", "")
                    })
                return resultados
            else:
                print("La respuesta de CORE no contiene datos válidos.")
                return []
        except json.JSONDecodeError:
            print("La respuesta de CORE no es un JSON válido.")
            return []
    else:
        print(f"Error en CORE: {response.status_code}")
        return []

# Define una función para buscar en la API de arXiv
def search_arxiv(query):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": 5,  # Ajusta el número de resultados según tus necesidades
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.text
        # Procesa los resultados de arXiv aquí
        resultados = []
        # Analiza el XML o el texto de arXiv para obtener títulos, resúmenes y enlaces
        # Puedes utilizar bibliotecas como xml.etree.ElementTree o regex para esto
        # Agrega los resultados a la lista "resultados" en el formato correcto
        return resultados
    else:
        print(f"Error en arXiv: {response.status_code}")
        return []

# Define una función para buscar en la API de Semantic Scholar
def search_semantic_scholar(query):
    base_url = "https://api.semanticscholar.org/v1/paper/search"
    params = {
        "query": query,
        "limit": 5,  # Ajusta el número de resultados según tus necesidades
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Procesa los resultados de Semantic Scholar aquí
        resultados = []
        for item in data["data"]:
            resultados.append({
                "Título": item["title"],
                "Resumen": item.get("abstract", ""),
                "Enlace": f"https://www.semanticscholar.org/paper/{item['paperId']}"
            })
        return resultados
    else:
        print(f"Error en Semantic Scholar: {response.status_code}")
        return []

# Define una función para buscar en la API de Unpaywall
def search_unpaywall(query):
    base_url = "https://api.unpaywall.org/v2/search"
    params = {
        "query": query,
        "limit": 5,  # Ajusta el número de resultados según tus necesidades
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        # Comprueba si hay resultados
        if data:
            resultados = []
            for item in data:
                resultados.append({
                    "Título": item.get("title", "Sin título disponible"),
                    "Resumen": "",
                    "Enlace": item["best_oa_location"]["url_for_pdf"]
                })
            return resultados
        else:
            print("No se encontraron resultados para la consulta.")
            return []
    else:
        print(f"Error en Unpaywall: {response.status_code}")
        return []

# Define una función para buscar en la API de Crossref
def search_crossref(query):
    base_url = "https://api.crossref.org/works"
    params = {
        "query.title": query,
        "rows": 5,  # Ajusta el número de resultados según tus necesidades
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        # Procesa los resultados de Crossref aquí
        resultados = []
        for item in data["message"]["items"]:
            resultados.append({
                "Título": item["title"][0],
                "Resumen": "",
                "Enlace": item["URL"]
            })
        return resultados
    else:
        print(f"Error en Crossref: {response.status_code}")
        return []



# Función para manejar el evento del botón
def obtener_cadena():
    query = entrada_cadena.value
    resultados_pubmed = [{'Título': 'PubMed', 'Resumen': '', 'Enlace': ''}] + search_pubmed(query)
    resultados_core = [{'Título': 'Core', 'Resumen': '', 'Enlace': ''}] + search_core(query)
    resultados_arxiv = [{'Título': 'Arxiv', 'Resumen': '', 'Enlace': ''}] + search_arxiv(query)
    resultados_semantic_scholar = [{'Título': 'Semantic', 'Resumen': '', 'Enlace': ''}] + search_semantic_scholar(query)
    resultados_unpaywall = [{'Título': 'unpaywall', 'Resumen': '', 'Enlace': ''}] + search_unpaywall(query)
    resultados_crossref = [{'Título': 'crossref', 'Resumen': '', 'Enlace': ''}] + search_crossref(query)
    resultados_google = [{'Título': 'GoogleScholar', 'Resumen': '', 'Enlace': ''}] + buscar_en_google_scholar(query)


    # Combina los resultados de todas las APIs
    resultados_combinados = (resultados_google + resultados_pubmed + resultados_core + resultados_arxiv +
                             resultados_semantic_scholar + resultados_unpaywall +
                             resultados_crossref )

    # Crea un DataFrame de pandas
    df = pd.DataFrame(resultados_combinados)

    # Guarda el DataFrame en un archivo Excel
    df.to_excel("resultados.xlsx", index=False)
    
    Text(app, text="Se ha generado un excel con los resultados")
# Crea una aplicación guizero
app = App("Herramienta de Búsqueda")

# Crea un cuadro de entrada de texto
entrada_cadena = TextBox(app, width=40)

# Crea un botón para capturar la cadena ingresada
boton_capturar = PushButton(app, text="Ejecutar Consulta", command=obtener_cadena)



# Inicia la aplicación
app.display()