
"""
Activities Agent - specialized agent for entertainment planning
React agent that receives requests from RouterAgent
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
from app.models.activities_models import ActivitiesResponse, ActivitiesAgentResult
from app.tools.activities_tools import create_activities_plan

# Add project path for correct imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class ActivitiesAgent:
    """Specialized agent for entertainment planning in Madrid"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=0.3
        )
        
       
        
        # Create parser for structured output
        self.output_parser = PydanticOutputParser(pydantic_object=ActivitiesResponse)
        
        # Add API services
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
            max_iterations=2,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            early_stopping_method="force"
        )
        
    
   
    
    def _initialize_api_services(self) -> Dict[str, Any]:
        """Initialize API services"""
        return {
            "google_places": self._init_google_places(),
            "weather": self._init_weather_api(),
            "events": self._init_events_api()
        }
    
    def _init_google_places(self) -> Optional[Dict]:
        """Инициализирует Google Places API"""
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://maps.googleapis.com/maps/api/place"}
        return None
    
    def _init_weather_api(self) -> Optional[Dict]:
        """Инициализирует Weather API"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://api.openweathermap.org/data/2.5"}
        return None
    
    def _init_events_api(self) -> Optional[Dict]:
        """Инициализирует Events API"""
        api_key = os.getenv("EVENTBRITE_API_KEY")
        if api_key:
            return {"api_key": api_key, "base_url": "https://www.eventbriteapi.com/v3"}
        return None
    
    def _create_enhanced_tools(self) -> List[Tool]:
        """Creates enhanced tools with API calls"""
        tools = []
        
        # Add API tools (PRIORITY 1)
        if self.api_services["google_places"]:
            tools.append(Tool(
                name="search_places_api",
                description="""[PRIORITY 1] Search places through Google Places API.
                MANDATORY to use FIRST for finding places in Madrid.
                Input parameters: query (search query), place_type (place type)
                Format: search_places_api("museos para niños", "museum")
                Returns: list of places with ratings, prices, types""",
                func=self._search_places_api
            ))
            
            tools.append(Tool(
                name="get_place_details_api",
                description="""[PRIORITY 1] Get detailed information about a place.
                Use AFTER search_places_api to get complete information.
                Input parameters: place_id (place ID from search_places_api)
                Format: get_place_details_api("ChIJN1t_tDeuEmsRUsoyG83frY4")
                Returns: details, opening hours, reviews, contacts""",
                func=self._get_place_details_api
            ))
        
        if self.api_services["weather"]:
            tools.append(Tool(
                name="check_weather_api",
                description="""[PRIORITY 1] Check weather in Madrid.
                MANDATORY to use for recommending outdoor activities.
                Input parameters: date (date in YYYY-MM-DD format)
                Format: check_weather_api("2024-01-15")
                Returns: temperature, conditions, recommendations""",
                func=self._check_weather_api
            ))
        
        if self.api_services["events"]:
            tools.append(Tool(
                name="search_events_api",
                description="""[PRIORITY 1] Search events and activities.
                Use for finding temporary events and activities.
                Input parameters: query (search query), date (date)
                Format: search_events_api("talleres niños", "2024-01-15")
                Returns: events with dates, times, prices""",
                func=self._search_events_api
            ))
        
        # Add fallback tool (PRIORITY 2 - only if APIs unavailable)
        tools.append(StructuredTool.from_function(
            func=create_activities_plan,
            name="create_activities_plan",
            description="""[PRIORITY 2] Creates activities plan (fallback).
            Use ONLY if APIs are unavailable or didn't return results.
            Input parameters: query, kids_ages, adults_count, interests, budget_level, special_needs, origin_country, travel_dates
            Format: create_activities_plan(query="actividades", kids_ages=[8, 12], adults_count=2, interests=["arte"], budget_level="medium", special_needs=[], origin_country="Spain", travel_dates="2024-01-15")
            Returns: structured activities plan""",
            return_schema=ActivitiesResponse
        ))
        
        return tools
    
    def _force_api_usage(self, context: Dict[str, Any]) -> None:
        """Forces API check and usage to get current data"""
        try:
            # Check API availability
            api_available = {
                "google_places": self.api_services["google_places"] is not None,
                "weather": self.api_services["weather"] is not None,
                "events": self.api_services["events"] is not None
            }
            
            # If APIs are available, add STRICT instructions to context
            if any(api_available.values()):
                # Create personalized instructions considering children's age
                kids_ages = context.get('kids_ages', [])
                travel_dates = context.get('travel_dates', '2024-01-15')
                input_query = context.get('input', 'actividades para niños')
                
                if kids_ages:
                    age_info = f" para niños de {min(kids_ages)}-{max(kids_ages)} años"
                    personalized_query = f"{input_query}{age_info}"
                else:
                    personalized_query = input_query
                
                context["api_instructions"] = f"""
                🚨 CRITICALLY IMPORTANT: APIs ARE AVAILABLE! MANDATORY TO USE THEM!
                
                AVAILABLE APIs: {[k for k, v in api_available.items() if v]}
                👶 CHILDREN AGES: {kids_ages}
                📅 TRAVEL DATES: {travel_dates}
                
                ACTION ORDER (MANDATORY):
                1. **FIRST** call search_places_api with query "{personalized_query}"
                2. **THEN** call check_weather_api for date "{travel_dates}"
                3. **THEN** call search_events_api to search for events considering age
                4. **ONLY AFTER** all API calls use create_activities_plan
                
                FORBIDDEN:
                ❌ Use create_activities_plan WITHOUT calling APIs
                ❌ Skip API calls
                ❌ Use fallback data
                ❌ Ignore children's age in queries
                
                START WITH: search_places_api("{personalized_query}", "amusement_park|museum|park|zoo")
                """
                
                # Add forcing flag
                context["force_api_first"] = True
            else:
                context["api_instructions"] = """
                ⚠️ APIs unavailable, use create_activities_plan as fallback
                """
                context["force_api_first"] = False
                
        except Exception as e:
            pass
    
    def _force_api_calls(self, context: Dict[str, Any]) -> None:
        """Forces API calls to get data"""
        try:
            # Extract data from context for personalization
            kids_ages = context.get('kids_ages', [])
            travel_dates = context.get('travel_dates', '2024-01-15')
            input_query = context.get('input', 'actividades para niños')
            
            # Create simple query for Google Places API
            if kids_ages:
                # Simplify query for better API understanding
                personalized_query = f"actividades niños Madrid {min(kids_ages)} {max(kids_ages)} años"
            else:
                personalized_query = "actividades niños Madrid"
            
            # Force call Google Places API
            if self.api_services["google_places"]:
                places_result = self._search_places_api(personalized_query, "amusement_park|museum|park|zoo")
                # Add result to context
                context["forced_places_data"] = places_result
            
            # Force call Weather API
            if self.api_services["weather"]:
                # Use real travel dates
                weather_date = travel_dates.split(' - ')[0] if ' - ' in travel_dates else travel_dates
                weather_result = self._check_weather_api(weather_date)
                # Add result to context
                context["forced_weather_data"] = weather_result
            
            # Force call Events API
            if self.api_services["events"]:
                # Create query considering children's age
                if kids_ages:
                    events_query = f"talleres niños Madrid {min(kids_ages)} {max(kids_ages)} años"
                else:
                    events_query = "talleres niños Madrid"
                events_result = self._search_events_api(events_query, weather_date)
                # Add result to context
                context["forced_events_data"] = events_result
            
        except Exception as e:
            pass
    
    def _create_enhanced_prompt(self) -> PromptTemplate:
        """Creates enhanced prompt with API capabilities using ReAct pattern"""
        template = """You are an expert family activities agent in Madrid that follows the ReAct pattern (Reasoning + Acting).

