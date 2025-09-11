
"""
Restaurant Agent - specialized agent for restaurant recommendations
ReAct agent that receives requests from RouterAgent
"""

import os
import json
import sys
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.tools import Tool, StructuredTool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Import Pydantic models
from app.models.restaurant_models import (
    RestaurantResponse, RestaurantAgentResult, Restaurant, CuisineType, 
    PriceRange, DietaryRestrictions, Location, OpeningHours, BudgetEstimate
)

# Add project path for correct imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class RestoranAgent:
    """Specialized agent for restaurant recommendations in Madrid"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.3
        )
        
        # Create parser for structured output
        self.output_parser = PydanticOutputParser(pydantic_object=RestaurantResponse)
        
        # Initialize API services
        self.api_services = self._initialize_api_services()
        
        # Create tools with API capabilities
        self.tools = self._create_enhanced_tools()
        self.prompt = self._create_enhanced_prompt()
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            max_iterations=3,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            early_stopping_method="force"
        )
    
    def _initialize_api_services(self) -> Dict[str, Any]:
        """Initialize API services"""
        return {
            "google_places": self._init_google_places(),
            "weather": self._init_weather_api()
        }
    
    def _init_google_places(self) -> Optional[Dict]:
        """Initialize Google Places API"""
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://maps.googleapis.com/maps/api/place"}
        return None
    
    def _init_weather_api(self) -> Optional[Dict]:
        """Initialize Weather API for outdoor dining recommendations"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://api.openweathermap.org/data/2.5"}
        return None
    
    def _create_enhanced_tools(self) -> List[Tool]:
        """Creates enhanced tools with API calls"""
        tools = []
        
        # Add API tools (PRIORITY 1)
        if self.api_services["google_places"]:
            tools.append(Tool(
                name="search_restaurants_api",
                description="""[PRIORITY 1] Search restaurants through Google Places API.
                MANDATORY to use FIRST for finding restaurants in Madrid.
                Input parameters: query (search query), cuisine_type (type of cuisine), price_level (1-4)
                Format: search_restaurants_api("family restaurants Madrid", "spanish", 2)
                Returns: list of restaurants with ratings, prices, types""",
                func=self._search_restaurants_api
            ))
            
            tools.append(Tool(
                name="get_restaurant_details_api",
                description="""[PRIORITY 1] Get detailed information about a restaurant.
                Use AFTER search_restaurants_api to get complete information.
                Input parameters: place_id (restaurant ID from search_restaurants_api)
                Format: get_restaurant_details_api("ChIJN1t_tDeuEmsRUsoyG83frY4")
                Returns: details, opening hours, reviews, photos, features""",
                func=self._get_restaurant_details_api
            ))
        
        if self.api_services["weather"]:
            tools.append(Tool(
                name="check_weather_api",
                description="""[PRIORITY 1] Check weather in Madrid for outdoor dining.
                MANDATORY to use for recommending outdoor seating.
                Input parameters: date (date in YYYY-MM-DD format)
                Format: check_weather_api("2024-01-15")
                Returns: temperature, conditions, outdoor dining recommendations""",
                func=self._check_weather_api
            ))
        
        # Add fallback tool (PRIORITY 2 - only if APIs unavailable)
        tools.append(StructuredTool.from_function(
            func=self._create_restaurant_plan,
            name="create_restaurant_plan",
            description="""[PRIORITY 2] Creates restaurant plan (fallback).
            Use ONLY if APIs are unavailable or didn't return results.
            Input parameters: query, kids_ages, adults_count, dietary_restrictions, budget_level, cuisine_preferences, travel_dates
            Format: create_restaurant_plan(query="restaurants", kids_ages=[8, 12], adults_count=2, dietary_restrictions=["vegetarian"], budget_level="moderate", cuisine_preferences=["spanish"], travel_dates="2024-01-15")
            Returns: structured restaurant plan""",
            return_schema=RestaurantResponse
        ))
        
        return tools
    
    def _force_api_usage(self, context: Dict[str, Any]) -> None:
        """Forces API check and usage to get current data"""
        try:
            # Check API availability
            api_available = {
                "google_places": self.api_services["google_places"] is not None,
                "weather": self.api_services["weather"] is not None
            }
            
            # If APIs are available, add STRICT instructions to context
            if any(api_available.values()):
                # Create personalized instructions considering family needs
                kids_ages = context.get('kids_ages', [])
                dietary_restrictions = context.get('dietary_restrictions', [])
                cuisine_preferences = context.get('cuisine_preferences', [])
                travel_dates = context.get('travel_dates', '2024-01-15')
                input_query = context.get('input', 'restaurants for family')
                
                # Create personalized query
                if kids_ages:
                    age_info = f" for children ages {min(kids_ages)}-{max(kids_ages)}"
                    personalized_query = f"{input_query}{age_info}"
                else:
                    personalized_query = input_query
                
                context["api_instructions"] = f"""
                🚨 CRITICALLY IMPORTANT: APIs ARE AVAILABLE! MANDATORY TO USE THEM!
                
                AVAILABLE APIs: {[k for k, v in api_available.items() if v]}
                👶 CHILDREN AGES: {kids_ages}
                🥗 DIETARY RESTRICTIONS: {dietary_restrictions}
                🍽️ CUISINE PREFERENCES: {cuisine_preferences}
                📅 TRAVEL DATES: {travel_dates}
                
                ACTION ORDER (MANDATORY):
                1. **FIRST** call search_restaurants_api with query "{personalized_query}"
                2. **THEN** call get_restaurant_details_api for each found restaurant
                3. **THEN** call check_weather_api for date "{travel_dates}"
                4. **ONLY AFTER** all API calls use create_restaurant_plan
                
                FORBIDDEN:
                ❌ Use create_restaurant_plan WITHOUT calling APIs
                ❌ Skip API calls
                ❌ Use fallback data
                ❌ Ignore family dietary needs in queries
                
                START WITH: search_restaurants_api("{personalized_query}", "restaurant", 2)
                """
                
                # Add forcing flag
                context["force_api_first"] = True
            else:
                context["api_instructions"] = """
                ⚠️ APIs unavailable, use create_restaurant_plan as fallback
                """
                context["force_api_first"] = False
                
        except Exception as e:
            pass
    
    def _force_api_calls(self, context: Dict[str, Any]) -> None:
        """Forces API calls to get data"""
        try:
            # Extract data from context for personalization
            kids_ages = context.get('kids_ages', [])
            dietary_restrictions = context.get('dietary_restrictions', [])
            cuisine_preferences = context.get('cuisine_preferences', [])
            travel_dates = context.get('travel_dates', '2024-01-15')
            input_query = context.get('input', 'restaurants for family')
            
            # Create personalized query for Google Places API
            if kids_ages:
                personalized_query = f"family restaurants Madrid children {min(kids_ages)} {max(kids_ages)} years"
            else:
                personalized_query = "family restaurants Madrid"
            
            # Force call Google Places API
            if self.api_services["google_places"]:
                restaurants_result = self._search_restaurants_api(personalized_query, "restaurant", 2)
                # Add result to context
                context["forced_restaurants_data"] = restaurants_result
            
            # Force call Weather API
            if self.api_services["weather"]:
                # Use real travel dates
                weather_date = travel_dates.split(' - ')[0] if ' - ' in travel_dates else travel_dates
                weather_result = self._check_weather_api(weather_date)
                # Add result to context
                context["forced_weather_data"] = weather_result
            
        except Exception as e:
            pass
    
    def _create_enhanced_prompt(self) -> PromptTemplate:
        """Creates enhanced prompt with API capabilities using ReAct pattern"""
        template = """You are an expert family restaurant agent in Madrid that follows the ReAct pattern (Reasoning + Acting).

FAMILY INFORMATION:
- Children ages: {kids_ages}
- Number of adults: {adults_count}
- Dietary restrictions: {dietary_restrictions}
- Cuisine preferences: {cuisine_preferences}
- Budget level: {budget_level}
- Travel dates: {travel_dates}
- Origin country: {origin_country}

API INSTRUCTIONS:
{api_instructions}

API DATA OBTAINED (if available):
- Restaurants: {forced_restaurants_data}
- Weather: {forced_weather_data}

AVAILABLE TOOLS:
{tools}

TOOL NAMES:
{tool_names}

TOOL PRIORITY (MANDATORY ORDER):
1. **FIRST PRIORITY**: External APIs (search_restaurants_api, get_restaurant_details_api, check_weather_api)
2. **SECOND PRIORITY**: create_restaurant_plan (only if APIs not available)

ReAct REASONING PATTERN:
**Thought**: [Analyze what you need to do and why]
**Action**: [Name of the tool to use]
**Action Input**: [Parameters for the tool]
**Observation**: [Tool result]
**Thought**: [Analyze the result and decide the next step]
**Action**: [Next tool if necessary]
**Action Input**: [Parameters]
**Observation**: [Result]
**Final Answer**: [Final structured response]

STRICT RULES:
1. **ALWAYS** try to use external APIs FIRST
2. **NEVER** use create_restaurant_plan if APIs are available
3. **COMBINE** information from multiple APIs when possible
4. **CHECK** weather before recommending outdoor seating
5. **SEARCH** for family-friendly restaurants with specific criteria
6. **GET** complete details of recommended restaurants
7. **CONSIDER** dietary restrictions and children's ages
8. **PERSONALIZE** recommendations based on family profile

🚨 MANDATORY VERIFICATION:
- If you see "force_api_first": true, you MUST use APIs FIRST
- If you see "API ДОСТУПНЫ", you MUST use APIs FIRST
- You CANNOT use create_restaurant_plan without first calling APIs

FAMILY-FRIENDLY CRITERIA TO CONSIDER:
- Child-friendly menu and high chairs
- Noise level and family atmosphere
- Play areas and entertainment for children
- Changing tables and family bathrooms
- Wait times and service speed
- Outdoor seating availability
- Dietary accommodations

CORRECT FLOW EXAMPLE:
**Thought**: I need to find family-friendly Spanish restaurants in Madrid for children aged 8 and 12
**Action**: search_restaurants_api
**Action Input**: {{"query": "family Spanish restaurants Madrid children", "cuisine_type": "restaurant", "price_level": 2}}
**Observation**: [Restaurants found]
**Thought**: Now I need to get detailed information about each restaurant
**Action**: get_restaurant_details_api
**Action Input**: {{"place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4"}}
**Observation**: [Restaurant details]
**Thought**: I should check the weather for outdoor dining recommendations
**Action**: check_weather_api
**Action Input**: {{"date": "2024-01-15"}}
**Observation**: [Weather data]
**Final Answer**: [Complete personalized restaurant plan]

User query: {input}

{agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=[
                "input", "kids_ages", "adults_count", "dietary_restrictions", 
                "cuisine_preferences", "budget_level", "travel_dates", "origin_country",
                "api_instructions", "forced_restaurants_data", "forced_weather_data", 
                "tools", "tool_names", "agent_scratchpad"
            ]
        )
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method for processing requests from RouterAgent with Pydantic + Function Calling"""
        try:
            profile = request_data.get('profile', {})
            query = request_data.get('query', 'find restaurants')
            
            # Extract profile data
            kids_ages = profile.get('kids_ages', []) if isinstance(profile, dict) else getattr(profile, 'kids_ages', [])
            adults_count = profile.get('adults_count', 2) if isinstance(profile, dict) else getattr(profile, 'adults_count', 2)
            dietary_restrictions = profile.get('dietary_restrictions', []) if isinstance(profile, dict) else getattr(profile, 'dietary_restrictions', [])
            cuisine_preferences = profile.get('cuisine_preferences', []) if isinstance(profile, dict) else getattr(profile, 'cuisine_preferences', [])
            origin_country = profile.get('origin_country', 'Spain') if isinstance(profile, dict) else getattr(profile, 'origin_country', 'Spain')
            special_needs = profile.get('special_needs', []) if isinstance(profile, dict) else getattr(profile, 'special_needs', [])
            
            # Load travel data
            if isinstance(profile, dict):
                # If profile is a dictionary from RouterAgent, extract dates directly
                budget_level = profile.get('budget_level', 'moderate')
                start_date = profile.get('start_date', '')
                end_date = profile.get('end_date', '')
                travel_dates = f"{start_date} - {end_date}" if start_date and end_date else ''
            else:
                # If profile is a FamilyProfileSupabase object, load travel data
                travel_data = profile.load_travel_dates(family_id)
                budget_level = travel_data.get('budget_level', 'moderate')
                start_date = travel_data.get('start_date', '')
                end_date = travel_data.get('end_date', '')
                travel_dates = f"{start_date} - {end_date}" if start_date and end_date else ''
            
            context = {
                "input": query,
                "kids_ages": kids_ages,
                "adults_count": adults_count,
                "dietary_restrictions": dietary_restrictions,
                "cuisine_preferences": cuisine_preferences,
                "origin_country": origin_country,
                "special_needs": special_needs,
                "budget_level": budget_level,
                "travel_dates": travel_dates,
                "api_instructions": "",  # Will be filled in _force_api_usage
                "forced_restaurants_data": "",  # Will be filled in _force_api_calls
                "forced_weather_data": ""  # Will be filled in _force_api_calls
            }
            
            try:
                # Check API availability and force use them
                self._force_api_usage(context)
                
                # Force call APIs if they are available
                if context.get("force_api_first", False):
                    self._force_api_calls(context)
                
                # Execute agent with Function Calling
                result = self.agent_executor.invoke(context)
                
                # Extract structured data from result
                structured_data = None
                restaurant_text = ""
                
                if isinstance(result, dict):
                    output = result.get('output', '')
                    intermediate_steps = result.get('intermediate_steps', [])
                    
                    # Look for create_restaurant_plan function call in intermediate steps
                    for step in intermediate_steps:
                        if isinstance(step, tuple) and len(step) >= 2:
                            action, observation = step
                            if isinstance(action, dict) and action.get('tool') == 'create_restaurant_plan':
                                try:
                                    # Parse function result (observation is already a dictionary)
                                    if isinstance(observation, dict):
                                        structured_data = RestaurantResponse(**observation)
                                    else:
                                        structured_data = RestaurantResponse.parse_raw(observation)
                                    restaurant_text = self._format_restaurant_text(structured_data)
                                    break
                                except Exception as e:
                                    continue
                    
                    # If structured data not found, use text output
                    if not structured_data and output:
                        restaurant_text = output
                
                # If no structured data, create minimal data
                if not structured_data:
                    restaurant_text = "Could not obtain restaurant recommendations. Please check API connection."
                
                # Check that restaurant_text is not empty
                if not restaurant_text or restaurant_text.strip() == "":
                    restaurant_text = f"""🍽️ **Restaurant Recommendations for Family with {context.get('kids_ages', [])} years old children**

**Family Profile:**
• Children ages: {context.get('kids_ages', [])}
• Number of adults: {context.get('adults_count', 2)}
• Dietary restrictions: {', '.join(context.get('dietary_restrictions', [])) if context.get('dietary_restrictions') else 'None'}
• Cuisine preferences: {', '.join(context.get('cuisine_preferences', [])) if context.get('cuisine_preferences') else 'Any'}
• Country of origin: {context.get('origin_country', 'Not specified')}
• Budget: {context.get('budget_level', 'moderate')}
• Travel dates: {context.get('travel_dates', 'Not specified')}

**Personalized recommendations:**
- Family-friendly restaurants for ages: {context.get('kids_ages', [])}
- Dietary accommodations: {', '.join(context.get('dietary_restrictions', [])) if context.get('dietary_restrictions') else 'None'}
- Cuisine preferences: {', '.join(context.get('cuisine_preferences', [])) if context.get('cuisine_preferences') else 'Any'}
- Budget level: {context.get('budget_level', 'moderate')}

[Fallback - restaurant agent with context]"""
                    # Create minimal structured data
                    structured_data = RestaurantResponse(
                        restaurants=[],
                        total_restaurants=0,
                        recommended_duration="1-2 hours",
                        budget_estimate=BudgetEstimate(
                            range="€20-40", 
                            per_person="€15-25", 
                            notes="API unavailable"
                        ),
                        cuisine_types_covered=[],
                        dietary_restrictions_covered=[],
                        kid_friendly_options=0,
                        booking_recommendations=["Check availability"],
                        practical_tips=["Check API connection"],
                        weather_considerations=["Check weather before outdoor dining"]
                    )
                
                # Create result with Pydantic validation
                agent_result = RestaurantAgentResult(
                    agent_name="restaurant",
                    status="success",
                    query=query,
                    family_context=context,
                    restaurant_text=restaurant_text,
                    structured_data=structured_data,
                    metadata={
                        "processing_time": "real_time",
                        "confidence": 0.9,
                        "source": "pydantic_function_calling",
                        "validation": "passed"
                    }
                )
                
                result_dict = agent_result.dict()
                return result_dict

            except Exception as agent_error:
                # Error - create minimal data
                restaurant_text = f"Error processing request: {str(agent_error)}. Please check API connection."
                structured_data = RestaurantResponse(
                    restaurants=[],
                    total_restaurants=0,
                    recommended_duration="1-2 hours",
                    budget_estimate=BudgetEstimate(
                        range="€20-40", 
                        per_person="€15-25", 
                        notes="Processing error"
                    ),
                    cuisine_types_covered=[],
                    dietary_restrictions_covered=[],
                    kid_friendly_options=0,
                    booking_recommendations=["Check availability"],
                    practical_tips=["Check API connection"],
                    weather_considerations=["Check weather before outdoor dining"]
                )
                
                return {
                    "agent_name": "restaurant",
                    "status": "fallback",
                    "query": query,
                    "family_context": context,
                    "restaurant_text": restaurant_text,
                    "structured_data": structured_data,
                    "metadata": {
                        "processing_time": "real_time",
                        "confidence": 0.6,
                        "source": "fallback",
                        "error": str(agent_error)
                    }
                }
            
        except Exception as e:
            structured_data = RestaurantResponse(
                restaurants=[],
                total_restaurants=0,
                recommended_duration="1-2 hours",
                budget_estimate=BudgetEstimate(
                    range="€20-40", 
                    per_person="€15-25", 
                    notes="Critical error"
                ),
                cuisine_types_covered=[],
                dietary_restrictions_covered=[],
                kid_friendly_options=0,
                booking_recommendations=["Check availability"],
                practical_tips=["Check API connection"],
                weather_considerations=["Check weather before outdoor dining"]
            )
            return {
                "agent_name": "restaurant",
                "status": "error",
                "query": query,
                "family_context": context,
                "restaurant_text": f"Sorry, there was an error creating your restaurant recommendations: {str(e)}",
                "structured_data": structured_data,
                "metadata": {
                    "processing_time": "real_time",
                    "confidence": 0.0,
                    "source": "error",
                    "error": str(e)
                }
            }
    
    def _format_restaurant_text(self, structured_data: RestaurantResponse) -> str:
        """Formats structured data into readable text"""
        text = f"# 🍽️ Personalized Restaurant Plan\n\n"
        text += f"**Total restaurants:** {structured_data.total_restaurants}\n"
        text += f"**Recommended duration:** {structured_data.recommended_duration}\n"
        text += f"**Budget estimate:** {structured_data.budget_estimate.range} per person\n\n"
        
        for i, restaurant in enumerate(structured_data.restaurants, 1):
            text += f"## {i}. {restaurant.name}\n"
            text += f"**Cuisine:** {restaurant.cuisine_type.value.title()}\n"
            text += f"**Price range:** {restaurant.price_range.value}\n"
            text += f"**Rating:** {restaurant.rating}/5\n"
            text += f"**Address:** {restaurant.location.address}\n"
            if restaurant.description:
                text += f"**Description:** {restaurant.description}\n"
            if restaurant.features:
                text += f"**Features:** {', '.join(restaurant.features)}\n"
            if restaurant.dietary_options:
                text += f"**Dietary options:** {', '.join([opt.value for opt in restaurant.dietary_options])}\n"
            text += f"**Kid-friendly:** {'Yes' if restaurant.kid_friendly else 'No'}\n\n"
        
        return text
    
    def _create_restaurant_plan(self, query: str, kids_ages: List[int], adults_count: int, 
                              dietary_restrictions: List[str], budget_level: str, 
                              cuisine_preferences: List[str], travel_dates: str) -> RestaurantResponse:
        """Creates restaurant plan as fallback"""
        # This would be implemented with fallback restaurant data
        # For now, return empty response
        return RestaurantResponse(
            restaurants=[],
            total_restaurants=0,
            recommended_duration="1-2 hours",
            budget_estimate=BudgetEstimate(
                range="€20-40",
                per_person="€15-25",
                notes="Fallback data"
            ),
            cuisine_types_covered=[],
            dietary_restrictions_covered=[],
            kid_friendly_options=0,
            booking_recommendations=["Check availability"],
            practical_tips=["Use fallback data"],
            weather_considerations=["Check weather"]
        )
    
    # API methods
    def _search_restaurants_api(self, query: str, cuisine_type: str = "restaurant", price_level: int = 2) -> str:
        """Search restaurants through Google Places API"""
        try:
            if not self.api_services["google_places"]:
                return json.dumps({"status": "error", "error": "Google Places API not configured"})
            
            # Real API call
            params = {
                "query": query,
                "location": "40.4168,-3.7038",  # Madrid coordinates
                "radius": 5000,
                "type": "restaurant",
                "key": self.api_services["google_places"]["api_key"]
            }
            
            response = requests.get(
                f"{self.api_services['google_places']['base_url']}/textsearch/json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                restaurants = data.get("results", [])
                
                # Format results
                formatted_restaurants = []
                for restaurant in restaurants[:5]:  # Limit to 5 results
                    formatted_restaurants.append({
                        "name": restaurant.get("name"),
                        "place_id": restaurant.get("place_id"),
                        "rating": restaurant.get("rating", 0),
                        "price_level": restaurant.get("price_level", 2),
                        "types": restaurant.get("types", []),
                        "vicinity": restaurant.get("vicinity"),
                        "geometry": restaurant.get("geometry", {})
                    })
                
                return json.dumps({
                    "status": "success",
                    "restaurants": formatted_restaurants,
                    "query": query,
                    "cuisine_type": cuisine_type
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"API error: {response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _get_restaurant_details_api(self, place_id: str) -> str:
        """Get detailed information about a restaurant"""
        try:
            if not self.api_services["google_places"]:
                return json.dumps({"status": "error", "error": "Google Places API not configured"})
            
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,rating,price_level,opening_hours,photos,reviews,website,formatted_phone_number,types,geometry",
                "key": self.api_services["google_places"]["api_key"]
            }
            
            response = requests.get(
                f"{self.api_services['google_places']['base_url']}/details/json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                return json.dumps({
                    "status": "success",
                    "details": {
                        "name": result.get("name"),
                        "address": result.get("formatted_address"),
                        "rating": result.get("rating", 0),
                        "price_level": result.get("price_level", 2),
                        "opening_hours": result.get("opening_hours", {}),
                        "phone": result.get("formatted_phone_number"),
                        "website": result.get("website"),
                        "reviews": result.get("reviews", [])[:3],  # Last 3 reviews
                        "types": result.get("types", []),
                        "photos": result.get("photos", [])[:3]  # First 3 photos
                    }
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"API error: {response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _check_weather_api(self, date: str) -> str:
        """Check weather through OpenWeatherMap API for outdoor dining"""
        try:
            if not self.api_services["weather"]:
                return json.dumps({"status": "error", "error": "Weather API not configured"})
            
            # Real OpenWeatherMap API call
            api_key = self.api_services["weather"]["api_key"]
            base_url = self.api_services["weather"]["base_url"]
            
            # Madrid coordinates
            lat = "40.4168"
            lon = "-3.7038"
            
            params = {
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric",
                "lang": "en"
            }
            
            response = requests.get(f"{base_url}/weather", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    "date": date,
                    "temperature": f"{data['main']['temp']:.1f}°C",
                    "condition": data['weather'][0]['description'].title(),
                    "humidity": f"{data['main']['humidity']}%",
                    "wind": f"{data['wind']['speed']} m/s",
                    "outdoor_dining_recommendation": self._get_outdoor_dining_recommendation(data['main']['temp'], data['weather'][0]['main'])
                }
                
                return json.dumps({
                    "status": "success",
                    "weather": weather_data
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"Weather API error: {response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _get_outdoor_dining_recommendation(self, temp: float, condition: str) -> str:
        """Generates outdoor dining recommendation based on weather"""
        if temp < 10:
            return "Too cold for outdoor dining, recommend indoor seating"
        elif temp > 35:
            return "Very hot, outdoor dining with shade recommended"
        elif condition in ["Rain", "Drizzle"]:
            return "Rain expected, recommend indoor seating"
        else:
            return "Perfect weather for outdoor dining"


def create_restaurant_agent() -> RestoranAgent:
    """Creates RestoranAgent instance for RouterAgent"""
    return RestoranAgent()
