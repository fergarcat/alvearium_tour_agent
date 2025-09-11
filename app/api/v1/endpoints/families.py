# app/api/v1/endpoints/families.py
"""
Family management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from ...dependencies import get_supabase_config
from models.family_models_supabase import FamilyProfileSupabase

router = APIRouter(prefix="/families", tags=["families"])

# Pydantic модели для API
class FamilyCreateRequest(BaseModel):
    family_id: str
    kids_ages: List[int]
    adults_count: int
    budget_level: str
    start_date: str
    end_date: str
    interests: List[str]
    origin_country: str
    special_needs: Optional[List[str]] = None
    language_preference: str = "es"
    accommodation_type: Optional[str] = None
    transportation_preference: Optional[str] = None

class FamilyUpdateRequest(BaseModel):
    kids_ages: Optional[List[int]] = None
    adults_count: Optional[int] = None
    budget_level: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interests: Optional[List[str]] = None
    origin_country: Optional[str] = None
    special_needs: Optional[List[str]] = None
    language_preference: Optional[str] = None
    accommodation_type: Optional[str] = None
    transportation_preference: Optional[str] = None

class FamilyResponse(BaseModel):
    family_id: str
    kids_ages: List[int]
    adults_count: int
    budget_level: str
    start_date: str
    end_date: str
    interests: List[str]
    origin_country: str
    special_needs: List[str]
    language_preference: str
    accommodation_type: str
    transportation_preference: str
    stay_duration: int
    family_size: int
    age_group: str

@router.post("/", response_model=FamilyResponse)
async def create_family(
    family_data: FamilyCreateRequest,
    supabase_config: Dict[str, str] = Depends(get_supabase_config)
):
    """Создает новый профиль семьи"""
    try:
        # Создаем профиль
        profile = FamilyProfileSupabase(
            family_id=family_data.family_id,
            kids_ages=family_data.kids_ages,
            adults_count=family_data.adults_count,
            budget_level=family_data.budget_level,
            start_date=family_data.start_date,
            end_date=family_data.end_date,
            interests=family_data.interests,
            origin_country=family_data.origin_country,
            special_needs=family_data.special_needs,
            language_preference=family_data.language_preference,
            accommodation_type=family_data.accommodation_type,
            transportation_preference=family_data.transportation_preference
        )
        
        # Сохраняем в Supabase
        family_uuid = profile.save_to_supabase()
        
        if not family_uuid:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save family profile"
            )
        
        return FamilyResponse(
            family_id=profile.family_id,
            kids_ages=profile.kids_ages,
            adults_count=profile.adults_count,
            budget_level=getattr(profile, 'budget_level', 'medium'),
            start_date=getattr(profile, 'start_date', ''),
            end_date=getattr(profile, 'end_date', ''),
            interests=profile.interests,
            origin_country=profile.origin_country,
            special_needs=profile.special_needs or [],
            language_preference=profile.language_preference,
            accommodation_type=profile.accommodation_type or "hotel",
            transportation_preference=profile.transportation_preference or "public",
            stay_duration=profile.get_stay_duration(),
            family_size=profile.get_family_size(),
            age_group=profile.get_age_group()
        )
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка создания семьи: {error_msg}")
        
        # Проверяем тип ошибки
        if "duplicate key value violates unique constraint" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Family with ID '{family_data.family_id}' already exists. Please use a different family_id or delete the existing one."
            )
        elif "Supabase credentials not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection not configured. Please check SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating family: {error_msg}"
            )

@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: str,
    supabase_config: Dict[str, str] = Depends(get_supabase_config)
):
    """Получает профиль семьи по ID"""
    try:
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=[],
            adults_count=0,
            budget_level="",
            start_date="",
            end_date="",
            interests=[],
            origin_country=""
        )
        
        if not profile.load_from_supabase(family_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with ID {family_id} not found"
            )
        
        return FamilyResponse(
            family_id=profile.family_id,
            kids_ages=profile.kids_ages,
            adults_count=profile.adults_count,
            budget_level=getattr(profile, 'budget_level', 'medium'),
            start_date=getattr(profile, 'start_date', ''),
            end_date=getattr(profile, 'end_date', ''),
            interests=profile.interests,
            origin_country=profile.origin_country,
            special_needs=profile.special_needs or [],
            language_preference=profile.language_preference,
            accommodation_type=profile.accommodation_type or "hotel",
            transportation_preference=profile.transportation_preference or "public",
            stay_duration=profile.get_stay_duration(),
            family_size=profile.get_family_size(),
            age_group=profile.get_age_group()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting family: {str(e)}"
        )

@router.put("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: str,
    family_data: FamilyUpdateRequest,
    supabase_config: Dict[str, str] = Depends(get_supabase_config)
):
    """Обновляет профиль семьи"""
    try:
        # Загружаем существующий профиль
        profile = FamilyProfileSupabase(
            family_id=family_id,
            kids_ages=[],
            adults_count=0,
            budget_level="",
            start_date="",
            end_date="",
            interests=[],
            origin_country=""
        )
        
        if not profile.load_from_supabase(family_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with ID {family_id} not found"
            )
        
        # Обновляем поля
        if family_data.kids_ages is not None:
            profile.kids_ages = family_data.kids_ages
        if family_data.adults_count is not None:
            profile.adults_count = family_data.adults_count
        if family_data.budget_level is not None:
            setattr(profile, 'budget_level', family_data.budget_level)
        if family_data.start_date is not None:
            profile.start_date = family_data.start_date
        if family_data.end_date is not None:
            profile.end_date = family_data.end_date
        if family_data.interests is not None:
            profile.interests = family_data.interests
        if family_data.origin_country is not None:
            profile.origin_country = family_data.origin_country
        if family_data.special_needs is not None:
            profile.special_needs = family_data.special_needs
        if family_data.language_preference is not None:
            profile.language_preference = family_data.language_preference
        if family_data.accommodation_type is not None:
            profile.accommodation_type = family_data.accommodation_type
        if family_data.transportation_preference is not None:
            profile.transportation_preference = family_data.transportation_preference
        
        # Сохраняем изменения
        if not profile.update_in_supabase():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update family profile"
            )
        
        return FamilyResponse(
            family_id=profile.family_id,
            kids_ages=profile.kids_ages,
            adults_count=profile.adults_count,
            budget_level=getattr(profile, 'budget_level', 'medium'),
            start_date=getattr(profile, 'start_date', ''),
            end_date=getattr(profile, 'end_date', ''),
            interests=profile.interests,
            origin_country=profile.origin_country,
            special_needs=profile.special_needs or [],
            language_preference=profile.language_preference,
            accommodation_type=profile.accommodation_type or "hotel",
            transportation_preference=profile.transportation_preference or "public",
            stay_duration=profile.get_stay_duration(),
            family_size=profile.get_family_size(),
            age_group=profile.get_age_group()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating family: {str(e)}"
        )

@router.delete("/{family_id}")
async def delete_family(
    family_id: str,
    supabase_config: Dict[str, str] = Depends(get_supabase_config)
):
    """Удаляет профиль семьи"""
    try:
        from supabase import create_client
        
        client = create_client(supabase_config["url"], supabase_config["key"])
        
        # Получаем UUID семьи
        family_result = client.table("families").select("id").eq("family_id", family_id).execute()
        
        if not family_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Family with ID {family_id} not found"
            )
        
        family_uuid = family_result.data[0]["id"]
        
        # Удаляем семью (члены семьи удалятся автоматически из-за CASCADE)
        client.table("families").delete().eq("id", family_uuid).execute()
        
        return {"message": f"Family {family_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting family: {str(e)}"
        )
