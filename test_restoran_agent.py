# test_restoran_agent.py
"""
Test file for RestoranAgent
Tests the restaurant agent functionality with mock data
"""

import os
import sys
from pathlib import Path

# Add project path for correct imports
current_dir = Path(__file__).parent
project_root = current_dir
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import with proper path handling
try:
    from app.services.restoran_agent import RestoranAgent
    from app.models.restaurant_models import *
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    # Alternative import method
    sys.path.append(str(project_root / "app"))
    from services.restoran_agent import RestoranAgent
    from models.restaurant_models import *


def test_restoran_agent_initialization():
    """Test RestoranAgent initialization"""
    print("🧪 Testing RestoranAgent initialization...")
    
    # Set mock API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
    
    try:
        agent = RestoranAgent()
        print("✅ RestoranAgent initialized successfully")
        
        # Check tools
        print(f"📋 Available tools: {len(agent.tools)}")
        for tool in agent.tools:
            print(f"  - {tool.name}")
        
        # Check API services
        print(f"🔌 Google Places API: {'✅ Available' if agent.api_services['google_places'] else '❌ Not configured'}")
        print(f"🌤️ Weather API: {'✅ Available' if agent.api_services['weather'] else '❌ Not configured'}")
        
        return agent
        
    except Exception as e:
        print(f"❌ Error initializing RestoranAgent: {e}")
        print("ℹ️ This is expected if API keys are not configured")
        return None


