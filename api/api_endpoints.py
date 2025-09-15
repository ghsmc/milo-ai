from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
from milo_ai import MiloAI

# Initialize the API
api_app = FastAPI(title="Yale Alumni API", version="1.0.0")

# Initialize MiloAI for data access
milo = MiloAI()

# Pydantic models for request/response
class AlumniProfile(BaseModel):
    name: str
    position: Optional[str] = None
    company: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[str] = None
    location: Optional[str] = None
    connections: Optional[int] = None
    networking_score: Optional[int] = None
    career_progression: Optional[Dict] = None
    key_skills: Optional[List[str]] = None
    experience_history: Optional[List[Dict]] = None

class CompanyAlumniResponse(BaseModel):
    company: str
    total_alumni: int
    alumni: List[AlumniProfile]

class CareerPathResponse(BaseModel):
    path: str
    count: int
    examples: List[Dict]

# Helper functions
def filter_alumni_by_company(company_name: str, limit: int = 50) -> List[Dict]:
    """Filter alumni by company name"""
    if not milo.yale_data:
        return []
    
    company_lower = company_name.lower()
    filtered = []
    
    for alumni in milo.yale_data:
        current_company = (alumni.get('current_company_name') or alumni.get('company') or '').lower()
        
        # Flexible matching
        if company_lower in current_company or current_company in company_lower:
            filtered.append(alumni)
            if len(filtered) >= limit:
                break
    
    return filtered

def filter_alumni_by_position(position_name: str, limit: int = 50) -> List[Dict]:
    """Filter alumni by position/role"""
    if not milo.yale_data:
        return []
    
    position_lower = position_name.lower()
    filtered = []
    
    for alumni in milo.yale_data:
        current_position = (alumni.get('current_title') or alumni.get('position') or '').lower()
        
        # Check if position matches
        if position_lower in current_position or any(word in current_position for word in position_lower.split()):
            filtered.append(alumni)
            if len(filtered) >= limit:
                break
    
    return filtered

def filter_alumni_by_major(major_name: str, limit: int = 50) -> List[Dict]:
    """Filter alumni by major"""
    if not milo.yale_data:
        return []
    
    major_lower = major_name.lower()
    filtered = []
    
    for alumni in milo.yale_data:
        education_details = alumni.get('educations_details', '')
        if major_lower in education_details.lower():
            filtered.append(alumni)
            if len(filtered) >= limit:
                break
    
    return filtered

