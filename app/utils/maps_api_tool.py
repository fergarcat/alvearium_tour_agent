import requests

def maps_transport_search(origin: str = "Centro de Madrid", destination: str = "Aeropuerto") -> str:
    """
    Obtiene información de transporte entre dos puntos en Madrid.
    origin: punto de origen
    destination: punto de destino
    """
    return _get_fallback_transport_data(origin, destination)

def _get_fallback_transport_data(origin: str, destination: str) -> str:
    """Datos de respaldo cuando no hay acceso a Madrid Open Data"""
    opciones_transporte = [
        {
            "tipo": "Metro",
            "tiempo": "45 minutos",
            "precio": "4.50€",
            "descripción": f"Línea 8 desde {origin} hasta {destination}",
            "fuente": "Datos de respaldo"
        },
        {
            "tipo": "Taxi",
            "tiempo": "25 minutos",
            "precio": "30€ - 40€",
            "descripción": f"Taxi directo desde {origin} hasta {destination}",
            "fuente": "Datos de respaldo"
        },
        {
            "tipo": "Autobús",
            "tiempo": "50 minutos",
            "precio": "5€",
            "descripción": f"Línea 200 desde {origin} hasta {destination}",
            "fuente": "Datos de respaldo"
        },
        {
            "tipo": "Coche de alquiler",
            "tiempo": "20 minutos",
            "precio": "25€/día + gasolina",
            "descripción": f"Alquiler de coche para mayor flexibilidad desde {origin}",
            "fuente": "Datos de respaldo"
        }
    ]
    
    return str(opciones_transporte)