FAMILY INFORMATION:
- Children ages: {kids_ages}
- Number of adults: {adults_count}
- Interests: {interests}
- Budget: {budget_level}
- Travel dates: {travel_dates}

API INSTRUCTIONS:
{api_instructions}

API DATA OBTAINED (if available):
- Places: {forced_places_data}
- Weather: {forced_weather_data}
- Events: {forced_events_data}

AVAILABLE TOOLS:
{tools}

TOOL NAMES:
{tool_names}

TOOL PRIORITY (MANDATORY ORDER):
1. **FIRST PRIORITY**: External APIs (search_places_api, get_place_details_api, check_weather_api, search_events_api)
2. **SECOND PRIORITY**: create_activities_plan (only if APIs not available)

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
2. **NEVER** use create_activities_plan if APIs are available
3. **COMBINE** information from multiple APIs when possible
4. **CHECK** weather before recommending outdoor activities
5. **SEARCH** for specific events for travel dates
6. **GET** complete details of recommended places

🚨 MANDATORY VERIFICATION:
- If you see "force_api_first": true, you MUST use APIs FIRST
- If you see "API ДОСТУПНЫ", you MUST use APIs FIRST
- You CANNOT use create_activities_plan without first calling APIs

CORRECT FLOW EXAMPLE:
**Thought**: I need to find museums for 8-year-old children in Madrid
**Action**: search_places_api
**Action Input**: {{"query": "museos para niños Madrid", "place_type": "museum"}}
**Observation**: [API result]
**Thought**: Now I need to check the weather to recommend activities
**Action**: check_weather_api
**Action Input**: {{"date": "2024-01-15"}}
**Observation**: [Weather data]
**Thought**: I'll search for special events for that date
**Action**: search_events_api
**Action Input**: {{"query": "talleres niños", "date": "2024-01-15"}}
**Observation**: [Events found]
**Final Answer**: [Complete plan based on real data]

