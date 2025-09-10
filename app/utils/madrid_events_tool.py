import requests

def madrid_events_search(query: str = "eventos familiares") -> str:
    """
    Busca eventos y actividades en Madrid usando Madrid Open Data.
    query: tipo de actividad a buscar (ej. "museos familiares", "parques", "teatros")
    """
    try:
        # Используем Madrid Open Data напрямую
        eventos = _search_madrid_open_data(query)
        if eventos:
            return str(eventos)
    except Exception as e:
        print(f"Error con Madrid Open Data: {e}")
    
    # Si falla, usamos datos de respaldo
    return _get_fallback_data()

def _search_madrid_open_data(query: str) -> list:
    """Busca en Madrid Open Data"""
    try:
        # Diferentes endpoints según la consulta
        endpoints = _get_endpoints_for_query(query)
        
        all_results = []
        
        for endpoint_name, endpoint_url in endpoints.items():
            try:
                response = requests.get(endpoint_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    processed_data = _process_data(data, endpoint_name)
                    all_results.extend(processed_data)
            except Exception as e:
                print(f"Error al consultar {endpoint_name}: {e}")
                continue
        
        return all_results[:5]  # Limitar a 5 resultados
        
    except Exception as e:
        print(f"Error general en Madrid Open Data: {e}")
        return []

def _get_endpoints_for_query(query: str) -> dict:
    """Retorna los endpoints apropiados basados en la consulta"""
    query_lower = query.lower()
    
    endpoints = {}
    
    # Eventos culturales
    if any(word in query_lower for word in ["evento", "cultura", "cultural", "actividad"]):
        endpoints["eventos_culturales"] = "https://datos.madrid.es/egob/catalogo/202625-0-agenda-eventos-culturales-100.json"
    
    # Museos
    if any(word in query_lower for word in ["museo", "museum", "exposición", "exposicion"]):
        endpoints["museos"] = "https://datos.madrid.es/egob/catalogo/201132-0-museos.json"
    
    # Parques y jardines
    if any(word in query_lower for word in ["parque", "park", "jardín", "jardin", "verde"]):
        endpoints["parques"] = "https://datos.madrid.es/egob/catalogo/200295-0-parques-jardines.json"
    
    # Si no hay coincidencias específicas, usar eventos culturales por defecto
    if not endpoints:
        endpoints["eventos_culturales"] = "https://datos.madrid.es/egob/catalogo/202625-0-agenda-eventos-culturales-100.json"
    
    return endpoints

def _process_data(data: dict, endpoint_name: str) -> list:
    """Procesa los datos según el tipo de endpoint"""
    results = []
    
    try:
        if endpoint_name == "eventos_culturales":
            results = _process_eventos_culturales(data)
        elif endpoint_name == "museos":
            results = _process_museos(data)
        elif endpoint_name == "parques":
            results = _process_parques(data)
    except Exception as e:
        print(f"Error procesando {endpoint_name}: {e}")
    
    return results
    
def _process_eventos_culturales(data: dict) -> list:
    """Procesa datos de eventos culturales"""
    eventos = []
    
    # La estructura puede variar, intentamos diferentes formatos
    if "data" in data:
        items = data["data"]
    elif "result" in data:
        items = data["result"]
    else:
        items = data.get("@graph", [])
    
    for item in items[:3]:  # Limitar a 3 por endpoint
        evento = {
            "nombre": item.get("title", item.get("nombre", "Evento sin nombre")),
            "tipo": "Evento Cultural",
            "fecha": item.get("dtstart", item.get("fecha", "Fecha no disponible")),
            "lugar": item.get("location", item.get("lugar", "Lugar no disponible")),
            "descripción": item.get("description", item.get("descripcion", "Sin descripción")),
            "precio": item.get("price", item.get("precio", "Consultar")),
            "fuente": "Madrid Open Data - Eventos Culturales"
        }
        eventos.append(evento)
    
    return eventos

def _process_museos(data: dict) -> list:
    """Procesa datos de museos"""
    museos = []
    
    if "data" in data:
        items = data["data"]
    elif "result" in data:
        items = data["result"]
    else:
        items = data.get("@graph", [])
    
    for item in items[:3]:
        museo = {
            "nombre": item.get("title", item.get("nombre", "Museo sin nombre")),
            "tipo": "Museo",
            "dirección": item.get("address", item.get("direccion", "Dirección no disponible")),
            "horario": item.get("opening_hours", item.get("horario", "Consultar horarios")),
            "precio": item.get("price", item.get("precio", "Consultar precios")),
            "descripción": item.get("description", item.get("descripcion", "Museo de Madrid")),
            "fuente": "Madrid Open Data - Museos"
        }
        museos.append(museo)
    
    return museos

def _process_parques(data: dict) -> list:
    """Procesa datos de parques"""
    parques = []
    
    if "data" in data:
        items = data["data"]
    elif "result" in data:
        items = data["result"]
    else:
        items = data.get("@graph", [])
    
    for item in items[:3]:
        parque = {
            "nombre": item.get("title", item.get("nombre", "Parque sin nombre")),
            "tipo": "Parque",
            "dirección": item.get("address", item.get("direccion", "Dirección no disponible")),
            "horario": item.get("opening_hours", item.get("horario", "Siempre abierto")),
            "precio": "Gratis",
            "descripción": item.get("description", item.get("descripcion", "Parque de Madrid")),
            "fuente": "Madrid Open Data - Parques"
        }
        parques.append(parque)
    
    return parques

def _get_fallback_data() -> str:
    """Datos de respaldo cuando no hay API key o falla la consulta"""
    eventos = [
        {
            "nombre": "Museo del Prado - Visita Familiar",
            "tipo": "Museo",
            "horario": "10:00 - 20:00",
            "precio": "Gratis para menores de 18 años",
            "descripción": "Visita guiada especial para familias con niños"
        },
        {
            "nombre": "Parque del Retiro - Paseo en Barca",
            "tipo": "Parque",
            "horario": "10:00 - 18:00",
            "precio": "6€ por persona",
            "descripción": "Paseo en barca por el estanque del Retiro"
        },
        {
            "nombre": "Teatro Real - Ópera para Niños",
            "tipo": "Teatro",
            "horario": "17:00",
            "precio": "15€ - 25€",
            "descripción": "Ópera adaptada para toda la familia"
        }
    ]
    return str(eventos)
