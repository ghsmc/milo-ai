from fastapi import FastAPI, Query
from typing import List, Optional
from pydantic import BaseModel
from milo_ai import MiloAI

# Create a simple API app
simple_api = FastAPI(title="Yale Alumni Simple API")

# Initialize MiloAI
milo = MiloAI()

class AlumniProfile(BaseModel):
    name: str
    position: Optional[str] = None
    company: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[str] = None
    location: Optional[str] = None
    connections: Optional[int] = None

@simple_api.get("/companies/{company_name}/alumni")
async def get_company_alumni(company_name: str, limit: int = Query(50, ge=1, le=500)):
    """Get Yale alumni at a specific company"""
    if not milo.yale_data:
        return {"company": company_name, "total_alumni": 0, "alumni": []}
    
    company_lower = company_name.lower()
    filtered = []
    
    # Use the same data source as the main analysis
    for alumni in milo.yale_data:
        current_company = (alumni.get('current_company_name') or alumni.get('company') or '').lower()
        
        # Use the same flexible matching logic as the main analysis
        target_words = [word for word in company_lower.split() if len(word) > 2]
        company_words = [word for word in current_company.split() if len(word) > 2]
        
        # Check if any target word is in company name or vice versa
        match_found = False
        for target_word in target_words:
            if any(target_word in company_word or company_word in target_word for company_word in company_words):
                match_found = True
                break
        
        # Also check the original simple matching as fallback
        if not match_found:
            match_found = company_lower in current_company or current_company in company_lower
        
        if match_found:
            education_info = milo.extract_detailed_education(alumni.get('education_details', []))
            
            filtered.append(AlumniProfile(
                name=alumni.get('name', 'Yale Alumni'),
                position=alumni.get('current_title') or alumni.get('position'),
                company=alumni.get('current_company_name') or alumni.get('company'),
                major=education_info.get('major', 'Liberal Arts'),
                graduation_year=education_info.get('graduation_year', 'XX'),
                location=alumni.get('city') or alumni.get('location'),
                connections=alumni.get('connections', 0)
            ))
            
            if len(filtered) >= limit:
                break
    
    return {
        "company": company_name,
        "total_alumni": len(filtered),
        "alumni": filtered
    }

@simple_api.get("/positions/{position_name}/alumni")
async def get_position_alumni(position_name: str, limit: int = Query(50, ge=1, le=500)):
    """Get Yale alumni in a specific position"""
    if not milo.yale_data:
        return {"position": position_name, "total_alumni": 0, "alumni": []}
    
    position_lower = position_name.lower()
    filtered = []
    
    for alumni in milo.yale_data:
        current_position = (alumni.get('current_title') or alumni.get('position') or '').lower()
        
        if position_lower in current_position or any(word in current_position for word in position_lower.split()):
            education_info = milo.extract_detailed_education(alumni.get('education_details', []))
            
            filtered.append(AlumniProfile(
                name=alumni.get('name', 'Yale Alumni'),
                position=alumni.get('current_title') or alumni.get('position'),
                company=alumni.get('current_company_name') or alumni.get('company'),
                major=education_info.get('major', 'Liberal Arts'),
                graduation_year=education_info.get('graduation_year', 'XX'),
                location=alumni.get('city') or alumni.get('location'),
                connections=alumni.get('connections', 0)
            ))
            
            if len(filtered) >= limit:
                break
    
    return {
        "position": position_name,
        "total_alumni": len(filtered),
        "alumni": filtered
    }

@simple_api.get("/companies/{company_name}/insights")
async def get_company_insights(company_name: str):
    """Get insights about a specific company"""
    if not milo.yale_data:
        return {"company": company_name, "total_alumni": 0, "insights": "No data available"}
    
    company_lower = company_name.lower()
    alumni = []
    
    for person in milo.yale_data:
        current_company = (person.get('current_company_name') or person.get('company') or '').lower()
        if company_lower in current_company or current_company in company_lower:
            alumni.append(person)
    
    if not alumni:
        return {"company": company_name, "total_alumni": 0, "insights": "No alumni found"}
    
    # Analyze the data
    majors = {}
    positions = {}
    locations = {}
    
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
    
    return {
        "company": company_name,
        "total_alumni": len(alumni),
        "hiring_trends": {
            "most_common_majors": sorted(majors.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_common_positions": sorted(positions.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_locations": sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    }

@simple_api.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "yale-alumni-simple-api",
        "data_loaded": len(milo.yale_data) if milo.yale_data else 0
    }