User query: {input}

{agent_scratchpad}"""

        return PromptTemplate(
            template=template,
            input_variables=[
                "input", "kids_ages", "adults_count", "interests", 
                "budget_level", "travel_dates", "api_instructions", "forced_places_data", 
                "forced_weather_data", "forced_events_data", "tools", "tool_names", "agent_scratchpad"
            ]
        )
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method for processing requests from RouterAgent with Pydantic + Function Calling"""
        try:
            profile = request_data.get('profile', {})
            query = request_data.get('query', 'planificar actividades')
            
            # Extract profile data
            kids_ages = profile.get('kids_ages', []) if isinstance(profile, dict) else getattr(profile, 'kids_ages', [])
            adults_count = profile.get('adults_count', 2) if isinstance(profile, dict) else getattr(profile, 'adults_count', 2)
            interests = profile.get('interests', []) if isinstance(profile, dict) else getattr(profile, 'interests', [])
            origin_country = profile.get('origin_country', 'Spain') if isinstance(profile, dict) else getattr(profile, 'origin_country', 'Spain')
            special_needs = profile.get('special_needs', []) if isinstance(profile, dict) else getattr(profile, 'special_needs', [])
            # Load travel data
            if isinstance(profile, dict):
                # If profile is a dictionary from RouterAgent, extract dates directly
                budget_level = profile.get('budget_level', 'medium')
                start_date = profile.get('start_date', '')
                end_date = profile.get('end_date', '')
                travel_dates = f"{start_date} - {end_date}" if start_date and end_date else ''
            else:
                # If profile is a FamilyProfileSupabase object, load travel data
                travel_data = profile.load_travel_dates(family_id)
                budget_level = travel_data.get('budget_level', 'medium')
                start_date = travel_data.get('start_date', '')
                end_date = travel_data.get('end_date', '')
                travel_dates = f"{start_date} - {end_date}" if start_date and end_date else ''
            
            context = {
                "input": query,
                "kids_ages": kids_ages,
                "adults_count": adults_count,
                "interests": interests,
                "origin_country": origin_country,
                "special_needs": special_needs,
                "budget_level": budget_level,
                "travel_dates": travel_dates,
                "api_instructions": "",  # Will be filled in _force_api_usage
                "forced_places_data": "",  # Will be filled in _force_api_calls
                "forced_weather_data": "",  # Will be filled in _force_api_calls
                "forced_events_data": ""  # Will be filled in _force_api_calls
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
                activities_text = ""
                
                if isinstance(result, dict):
                    output = result.get('output', '')
                    intermediate_steps = result.get('intermediate_steps', [])
                    
                    # Look for create_activities_plan function call in intermediate steps
                    for step in intermediate_steps:
                        if isinstance(step, tuple) and len(step) >= 2:
                            action, observation = step
                            if isinstance(action, dict) and action.get('tool') == 'create_activities_plan':
                                try:
                                    # Parse function result (observation is already a dictionary)
                                    if isinstance(observation, dict):
                                        structured_data = ActivitiesResponse(**observation)
                                    else:
                                        structured_data = ActivitiesResponse.parse_raw(observation)
                                    activities_text = self._format_activities_text(structured_data)
                                    break
                                except Exception as e:
                                    continue
                    
                    # If structured data not found, use text output
                    if not structured_data and output:
                        activities_text = output
                
                # If no structured data, create minimal data
                if not structured_data:
                    activities_text = "Could not obtain activities. Please check API connection."
                
                # Check that activities_text is not empty
                if not activities_text or activities_text.strip() == "":
                    activities_text = f"""🎯 **Activity Recommendations for {context.get('kids_ages', [])} years old**

**Family Profile:**
• Children ages: {context.get('kids_ages', [])}
• Number of adults: {context.get('adults_count', 2)}
• Interests: {', '.join(context.get('interests', [])) if context.get('interests') else 'Not specified'}
• Country of origin: {context.get('origin_country', 'Not specified')}
• Budget: {context.get('budget_level', 'medium')}
• Travel dates: {context.get('travel_dates', 'Not specified')}

**Personalized recommendations:**
- Age-appropriate activities: {context.get('kids_ages', [])}
- Interests: {', '.join(context.get('interests', [])) if context.get('interests') else 'Not specified'}
- Special needs: {', '.join(context.get('special_needs', [])) if context.get('special_needs') else 'None'}
- Budget: {context.get('budget_level', 'medium')}

[Fallback - activities agent with context]"""
                    # Create minimal structured data
                    from app.models.activities_models import BudgetEstimate
                    structured_data = ActivitiesResponse(
                        activities=[],
                        total_activities=0,
                        recommended_duration="1 día",
                        budget_estimate=BudgetEstimate(
                            range="€0-50", 
                            per_person="€10-25", 
                            notes="API unavailable"
                        ),
                        age_groups=self._get_age_groups(context.get('kids_ages', [])),
                        interests_covered=[],
                        weather_considerations=["Check weather before going out"],
                        practical_tips=["Check API connection"]
                    )
                
                # Create result with Pydantic validation
                agent_result = ActivitiesAgentResult(
                    agent_name="activities",
                    status="success",
                    query=query,
                    family_context=context,
                    activities_text=activities_text,
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
                activities_text = f"Error processing request: {str(agent_error)}. Please check API connection."
                from app.models.activities_models import BudgetEstimate
                structured_data = ActivitiesResponse(
                    activities=[],
                    total_activities=0,
                    recommended_duration="1 día",
                    budget_estimate=BudgetEstimate(
                        range="€0-50", 
                        per_person="€10-25", 
                        notes="Processing error"
                    ),
                    age_groups=self._get_age_groups(context.get('kids_ages', [])),
                    interests_covered=[],
                    weather_considerations=["Check weather before going out"],
                    practical_tips=["Check API connection"]
                )
                
                return {
                    "agent_name": "activities",
                    "status": "fallback",
                    "query": query,
                    "family_context": context,
                    "activities_text": activities_text,
                    "structured_data": structured_data,
                    "metadata": {
                        "processing_time": "real_time",
                        "confidence": 0.6,
                        "source": "fallback",
                        "error": str(agent_error)
                    }
                }
            
        except Exception as e:
            from app.models.activities_models import BudgetEstimate
            structured_data = ActivitiesResponse(
                activities=[],
                total_activities=0,
                recommended_duration="1 día",
                budget_estimate=BudgetEstimate(
                    range="€0-50", 
                    per_person="€10-25", 
                        notes="Critical error"
                ),
                age_groups=self._get_age_groups(context.get('kids_ages', [])),
                interests_covered=[],
                weather_considerations=["Check weather before going out"],
                practical_tips=["Check API connection"]
            )
            return {
                "agent_name": "activities",
                "status": "error",
                "query": query,
                "family_context": context,
                "activities_text": f"Sorry, there was an error creating your activities plan: {str(e)}",
                "structured_data": structured_data,
                "metadata": {
                    "processing_time": "real_time",
                    "confidence": 0.0,
                    "source": "error",
                    "error": str(e)
                }
            }
    
    def _parse_activities_response(self, activities_text: str, context: Dict) -> Dict[str, Any]:
        """Parses text response into structured data"""
        try:
            # Extract main data from context
            kids_ages = context.get('kids_ages', [])
            budget_level = context.get('budget_level', 'medium')
            interests = context.get('interests', [])
            
            # Parse activities from text
            activities = []
            lines = activities_text.split('\n')
            
            current_activity = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for activity headers (contain numbers or emojis)
                if any(indicator in line for indicator in ['**', '###', '1.', '2.', '3.', '4.', '5.', '🎯', '🏛️', '🌳', '🎨']):
                    if current_activity:
                        activities.append(current_activity)
                    
                    # Extract activity name
                    activity_name = line.replace('**', '').replace('###', '').strip()
                    # Remove numbers
                    import re
                    activity_name = re.sub(r'^\d+\.\s*', '', activity_name)
                    
                    current_activity = {
                        "name": activity_name,
                        "type": self._classify_activity_type(activity_name),
                        "description": "",
                        "schedule": "",
                        "location": "",
                        "price_range": self._estimate_price_range(activity_name, budget_level),
                        "age_suitability": self._assess_age_suitability(activity_name, kids_ages),
                        "interests_match": self._assess_interests_match(activity_name, interests),
                        "accessibility": "standard"
                    }
                elif current_activity and line:
                    # Add information to current activity
                    if 'horario' in line.lower() or 'schedule' in line.lower():
                        current_activity["schedule"] = line
                    elif 'ubicación' in line.lower() or 'location' in line.lower():
                        current_activity["location"] = line
                    elif not current_activity["description"]:
                        current_activity["description"] = line
                    else:
                        current_activity["description"] += " " + line
            
            # Add last activity
            if current_activity:
                activities.append(current_activity)
            
            # If couldn't extract activities, return empty list
            if not activities:
                activities = []
            
            return {
                "activities": activities,
                "total_activities": len(activities),
                "recommended_duration": self._calculate_recommended_duration(activities),
                "budget_estimate": self._calculate_budget_estimate(activities, budget_level),
                "age_groups": self._get_age_groups(kids_ages),
                "interests_covered": self._get_covered_interests(activities, interests),
                "weather_considerations": self._get_weather_considerations(),
                "practical_tips": self._get_practical_tips()
            }
            
        except Exception as e:
            return {
                "activities": [],
                "total_activities": 0,
                "error": str(e)
            }
    
    def _classify_activity_type(self, activity_name: str) -> str:
        """Classifies activity type"""
        activity_lower = activity_name.lower()
        if any(word in activity_lower for word in ['museo', 'museum', 'galería']):
            return "museum"
        elif any(word in activity_lower for word in ['parque', 'park', 'jardín']):
            return "park"
        elif any(word in activity_lower for word in ['taller', 'workshop', 'clase']):
            return "workshop"
        elif any(word in activity_lower for word in ['teatro', 'theater', 'espectáculo']):
            return "entertainment"
        elif any(word in activity_lower for word in ['zoo', 'acuario', 'animal']):
            return "nature"
        else:
            return "general"
    
    def _estimate_price_range(self, activity_name: str, budget_level: str) -> str:
        """Estimates activity price range"""
        activity_lower = activity_name.lower()
        if any(word in activity_lower for word in ['gratis', 'free', 'entrada libre']):
            return "free"
        elif any(word in activity_lower for word in ['museo', 'parque']):
            return "low" if budget_level == "low" else "medium"
        else:
            return "medium" if budget_level == "medium" else "high"
    
    def _assess_age_suitability(self, activity_name: str, kids_ages: List[int]) -> Dict[str, Any]:
        """Assesses suitable age for activity"""
        if not kids_ages:
            return {"suitable": True, "age_range": "all", "notes": ""}
        
        activity_lower = activity_name.lower()
        min_age = min(kids_ages)
        max_age = max(kids_ages)
        
        if any(word in activity_lower for word in ['museo', 'museum']):
            if min_age < 5:
                return {"suitable": False, "age_range": "5+", "notes": "Demasiado pequeño para museos"}
            elif max_age > 12:
                return {"suitable": True, "age_range": "5-12", "notes": "Ideal para niños"}
            else:
                return {"suitable": True, "age_range": "5-12", "notes": "Perfecto para esta edad"}
        else:
            return {"suitable": True, "age_range": "all", "notes": "Adecuado para todas las edades"}
    
    def _assess_interests_match(self, activity_name: str, interests: List[str]) -> float:
        """Assesses match with family interests (0-1)"""
        if not interests:
            return 0.5
        
        activity_lower = activity_name.lower()
        matches = 0
        
        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in activity_lower or any(word in activity_lower for word in interest_lower.split()):
                matches += 1
        
        return matches / len(interests)
    
    # Removed _generate_default_activities method - using only API data
    
    def _calculate_recommended_duration(self, activities: List[Dict]) -> str:
        """Calculates recommended duration"""
        total_activities = len(activities)
        if total_activities <= 2:
            return "1-2 días"
        elif total_activities <= 4:
            return "2-3 días"
        else:
            return "3-5 días"
    
    def _calculate_budget_estimate(self, activities: List[Dict], budget_level: str) -> Dict[str, str]:
        """Calculates budget estimate"""
        free_activities = len([a for a in activities if a.get("price_range") == "free"])
        total_activities = len(activities)
        
        if budget_level == "low":
            return {"range": "€0-50", "per_person": "€10-25", "notes": "Enfocado en actividades gratuitas"}
        elif budget_level == "high":
            return {"range": "€100-300", "per_person": "€50-150", "notes": "Incluye actividades premium"}
        else:
            return {"range": "€50-150", "per_person": "€25-75", "notes": "Balance entre calidad y precio"}
    
    def _get_age_groups(self, kids_ages: List[int]) -> List[str]:
        """Determines children's age groups"""
        if not kids_ages:
            return ["adults_only"]
        
        groups = []
        for age in kids_ages:
            if age <= 3:
                groups.append("toddlers")
            elif age <= 8:
                groups.append("children")
            elif age <= 12:
                groups.append("pre_teens")
            else:
                groups.append("teens")
        
        return list(set(groups))
    
    def _get_covered_interests(self, activities: List[Dict], interests: List[str]) -> List[str]:
        """Determines covered interests"""
        if not interests:
            return []
        
        covered = []
        for interest in interests:
            for activity in activities:
                if self._assess_interests_match(activity["name"], [interest]) > 0.5:
                    covered.append(interest)
                    break
        
        return covered
    
    def _get_weather_considerations(self) -> List[str]:
        """Returns weather recommendations"""
        return [
            "Llevar ropa de abrigo en invierno",
            "Paraguas recomendado en primavera",
            "Protector solar en verano",
            "Verificar horarios en días lluviosos"
        ]
    
    def _get_practical_tips(self) -> List[str]:
        """Returns practical tips"""
        return [
            "Reservar con antelación para actividades populares",
            "Llevar documentación para descuentos familiares",
            "Verificar horarios de apertura",
            "Considerar transporte público"
        ]
    
    def _format_activities_text(self, structured_data: ActivitiesResponse) -> str:
        """Formats structured data into readable text"""
        text = f"# 🎯 Plan de Actividades Personalizado\n\n"
        text += f"**Total de actividades:** {structured_data.total_activities}\n"
        text += f"**Duración recomendada:** {structured_data.recommended_duration}\n\n"
        
        for i, activity in enumerate(structured_data.activities, 1):
            text += f"## {i}. {activity.name}\n"
            text += f"**Tipo:** {activity.type.value.title()}\n"
            text += f"**Descripción:** {activity.description}\n"
            if activity.schedule:
                text += f"**Horario:** {activity.schedule}\n"
            if activity.location:
                text += f"**Ubicación:** {activity.location}\n"
            text += f"**Precio:** {activity.price_range.value}\n"
            text += f"**Adecuado para:** {activity.age_suitability.age_range}\n"
            if activity.age_suitability.notes:
                text += f"**Notas:** {activity.age_suitability.notes}\n"
            text += f"**Coincidencia con intereses:** {activity.interests_match:.0%}\n\n"
        
        return text
    
    # Removed _create_fallback_structured_data method - using only API data
    
    def _create_tools(self) -> List[Tool]:
        """Creates tools for agent with priorities"""
        return [
            Tool(
                name="analyze_age_compatibility",
                description="""[PRIORITY 2] Analyze compatibility of activities with age groups.
                Use for additional analysis after getting data from APIs.
                Input parameters: kids_ages (JSON array of ages)
                Format: analyze_age_compatibility('[8, 12]')
                Returns: analysis by age groups and recommendations""",
                func=self._analyze_age_compatibility
            ),
            Tool(
                name="optimize_schedule",
                description="""[PRIORITY 2] Optimize schedule considering energy peaks.
                Use for final schedule optimization.
                Input parameters: schedule_data (JSON with schedule data)
                Format: optimize_schedule('{"activities": [...]}')
                Returns: optimized schedule by time of day""",
                func=self._optimize_schedule
            )
        ]
    
    def _create_prompt(self) -> PromptTemplate:
        """Creates prompt for react-agent using ReAct pattern"""
        return PromptTemplate(
            template="""You are an expert family activities agent in Madrid that follows the ReAct pattern (Reasoning + Acting).

FAMILY INFORMATION:
- Children ages: {kids_ages}
- Number of adults: {adults_count}
- Interests: {interests}
- Country of origin: {origin_country}
- Special needs: {special_needs}
- Budget: {budget_level}
- Travel dates: {travel_dates}

AVAILABLE TOOLS:
{tools}

TOOL NAMES:
{tool_names}

TOOL PRIORITY:
1. **FIRST PRIORITY**: External APIs (search_places_api, get_place_details_api, check_weather_api, search_events_api)
2. **SECOND PRIORITY**: Internal tools (search_activities, analyze_age_compatibility, optimize_schedule)
3. **LAST OPTION**: create_activities_plan (only if no other options)

ReAct REASONING PATTERN:
**Thought**: [Analyze the query and determine what information you need]
**Action**: [Name of the tool to use]
**Action Input**: [Specific parameters for the tool]
**Observation**: [Tool result]
**Thought**: [Evaluate the result and decide the next step]
**Action**: [Next tool if necessary]
**Action Input**: [Parameters]
**Observation**: [Result]
**Final Answer**: [Final structured response]

STRICT RULES:
1. **ALWAYS** use external APIs FIRST if available
2. **COMBINE** information from multiple sources
3. **CHECK** weather for outdoor activities
4. **CONSIDER** specific age of children
5. **INCLUDE** precise schedules and locations
6. **BALANCE** educational and recreational activities

FLOW EXAMPLE:
**Thought**: I need to find activities for children aged 8 and 12 in Madrid
**Action**: search_places_api
**Action Input**: {{"query": "actividades familiares Madrid", "place_type": "tourist_attraction"}}
**Observation**: [Places found]
**Thought**: Now I'll check the weather to recommend appropriate activities
**Action**: check_weather_api
**Action Input**: {{"date": "2024-01-15"}}
**Observation**: [Weather data]
**Thought**: I'll analyze compatibility with children's ages
**Action**: analyze_age_compatibility
**Action Input**: {{"kids_ages": [8, 12]}}
**Observation**: [Age analysis]
**Final Answer**: [Personalized plan based on real data]

User question: {input}

{agent_scratchpad}""",
            input_variables=["input", "kids_ages", "adults_count", "interests", "origin_country", "special_needs", "budget_level", "travel_dates", "tools", "tool_names", "agent_scratchpad"]
        )
    
    # Removed _search_activities method - using only API search
    
    def _analyze_age_compatibility(self, kids_ages: str) -> str:
        """Analysis of compatibility with age groups"""
        try:
            ages = json.loads(kids_ages) if kids_ages.startswith('[') else [8, 12]
            
            analysis = {
                "age_groups": {
                    "toddlers": [age for age in ages if age < 4],
                    "preschoolers": [age for age in ages if 4 <= age < 6],
                    "school_age": [age for age in ages if 6 <= age < 12],
                    "teens": [age for age in ages if age >= 12]
                },
                "recommendations": {
                    "universal_activities": ["Parque del Retiro", "Museo Nacional de Ciencias Naturales"],
                    "age_specific": {
                        "toddlers": ["Parques infantiles", "Zoológico"],
                        "teens": ["Parque Warner", "Museo del Prado"]
                    }
                }
            }
            
            return json.dumps(analysis, ensure_ascii=False)
            
        except Exception as e:
            return f"Error in age analysis: {str(e)}"
    
    def _optimize_schedule(self, schedule_data: str) -> str:
        """Schedule optimization"""
        try:
            optimized_schedule = {
                "morning": {
                    "time": "09:00-12:00",
                    "activities": ["Museos", "Parques"],
                    "reason": "Alta energía, mejor concentración"
                },
                "afternoon": {
                    "time": "14:00-17:00",
                    "activities": ["Actividades activas", "Entretenimiento"],
                    "reason": "Energía moderada, tiempo para diversión"
                },
                "evening": {
                    "time": "18:00-20:00",
                    "activities": ["Paseos tranquilos", "Cenas familiares"],
                    "reason": "Energía baja, momento de relajación"
                }
            }
            
            return json.dumps(optimized_schedule, ensure_ascii=False)
            
        except Exception as e:
            return f"Error in optimization: {str(e)}"
    
    
    
    # API methods
    def _search_places_api(self, query: str, place_type: str = None) -> str:
        """Search places through Google Places API"""
        try:
            if not self.api_services["google_places"]:
                return json.dumps({"status": "error", "error": "Google Places API not configured"})
            
            # Real API call
            params = {
                "query": query,
                "location": "40.4168,-3.7038",  # Madrid coordinates
                "radius": 5000,
                "key": self.api_services["google_places"]["api_key"]
            }
            
            if place_type:
                params["types"] = place_type
            
            response = requests.get(
                f"{self.api_services['google_places']['base_url']}/textsearch/json",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                places = data.get("results", [])
                
                # Format results
                formatted_places = []
                for place in places[:5]:  # Limit to 5 results
                    formatted_places.append({
                        "name": place.get("name"),
                        "place_id": place.get("place_id"),
                        "rating": place.get("rating", 0),
                        "price_level": place.get("price_level", 2),
                        "types": place.get("types", []),
                        "vicinity": place.get("vicinity"),
                        "geometry": place.get("geometry", {})
                    })
                
                return json.dumps({
                    "status": "success",
                    "places": formatted_places,
                    "query": query,
                    "place_type": place_type
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
    
    def _get_place_details_api(self, place_id: str) -> str:
        """Get detailed information about a place"""
        try:
            if not self.api_services["google_places"]:
                return json.dumps({"status": "error", "error": "Google Places API not configured"})
            
            params = {
                "place_id": place_id,
                "fields": "name,formatted_address,rating,price_level,opening_hours,photos,reviews,website,formatted_phone_number,types",
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
                        "types": result.get("types", [])
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
        """Check weather through OpenWeatherMap API"""
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
                "lang": "es"
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
                    "recommendation": self._get_weather_recommendation(data['main']['temp'], data['weather'][0]['main'])
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
    
    def _get_weather_recommendation(self, temp: float, condition: str) -> str:
        """Generates recommendation based on weather"""
        if temp < 10:
            return "Llevar ropa de abrigo, ideal para actividades en interiores"
        elif temp > 25:
            return "Día caluroso, ideal para actividades al aire libre con protección solar"
        elif condition in ["Rain", "Drizzle"]:
            return "Lluvia prevista, recomendadas actividades en interiores"
        else:
            return "Ideal para actividades al aire libre"
    
    def _search_events_api(self, query: str, date: str = None) -> str:
        """Search events through Eventbrite API"""
        try:
            if not self.api_services["events"]:
                return json.dumps({"status": "error", "error": "Events API not configured"})
            
            # Real Eventbrite API call
            api_key = self.api_services["events"]["api_key"]
            base_url = self.api_services["events"]["base_url"]
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Search events in Madrid
            params = {
                "q": query,
                "location.address": "Madrid, Spain",
                "location.within": "10km",
                "sort_by": "date",
                "status": "live"
            }
            
            if date:
                params["start_date.range_start"] = date
                params["start_date.range_end"] = date
            
            response = requests.get(f"{base_url}/events/search", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = []
                
                for event in data.get("events", [])[:5]:  # Limit to 5 events
                    event_data = {
                        "name": event.get("name", {}).get("text", ""),
                        "date": event.get("start", {}).get("local", "").split("T")[0] if event.get("start", {}).get("local") else date or "",
                        "time": event.get("start", {}).get("local", "").split("T")[1][:5] if event.get("start", {}).get("local") else "",
                        "location": event.get("venue", {}).get("name", "Madrid"),
                        "price": self._get_event_price(event),
                        "age_range": self._get_event_age_range(event, query)
                    }
                    events.append(event_data)
            
                return json.dumps({
                    "status": "success",
                    "events": events,
                    "query": query,
                    "date": date
                })
            else:
                return json.dumps({
                    "status": "error",
                    "error": f"Events API error: {response.status_code}"
                })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    def _get_event_price(self, event: dict) -> str:
        """Extracts event price"""
        try:
            ticket_classes = event.get("ticket_availability", {}).get("ticket_classes", [])
            if ticket_classes:
                price = ticket_classes[0].get("cost", {}).get("display", "Gratis")
                return price
            return "Gratis"
        except:
            return "Gratis"
    
    def _get_event_age_range(self, event: dict, query: str) -> str:
        """Determines event age range"""
        name = event.get("name", {}).get("text", "").lower()
        if "niños" in name or "niños" in query.lower():
            return "5-12 años"
        elif "familiar" in name or "familiar" in query.lower():
            return "Todas las edades"
        else:
            return "Todas las edades"

def create_activities_agent() -> ActivitiesAgent:
    """Creates ActivitiesAgent instance for RouterAgent"""
    return ActivitiesAgent()