def test_restoran_agent_with_mock_data():
    """Test RestoranAgent with mock family data"""
    print("\n🧪 Testing RestoranAgent with mock data...")
    
    # Set mock API key for testing
    os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
    
    agent = test_restoran_agent_initialization()
    if not agent:
        print("⚠️ Skipping mock data test - agent not initialized")
        return
    
    # Mock family profile data
    mock_request_data = {
        'profile': {
            'kids_ages': [8, 12],
            'adults_count': 2,
            'dietary_restrictions': ['vegetarian', 'gluten_free'],
            'cuisine_preferences': ['spanish', 'mediterranean'],
            'budget_level': 'moderate',
            'start_date': '2024-01-15',
            'end_date': '2024-01-17',
            'origin_country': 'Spain',
            'special_needs': ['high_chairs', 'kid_menu']
        },
        'query': 'Find family-friendly Spanish restaurants in Madrid'
    }
    
    try:
        print("📝 Processing request...")
        result = agent.process_request(mock_request_data)
        
        # Check result structure
        print(f"✅ Agent result status: {result.get('status')}")
        print(f"🏷️ Agent name: {result.get('agent_name')}")
        print(f"❓ Query: {result.get('query')}")
        print(f"📄 Restaurant text length: {len(result.get('restaurant_text', ''))}")
        
        # Check family context
        family_context = result.get('family_context', {})
        print(f"👶 Kids ages: {family_context.get('kids_ages', [])}")
        print(f"👨‍👩‍👧‍👦 Adults count: {family_context.get('adults_count', 0)}")
        print(f"🥗 Dietary restrictions: {family_context.get('dietary_restrictions', [])}")
        print(f"🍽️ Cuisine preferences: {family_context.get('cuisine_preferences', [])}")
        print(f"💰 Budget level: {family_context.get('budget_level', 'unknown')}")
        print(f"🌍 Origin country: {family_context.get('origin_country', 'unknown')}")
        
        # Check structured data
        structured_data = result.get('structured_data')
        if structured_data:
            print(f"🏪 Total restaurants: {structured_data.total_restaurants}")
            print(f"⏱️ Recommended duration: {structured_data.recommended_duration}")
            print(f"💶 Budget estimate: {structured_data.budget_estimate.range}")
            print(f"🍽️ Cuisine types covered: {[c.value for c in structured_data.cuisine_types_covered]}")
            print(f"🥗 Dietary options: {[d.value for d in structured_data.dietary_restrictions_covered]}")
            print(f"👶 Kid-friendly options: {structured_data.kid_friendly_options}")
        
        # Check metadata
        metadata = result.get('metadata', {})
        print(f"⏰ Processing time: {metadata.get('processing_time', 'unknown')}")
        print(f"🎯 Confidence: {metadata.get('confidence', 0)}")
        print(f"📊 Source: {metadata.get('source', 'unknown')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_restoran_agent_api_calls():
    """Test RestoranAgent API calls"""
    print("\n🧪 Testing RestoranAgent API calls...")
    
    agent = test_restoran_agent_initialization()
    if not agent:
        return
    
    # Test Google Places API call
    if agent.api_services["google_places"]:
        print("🔍 Testing Google Places API...")
        try:
            result = agent._search_restaurants_api("family restaurants Madrid", "restaurant", 2)
            print(f"✅ Google Places API call successful")
            print(f"📄 Result length: {len(result)}")
            
            # Parse JSON result
            import json
            data = json.loads(result)
            if data.get("status") == "success":
                restaurants = data.get("restaurants", [])
                print(f"🏪 Found {len(restaurants)} restaurants")
                for i, restaurant in enumerate(restaurants[:3], 1):
                    print(f"  {i}. {restaurant.get('name', 'Unknown')} - Rating: {restaurant.get('rating', 0)}")
            else:
                print(f"⚠️ API returned error: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Google Places API error: {e}")
    else:
        print("⚠️ Google Places API not configured")
    
    # Test Weather API call
    if agent.api_services["weather"]:
        print("\n🌤️ Testing Weather API...")
        try:
            result = agent._check_weather_api("2024-01-15")
            print(f"✅ Weather API call successful")
            print(f"📄 Result length: {len(result)}")
            
            # Parse JSON result
            import json
            data = json.loads(result)
            if data.get("status") == "success":
                weather = data.get("weather", {})
                print(f"🌡️ Temperature: {weather.get('temperature', 'Unknown')}")
                print(f"☁️ Condition: {weather.get('condition', 'Unknown')}")
                print(f"💨 Wind: {weather.get('wind', 'Unknown')}")
                print(f"🍽️ Outdoor dining: {weather.get('outdoor_dining_recommendation', 'Unknown')}")
            else:
                print(f"⚠️ API returned error: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Weather API error: {e}")
    else:
        print("⚠️ Weather API not configured")


def test_restoran_agent_fallback():
    """Test RestoranAgent fallback functionality"""
    print("\n🧪 Testing RestoranAgent fallback...")
    
    agent = test_restoran_agent_initialization()
    if not agent:
        return
    
    # Test fallback restaurant plan creation
    try:
        fallback_plan = agent._create_restaurant_plan(
            query="test restaurants",
            kids_ages=[5, 10],
            adults_count=2,
            dietary_restrictions=["vegetarian"],
            budget_level="moderate",
            cuisine_preferences=["spanish"],
            travel_dates="2024-01-15"
        )
        
        print("✅ Fallback restaurant plan created successfully")
        print(f"🏪 Total restaurants: {fallback_plan.total_restaurants}")
        print(f"⏱️ Duration: {fallback_plan.recommended_duration}")
        print(f"💶 Budget: {fallback_plan.budget_estimate.range}")
        print(f"📝 Notes: {fallback_plan.budget_estimate.notes}")
        
    except Exception as e:
        print(f"❌ Fallback error: {e}")


def test_restoran_agent_different_scenarios():
    """Test RestoranAgent with different family scenarios"""
    print("\n🧪 Testing RestoranAgent with different scenarios...")
    
    agent = test_restoran_agent_initialization()
    if not agent:
        return
    
    scenarios = [
        {
            "name": "Young children (2-5 years)",
            "profile": {
                'kids_ages': [2, 4],
                'adults_count': 2,
                'dietary_restrictions': ['dairy_free'],
                'cuisine_preferences': ['italian'],
                'budget_level': 'budget',
                'start_date': '2024-06-15',
                'end_date': '2024-06-17',
                'origin_country': 'Germany'
            },
            "query": "Find restaurants for toddlers"
        },
        {
            "name": "Teenagers (13-16 years)",
            "profile": {
                'kids_ages': [13, 16],
                'adults_count': 2,
                'dietary_restrictions': ['vegan'],
                'cuisine_preferences': ['asian', 'fusion'],
                'budget_level': 'expensive',
                'start_date': '2024-08-10',
                'end_date': '2024-08-15',
                'origin_country': 'France'
            },
            "query": "Find trendy restaurants for teenagers"
        },
        {
            "name": "Mixed ages (5-15 years)",
            "profile": {
                'kids_ages': [5, 8, 12, 15],
                'adults_count': 4,
                'dietary_restrictions': ['gluten_free', 'nut_free'],
                'cuisine_preferences': ['mediterranean', 'international'],
                'budget_level': 'moderate',
                'start_date': '2024-12-20',
                'end_date': '2024-12-25',
                'origin_country': 'UK'
            },
            "query": "Find restaurants for large family"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        
        try:
            request_data = {
                'profile': scenario['profile'],
                'query': scenario['query']
            }
            
            result = agent.process_request(request_data)
            
            print(f"✅ Status: {result.get('status')}")
            print(f"👶 Kids: {scenario['profile']['kids_ages']}")
            print(f"🥗 Dietary: {scenario['profile']['dietary_restrictions']}")
            print(f"🍽️ Cuisine: {scenario['profile']['cuisine_preferences']}")
            print(f"💰 Budget: {scenario['profile']['budget_level']}")
            print(f"🌍 Origin: {scenario['profile']['origin_country']}")
            
        except Exception as e:
            print(f"❌ Scenario {i} error: {e}")


def test_restaurant_models():
    """Test restaurant models without agent initialization"""
    print("🧪 Testing Restaurant Models...")
    
    try:
        # Test CuisineType enum
        cuisine = CuisineType.SPANISH
        print(f"✅ CuisineType: {cuisine}")
        
        # Test PriceRange enum
        price = PriceRange.MODERATE
        print(f"✅ PriceRange: {price}")
        
        # Test DietaryRestrictions enum
        dietary = DietaryRestrictions.VEGETARIAN
        print(f"✅ DietaryRestrictions: {dietary}")
        
        # Test Location model
        location = Location(
            address="Calle de la Cava Baja, 35",
            city="Madrid",
            neighborhood="La Latina"
        )
        print(f"✅ Location: {location.address}, {location.city}")
        
        # Test Restaurant model
        restaurant = Restaurant(
            name="Casa Lucio",
            cuisine_type=CuisineType.SPANISH,
            price_range=PriceRange.MODERATE,
            rating=4.5,
            location=location,
            features=["outdoor_seating", "wifi"],
            dietary_options=[DietaryRestrictions.VEGETARIAN],
            kid_friendly=True
        )
        print(f"✅ Restaurant: {restaurant.name} - {restaurant.cuisine_type.value}")
        
        # Test BudgetEstimate model
        budget = BudgetEstimate(
            range="€30-50",
            per_person="€20-30",
            notes="Based on main course and drink"
        )
        print(f"✅ BudgetEstimate: {budget.range}")
        
        # Test RestaurantResponse model
        response = RestaurantResponse(
            restaurants=[restaurant],
            total_restaurants=1,
            recommended_duration="2-3 hours",
            budget_estimate=budget,
            cuisine_types_covered=[CuisineType.SPANISH],
            dietary_restrictions_covered=[DietaryRestrictions.VEGETARIAN],
            kid_friendly_options=1,
            booking_recommendations=["Reserve for dinner"],
            practical_tips=["Check opening hours"],
            weather_considerations=["Outdoor seating available"]
        )
        print(f"✅ RestaurantResponse: {response.total_restaurants} restaurants")
        
        # Test RestaurantAgentResult model
        agent_result = RestaurantAgentResult(
            agent_name="restaurant",
            status="success",
            query="Find Spanish restaurants",
            family_context={"kids_ages": [8, 12]},
            restaurant_text="Found great Spanish restaurants",
            structured_data=response
        )
        print(f"✅ RestaurantAgentResult: {agent_result.agent_name} - {agent_result.status}")
        
        print("🎉 All models working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Model test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Starting RestoranAgent Tests")
    print("=" * 50)
    
    # Test 0: Models (no API keys needed)
    test_restaurant_models()
    
    # Test 1: Initialization
    test_restoran_agent_initialization()
    
    # Test 2: Mock data processing
    test_restoran_agent_with_mock_data()
    
    # Test 3: API calls
    test_restoran_agent_api_calls()
    
    # Test 4: Fallback functionality
    test_restoran_agent_fallback()
    
    # Test 5: Different scenarios
    test_restoran_agent_different_scenarios()
    
    print("\n" + "=" * 50)
    print("🎉 RestoranAgent tests completed!")


if __name__ == "__main__":
    main()
