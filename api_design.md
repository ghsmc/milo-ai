# Yale Alumni API Design

## Core API Endpoints

### 1. Company Search
```
GET /api/companies/{company_name}/alumni
GET /api/companies/{company_name}/alumni?limit=50&offset=0
GET /api/companies/{company_name}/alumni?major=Computer Science
GET /api/companies/{company_name}/alumni?graduation_year=2020-2024
```

**Response:**
```json
{
  "company": "Goldman Sachs",
  "total_alumni": 45,
  "alumni": [
    {
      "name": "Jean-Joel Ocran",
      "position": "Analyst",
      "major": "Economics and Mathematics",
      "graduation_year": "2022",
      "location": "New York, NY",
      "connections": 500,
      "networking_score": 75,
      "career_progression": {
        "years_experience": 2,
        "career_stage": "Early Career",
        "total_positions": 3
      },
      "key_skills": ["Financial Modeling", "Data Analysis", "Strategy"],
      "experience_history": [...],
      "linkedin_url": "https://linkedin.com/in/jean-joel-ocran"
    }
  ]
}
```

### 2. Position/Role Search
```
GET /api/positions/{position_name}/alumni
GET /api/positions/software-engineer/alumni?company=Google
GET /api/positions/investment-banking-analyst/alumni?major=Economics
```

### 3. Industry Search
```
GET /api/industries/{industry}/alumni
GET /api/industries/technology/alumni?limit=100
GET /api/industries/finance/alumni?graduation_year=2015-2020
```

### 4. Major/Education Search
```
GET /api/majors/{major}/alumni
GET /api/majors/computer-science/alumni?company=Google
GET /api/majors/economics/alumni?industry=finance
```

### 5. Career Path Analysis
```
GET /api/career-paths?from_major=Computer Science&to_company=Google
GET /api/career-paths?from_position=Software Engineer&to_position=Product Manager
GET /api/career-paths/trending?industry=technology
```

### 6. Networking Recommendations
```
GET /api/networking/recommendations?target_company=Goldman Sachs&user_major=Economics
GET /api/networking/recommendations?target_industry=technology&user_graduation_year=2024
```

### 7. Company Insights
```
GET /api/companies/{company_name}/insights
GET /api/companies/Google/insights?include_salaries=true
```

**Response:**
```json
{
  "company": "Google",
  "total_yale_alumni": 127,
  "hiring_trends": {
    "most_common_majors": ["Computer Science", "Mathematics", "Physics"],
    "most_common_positions": ["Software Engineer", "Product Manager", "Data Scientist"],
    "average_experience_level": "Mid Career",
    "hiring_by_year": {...}
  },
  "alumni_distribution": {
    "by_location": {...},
    "by_graduation_year": {...},
    "by_career_stage": {...}
  },
  "networking_opportunities": {
    "high_networking_score": [...],
    "recent_hires": [...],
    "senior_alumni": [...]
  }
}
```

### 8. Search & Filter
```
GET /api/search?q=software engineer google
GET /api/search?company=Microsoft&position=Product Manager&major=Computer Science
GET /api/search?industry=finance&graduation_year=2020-2024&location=New York
```

## Advanced Features

### 9. Career Progression Analysis
```
GET /api/career-progression?from_company=Goldman Sachs&to_company=Google
GET /api/career-progression/trends?industry=technology
```

### 10. Salary Insights (if available)
```
GET /api/salaries?company=Google&position=Software Engineer
GET /api/salaries?industry=finance&experience_level=mid
```

### 11. Alumni Recommendations Engine
```
POST /api/recommendations
{
  "user_profile": {
    "major": "Computer Science",
    "graduation_year": "2024",
    "interests": ["AI", "Machine Learning"],
    "target_companies": ["Google", "OpenAI"],
    "target_roles": ["Software Engineer", "Research Scientist"]
  }
}
```

## Implementation Benefits

1. **Reliability**: Each endpoint has a specific purpose and can be tested independently
2. **Performance**: Can cache specific queries (e.g., company alumni lists)
3. **Flexibility**: Frontend can build custom experiences using different API combinations
4. **Scalability**: Can add new endpoints without breaking existing functionality
5. **Analytics**: Can track which queries are most popular
6. **Integration**: Other applications can use the API

## Database Optimization

- **Indexes**: Company names, positions, majors, graduation years
- **Caching**: Popular queries (e.g., "Goldman Sachs alumni")
- **Aggregation**: Pre-compute common statistics
- **Search**: Full-text search on names, companies, positions

## Frontend Integration

Instead of one monolithic response, the frontend can:
1. Query specific alumni for a company
2. Get career path recommendations
3. Fetch networking suggestions
4. Build custom dashboards
5. Create interactive visualizations
