from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from app.models.outing import OutingPreferences, OutingProfile
from app.models.plan import Plan
from app.services.recommendation import generate_recommendation

router = APIRouter()

outing_preferences_store = {}
plan_store = {}

@router.get("/")
def home():
    return {"message": "Planning Service Running"}

@router.get("/outing-profile", response_model=OutingProfile)
def get_outing_profile(user_id: str = Query(...)):
    # Mocked external call or future replacement
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/outing-preferences")
def post_outing_preferences(user_id: str = Query(...), prefs: OutingPreferences = ...):
    outing_preferences_store[user_id] = prefs
    return {"message": "Outing preferences saved", "user_id": user_id}

@router.get("/outing-preferences", response_model=OutingPreferences)
def get_outing_preferences(user_id: str = Query(...)):
    prefs = outing_preferences_store.get(user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return prefs

@router.post("/plan")
def post_plan(plan: Plan):
    plan_store[plan.user_id] = plan
    return {"message": "Plan saved successfully", "user_id": plan.user_id}

@router.get("/plan", response_model=Plan)
def get_plan(user_id: str = Query(...)):
    plan = plan_store.get(user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.get("/recommend")
def recommend(
    city: str = Query(...),
    venue_type: str = Query(...),
    keywords: str = Query(...),
    datetime_str: str = Query(...)
):
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        result = generate_recommendation(city, venue_type, keywords, dt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
