import requests

def hotels_search(query: str = "hoteles familiares") -> str:
    """
    Busca hoteles y alojamientos en Madrid.
    query: tipo de búsqueda (ej. "hoteles familiares", "hoteles con piscina", "apartamentos")
    """
    try:
        # Simulamos búsqueda de hoteles con datos realistas
        hotels = _get_hotels_data(query)
        return str(hotels)
    except Exception as e:
        print(f"Error buscando hoteles: {e}")
        return _get_fallback_hotels()

def _get_hotels_data(query: str) -> list:
    """Obtiene datos de hoteles basados en la consulta"""
    query_lower = query.lower()
    
    # Datos simulados de hoteles en Madrid
    all_hotels = [
        {
            "nombre": "Hotel Ritz Madrid",
            "tipo": "Hotel de lujo",
            "dirección": "Plaza de la Lealtad, 5, 28014 Madrid",
            "precio": "€€€€",
            "características": ["Piscina", "Spa", "Restaurante", "Niñera"],
            "rating": 4.8,
            "descripción": "Hotel histórico de lujo en el centro de Madrid, ideal para familias",
            "zona": "Centro"
        },
        {
            "nombre": "NH Collection Madrid Palacio de Tepa",
            "tipo": "Hotel 4 estrellas",
            "dirección": "Calle de San Sebastián, 2, 28012 Madrid",
            "precio": "€€€",
            "características": ["WiFi", "Desayuno", "Gimnasio", "Aire acondicionado"],
            "rating": 4.5,
            "descripción": "Hotel moderno en el centro histórico, perfecto para familias",
            "zona": "Centro"
        },
        {
            "nombre": "Hotel VP Plaza España Design",
            "tipo": "Hotel 4 estrellas",
            "dirección": "Plaza de España, 5, 28008 Madrid",
            "precio": "€€€",
            "características": ["Terraza", "Bar", "WiFi", "Parking"],
            "rating": 4.3,
            "descripción": "Hotel de diseño cerca del Palacio Real, ideal para familias",
            "zona": "Centro"
        },
        {
            "nombre": "Hotel NH Madrid Ribera del Manzanares",
            "tipo": "Hotel 4 estrellas",
            "dirección": "Calle de Ribera del Manzanares, 7, 28005 Madrid",
            "precio": "€€",
            "características": ["WiFi", "Desayuno", "Gimnasio", "Aire acondicionado"],
            "rating": 4.2,
            "descripción": "Hotel moderno cerca del río, con habitaciones familiares",
            "zona": "Arganzuela"
        },
        {
            "nombre": "Hotel Only YOU Boutique Madrid",
            "tipo": "Hotel boutique",
            "dirección": "Calle de Barquillo, 21, 28004 Madrid",
            "precio": "€€€",
            "características": ["Terraza", "Bar", "WiFi", "Diseño único"],
            "rating": 4.4,
            "descripción": "Hotel boutique con estilo único, perfecto para familias creativas",
            "zona": "Chueca"
        }
    ]
    
    # Filtrar hoteles basado en la consulta
    filtered_hotels = []
    for hotel in all_hotels:
        if any(word in query_lower for word in ["familia", "family", "niños", "kids"]):
            if "niñera" in hotel["características"] or "familia" in hotel["descripción"].lower():
                filtered_hotels.append(hotel)
        elif any(word in query_lower for word in ["lujo", "luxury", "5 estrellas"]):
            if hotel["tipo"] == "Hotel de lujo":
                filtered_hotels.append(hotel)
        elif any(word in query_lower for word in ["económico", "barato", "€€"]):
            if hotel["precio"] in ["€€", "€"]:
                filtered_hotels.append(hotel)
        elif any(word in query_lower for word in ["piscina", "pool", "spa"]):
            if any(car in hotel["características"] for car in ["Piscina", "Spa"]):
                filtered_hotels.append(hotel)
        else:
            filtered_hotels.append(hotel)
    
    return filtered_hotels[:3]  # Limitar a 3 resultados

def _get_fallback_hotels() -> str:
    """Datos de respaldo cuando no hay acceso a API"""
    hotels = [
        {
            "nombre": "Hotel Ritz Madrid",
            "tipo": "Hotel de lujo",
            "dirección": "Plaza de la Lealtad, 5, 28014 Madrid",
            "precio": "€€€€",
            "características": ["Piscina", "Spa", "Restaurante", "Niñera"],
            "rating": 4.8,
            "descripción": "Hotel histórico de lujo en el centro de Madrid",
            "zona": "Centro"
        },
        {
            "nombre": "NH Collection Madrid Palacio de Tepa",
            "tipo": "Hotel 4 estrellas",
            "dirección": "Calle de San Sebastián, 2, 28012 Madrid",
            "precio": "€€€",
            "características": ["WiFi", "Desayuno", "Gimnasio"],
            "rating": 4.5,
            "descripción": "Hotel moderno en el centro histórico",
            "zona": "Centro"
        }
    ]
    return str(hotels)
