from crewai import Task, Crew
from services.accommodation_agent import hotel_agent
from services.restaurant_agent import restaurant_agent
from services.activities_agent import activities_agent
from services.transport_agent import transport_agent
from services.itinerary_agent import itinerary_agent

def crear_tarea_personalizada(descripcion_cliente):
    """Crea una tarea personalizada basada en la descripción del cliente"""
    return Task(
        description=f"Cliente: '{descripcion_cliente}'. Planificar viaje personalizado en Madrid.",
        agent=itinerary_agent,
        expected_output="Recomendaciones personalizadas de alojamiento, actividades, restaurantes y transporte basadas en la solicitud específica del cliente, incluyendo horarios, precios y consejos prácticos."
    )

def ejecutar_planificacion(descripcion_cliente):
    """Ejecuta la planificación del viaje"""
    print(f"\n🎯 Planificando viaje para: '{descripcion_cliente}'")
    print("=" * 60)
    
    # Crear tarea personalizada
    tarea = crear_tarea_personalizada(descripcion_cliente)
    
    # Crear crew con la tarea
    crew = Crew(
        agents=[hotel_agent, restaurant_agent, activities_agent, transport_agent, itinerary_agent],
        tasks=[tarea],
        verbose=True
    )
    
    # Ejecutar planificación
    result = crew.kickoff()
    return result

if __name__ == "__main__":
    print("🏛️ ¡Bienvenido al Planificador de Viajes de Madrid! 🏛️")
    print("=" * 60)
    
    while True:
        print("\n¿Qué tipo de viaje planeas? (escribe 'salir' para terminar)")
        print("Ejemplos:")
        print("- 'Voy mañana 2 días con mi hijo de 5 años, ¿dónde alojarme en el centro y qué ver?'")
        print("- 'Necesito un hotel familiar para 3 días con actividades para niños'")
        print("- 'Quiero conocer Madrid en un fin de semana con mi pareja'")
        
        descripcion = input("\n📝 Tu solicitud: ").strip()
        
        if descripcion.lower() in ['salir', 'exit', 'quit']:
            print("\n¡Hasta luego! ¡Que disfrutes tu viaje a Madrid! 🎉")
            break
        
        if not descripcion:
            print("❌ Por favor, escribe una descripción de tu viaje.")
            continue
        
        try:
            resultado = ejecutar_planificacion(descripcion)
            print("\n" + "=" * 60)
            print("🎉 ¡ITINERARIO PERSONALIZADO COMPLETADO! 🎉")
            print("=" * 60)
            print(resultado)
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"❌ Error al planificar el viaje: {e}")
            print("Inténtalo de nuevo con una descripción más específica.")
        
        print("\n" + "-" * 60)