def get_company_insights(company_name: str) -> Dict[str, Any]:
    """Get insights about a specific company"""
    alumni = filter_alumni_by_company(company_name, limit=1000)
    
    if not alumni:
        return {"company": company_name, "total_alumni": 0, "insights": "No data available"}
    
    # Analyze the data
    majors = {}
    positions = {}
    locations = {}
    graduation_years = {}
    
    for person in alumni:
        # Count majors
        major = milo.extract_major(person.get('educations_details', ''))
        majors[major] = majors.get(major, 0) + 1
        
        # Count positions
        position = person.get('current_title') or person.get('position', 'Unknown')
        positions[position] = positions.get(position, 0) + 1
        
        # Count locations
        location = person.get('city') or person.get('location', 'Unknown')
        locations[location] = locations.get(location, 0) + 1
        
        # Count graduation years
        year = milo.extract_graduation_year(person.get('educations_details', ''))
        graduation_years[year] = graduation_years.get(year, 0) + 1
    
    return {
        "company": company_name,
        "total_alumni": len(alumni),
        "hiring_trends": {
            "most_common_majors": sorted(majors.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_common_positions": sorted(positions.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_locations": sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5],
            "graduation_years": dict(sorted(graduation_years.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    }

# API Endpoints

@api_app.get("/api/companies/{company_name}/alumni")
async def get_company_alumni(
    company_name: str,
    limit: int = Query(50, ge=1, le=500),
    major: Optional[str] = None,
    graduation_year: Optional[str] = None
):
    """Get Yale alumni at a specific company"""
    alumni = filter_alumni_by_company(company_name, limit)
    
    # Apply additional filters
    if major:
        alumni = [a for a in alumni if major.lower() in milo.extract_major(a.get('educations_details', '')).lower()]
    
    if graduation_year:
        alumni = [a for a in alumni if graduation_year in milo.extract_graduation_year(a.get('educations_details', ''))]
    
    # Convert to response format
    alumni_profiles = []
    for person in alumni:
        education_info = milo.extract_detailed_education(person.get('education_details', []))
        
        alumni_profiles.append(AlumniProfile(
            name=person.get('name', 'Yale Alumni'),
            position=person.get('current_title') or person.get('position'),
            company=person.get('current_company_name') or person.get('company'),
            major=education_info.get('major', 'Liberal Arts'),
            graduation_year=education_info.get('graduation_year', 'XX'),
            location=person.get('city') or person.get('location'),
            connections=person.get('connections', 0),
            networking_score=milo.calculate_networking_score(person),
            career_progression=milo.analyze_career_progression(person.get('experience_history', [])),
            key_skills=milo.extract_skills_from_experience(person.get('experience_history', [])),
            experience_history=person.get('experience_history', [])
        ))
    
    return CompanyAlumniResponse(
        company=company_name,
        total_alumni=len(alumni_profiles),
        alumni=alumni_profiles
    )

@api_app.get("/api/positions/{position_name}/alumni")
async def get_position_alumni(
    position_name: str,
    limit: int = Query(50, ge=1, le=500),
    company: Optional[str] = None
):
    """Get Yale alumni in a specific position/role"""
    alumni = filter_alumni_by_position(position_name, limit)
    
    # Apply company filter
    if company:
        company_lower = company.lower()
        alumni = [a for a in alumni if company_lower in (a.get('current_company_name') or a.get('company') or '').lower()]
    
    # Convert to response format
    alumni_profiles = []
    for person in alumni:
        education_info = milo.extract_detailed_education(person.get('education_details', []))
        
        alumni_profiles.append(AlumniProfile(
            name=person.get('name', 'Yale Alumni'),
            position=person.get('current_title') or person.get('position'),
            company=person.get('current_company_name') or person.get('company'),
            major=education_info.get('major', 'Liberal Arts'),
            graduation_year=education_info.get('graduation_year', 'XX'),
            location=person.get('city') or person.get('location'),
            connections=person.get('connections', 0),
            networking_score=milo.calculate_networking_score(person),
            career_progression=milo.analyze_career_progression(person.get('experience_history', [])),
            key_skills=milo.extract_skills_from_experience(person.get('experience_history', [])),
            experience_history=person.get('experience_history', [])
        ))
    
    return CompanyAlumniResponse(
        company=position_name,
        total_alumni=len(alumni_profiles),
        alumni=alumni_profiles
    )

@api_app.get("/api/companies/{company_name}/insights")
async def get_company_insights_endpoint(company_name: str):
    """Get insights about a specific company"""
    return get_company_insights(company_name)

@api_app.get("/api/majors/{major_name}/alumni")
async def get_major_alumni(
    major_name: str,
    limit: int = Query(50, ge=1, le=500),
    company: Optional[str] = None
):
    """Get Yale alumni with a specific major"""
    alumni = filter_alumni_by_major(major_name, limit)
    
    # Apply company filter
    if company:
        company_lower = company.lower()
        alumni = [a for a in alumni if company_lower in (a.get('current_company_name') or a.get('company') or '').lower()]
    
    # Convert to response format
    alumni_profiles = []
    for person in alumni:
        education_info = milo.extract_detailed_education(person.get('education_details', []))
        
        alumni_profiles.append(AlumniProfile(
            name=person.get('name', 'Yale Alumni'),
            position=person.get('current_title') or person.get('position'),
            company=person.get('current_company_name') or person.get('company'),
            major=education_info.get('major', 'Liberal Arts'),
            graduation_year=education_info.get('graduation_year', 'XX'),
            location=person.get('city') or person.get('location'),
            connections=person.get('connections', 0),
            networking_score=milo.calculate_networking_score(person),
            career_progression=milo.analyze_career_progression(person.get('experience_history', [])),
            key_skills=milo.extract_skills_from_experience(person.get('experience_history', [])),
            experience_history=person.get('experience_history', [])
        ))
    
    return CompanyAlumniResponse(
        company=major_name,
        total_alumni=len(alumni_profiles),
        alumni=alumni_profiles
    )

@api_app.get("/api/search")
async def search_alumni(
    q: str = Query(..., description="Search query"),
    company: Optional[str] = None,
    position: Optional[str] = None,
    major: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """Search alumni with multiple filters"""
    if not milo.yale_data:
        return {"results": [], "total": 0}
    
    results = []
    query_lower = q.lower()
    
    for alumni in milo.yale_data:
        # Check if query matches name, company, or position
        name = (alumni.get('name') or '').lower()
        company_name = (alumni.get('current_company_name') or alumni.get('company') or '').lower()
        position_name = (alumni.get('current_title') or alumni.get('position') or '').lower()
        
        if (query_lower in name or 
            query_lower in company_name or 
            query_lower in position_name):
            
            # Apply additional filters
            if company and company.lower() not in company_name:
                continue
            if position and position.lower() not in position_name:
                continue
            if major and major.lower() not in milo.extract_major(alumni.get('educations_details', '')).lower():
                continue
            
            results.append(alumni)
            if len(results) >= limit:
                break
    
    return {"results": results, "total": len(results)}

@api_app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "yale-alumni-api",
        "data_loaded": len(milo.yale_data) if milo.yale_data else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=8002)
