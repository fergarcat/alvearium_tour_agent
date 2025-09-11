
"""
Pydantic models for restaurant agent
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CuisineType(str, Enum):
    """Restaurant cuisine types"""
    SPANISH = "spanish"
    ITALIAN = "italian"
    FRENCH = "french"
    MEDITERRANEAN = "mediterranean"
    ASIAN = "asian"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    INDIAN = "indian"
    MEXICAN = "mexican"
    AMERICAN = "american"
    FAST_FOOD = "fast_food"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    SEAFOOD = "seafood"
    STEAKHOUSE = "steakhouse"
    TAPAS = "tapas"
    FUSION = "fusion"
    INTERNATIONAL = "international"
    CAFE = "cafe"
    BAKERY = "bakery"


class PriceRange(str, Enum):
    """Restaurant price ranges"""
    BUDGET = "budget"  # €0-15 per person
    MODERATE = "moderate"  # €15-35 per person
    EXPENSIVE = "expensive"  # €35-60 per person
    VERY_EXPENSIVE = "very_expensive"  # €60+ per person


class DietaryRestrictions(str, Enum):
    """Dietary restrictions and preferences"""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    HALAL = "halal"
    KOSHER = "kosher"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"
    LOW_SODIUM = "low_sodium"
    SUGAR_FREE = "sugar_free"


class OpeningHours(BaseModel):
    """Restaurant opening hours"""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None


class Location(BaseModel):
    """Restaurant location"""
    address: str
    city: str = "Madrid"
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    neighborhood: Optional[str] = None


class Review(BaseModel):
    """Restaurant review"""
    author: str
    rating: float = Field(ge=1.0, le=5.0)
    text: str
    date: Optional[str] = None


class MenuItem(BaseModel):
    """Restaurant menu item"""
    name: str
    description: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    dietary_info: List[DietaryRestrictions] = []


class Restaurant(BaseModel):
    """Restaurant model"""
    name: str
    cuisine_type: CuisineType
    price_range: PriceRange
    rating: float = Field(ge=1.0, le=5.0)
    location: Location
    opening_hours: Optional[OpeningHours] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    features: List[str] = []  # e.g., ["outdoor_seating", "wifi", "parking"]
    dietary_options: List[DietaryRestrictions] = []
    kid_friendly: bool = True
    reviews: List[Review] = []
    menu: List[MenuItem] = []
    photos: List[str] = []
    booking_required: bool = False
    average_meal_duration: Optional[str] = None  # e.g., "1-2 hours"


class BudgetEstimate(BaseModel):
    """Budget estimate for restaurant visit"""
    range: str  # e.g., "€20-40"
    per_person: str  # e.g., "€15-25"
    notes: str  # e.g., "Based on main course and drink"


class RestaurantResponse(BaseModel):
    """Main response from restaurant agent"""
    restaurants: List[Restaurant]
    total_restaurants: int
    recommended_duration: str  # e.g., "2-3 hours"
    budget_estimate: BudgetEstimate
    cuisine_types_covered: List[CuisineType]
    dietary_restrictions_covered: List[DietaryRestrictions]
    kid_friendly_options: int
    booking_recommendations: List[str]
    practical_tips: List[str]
    weather_considerations: List[str]


class RestaurantAgentResult(BaseModel):
    """Result from restaurant agent processing"""
    agent_name: str = "restaurant"
    status: str  # "success", "fallback", "error"
    query: str
    family_context: Dict[str, Any]
    restaurant_text: str
    structured_data: Optional[RestaurantResponse] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RestaurantSearchFilters(BaseModel):
    """Filters for restaurant search"""
    cuisine_types: List[CuisineType] = []
    price_ranges: List[PriceRange] = []
    dietary_restrictions: List[DietaryRestrictions] = []
    kid_friendly: bool = True
    outdoor_seating: Optional[bool] = None
    wifi: Optional[bool] = None
    parking: Optional[bool] = None
    rating_min: float = Field(default=3.0, ge=1.0, le=5.0)
    max_distance_km: float = Field(default=5.0, ge=0.1, le=50.0)
    booking_available: Optional[bool] = None


class RestaurantRecommendation(BaseModel):
    """Individual restaurant recommendation"""
    restaurant: Restaurant
    match_score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = []
    best_time_to_visit: Optional[str] = None
    special_notes: Optional[str] = None
