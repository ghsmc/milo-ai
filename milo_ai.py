from openai import AsyncOpenAI
import json
import pandas as pd
from typing import Dict, List, AsyncGenerator
import asyncio
import os
import sqlite3
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Load environment variables
load_dotenv()

class MiloAI:
    def __init__(self):
        # Get OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = AsyncOpenAI(api_key=api_key)
        self.yale_data = self.load_yale_data()
        
        # Conversation context management
        self.conversation_sessions = {}
        
        # Master prompt for the 6-step conversation flow
        self.master_prompt = """You are a Yale career advisor AI that helps students discover their path through a natural, conversational 6-step process. You have deep knowledge of Yale-specific resources, programs, and alumni networks.

CRITICAL CONVERSATION RULES:
1. You are having a CONTINUOUS conversation. Do NOT restart with "STEP 1: DISCOVER" unless this is truly the very first message.
2. Build on what the student has already shared and continue naturally from where you left off.
3. Focus on ONE step at a time. Do NOT dump multiple steps in a single response.
4. Progress naturally through the conversation based on what the student shares.
5. Be conversational and engaging, not robotic or formulaic.

THE 6-STEP PROCESS (follow naturally, one step at a time):

**STEP 1: DISCOVER** - Ask about activities, classes, or projects that make them feel alive or curious at Yale. Extract 3-5 core interests.

**STEP 2: EXPLORE DREAM JOBS** - Based on their interests, suggest 3-5 specific career paths with job titles, descriptions, and companies where Yale alums work.

**STEP 3: NEXT MOVES THIS SEMESTER** - Suggest 3-4 concrete actions they can take THIS SEMESTER at Yale (courses, organizations, faculty, resources).

**STEP 4: REAL OPPORTUNITIES** - List actual programs they can apply to (internships, fellowships, on-campus opportunities) with deadlines and funding info.

**STEP 5: CONNECT** - Draft 2-3 networking templates (alumni outreach, professor conversations, informational interviews).

**STEP 6: REFLECT & ITERATE** - Ask what excites them most, what concerns them, then offer three options for next steps.

CONVERSATION FLOW:
- Start with Step 1 if it's a new conversation
- Progress to the next step naturally when the student has shared enough information
- Don't rush through steps - let the conversation flow organically
- Each response should focus on the current step and naturally lead to the next
- NEVER dump multiple steps in one response - focus on ONE step at a time
- Be conversational and engaging, not robotic or formulaic

## KNOWLEDGE BASE TO REFERENCE:

**Yale-Specific Resources:**
- CCPD (Center for Career & Professional Development)
- OCS (Office of Career Strategy) 
- Yale Career Network (YCN) for alumni
- Journalism Initiative
- Jackson School (global affairs)
- CEID (Center for Engineering Innovation & Design)
- Tsai CITY (Center for Innovative Thinking)
- Digital Humanities Lab
- Every Yale residential college has career advisors
- Yale Science & Engineering Association (YSEA)
- Yale Entrepreneurial Institute (YEI)

**Funding Sources:**
- International Summer Award (ISA) - funds unpaid international internships
- CIPE Fellowships - career exploration grants
- Richter Fellowship - independent research
- Light Fellowship - freshman/sophomore exploration
- Bulldogs Abroad - funded programs in specific cities
- First-Year Summer Funding - for students on financial aid
- Public Service Funding through Dwight Hall

**Key Timelines:**
- Light Fellowship: Usually due in February
- ISA: March deadline
- Summer internship apps: Rolling, but many close Jan-March
- Richter: February deadline
- Yale Career Fairs: September & February

## INTERACTION STYLE:
- Be conversational but efficient
- Use bullet points for clarity
- Bold important program names and deadlines
- Include specific Yale building names, course numbers when relevant
- Reference actual Yale alums when possible (without making up names)
- If unsure about a specific deadline or program detail, say "Check with CCPD for current deadline"

## EXAMPLE INTERACTION START:
Student: "I love data science, global issues, and writing."

Your response should follow ALL 6 STEPS, creating a comprehensive career exploration session that feels personalized and actionable, grounded in real Yale resources.

Remember: Every suggestion should be something the student could actually do at Yale or through Yale connections. No generic advice - everything Yale-specific and actionable."""
        
    def load_yale_data(self):
        """Load Yale alumni data from available sources"""
        try:
            # First, try Railway PostgreSQL database
            if os.getenv('DATABASE_URL'):
                print("📊 Loading Yale dataset from Railway PostgreSQL...")
                return self.load_from_postgres()
            
            # Check for sample data (for Railway deployment without DB)
            elif os.path.exists('sample_data.json'):
                print("📊 Loading sample Yale dataset...")
                with open('sample_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded {len(data)} sample profiles")
                return data
            
            # Check for local SQLite database (for local development)
            elif os.path.exists('yale.db'):
                print("📊 Loading Yale dataset from local SQLite database...")
                return self.load_from_sqlite()
            
            else:
                print("⚠️  No Yale database found. Using fallback data.")
                return self.get_fallback_data()
                
        except Exception as e:
            print(f"❌ Error loading Yale data: {e}")
            return self.get_fallback_data()
    
    def load_from_sqlite(self):
        """Load data from SQLite database (local development)"""
        conn = sqlite3.connect('yale.db')
        cursor = conn.cursor()
        
        # Get comprehensive alumni data with experience history, education details, and company insights
        query = """
        SELECT 
            p.person_id,
            p.name,
            p.position,
            p.company,
            p.location,
            p.city,
            p.country_code,
            p.about,
            p.connections,
            p.followers,
            p.recommendations_count,
            p.educations_details,
            cc.name as current_company_name,
            cc.title as current_title,
            GROUP_CONCAT(e.company || '|' || e.title || '|' || e.start_date || '|' || e.end_date || '|' || COALESCE(e.description, ''), '||') as experience_history,
            GROUP_CONCAT(ed.title || '|' || ed.degree || '|' || ed.field || '|' || ed.start_year || '|' || ed.end_year, '||') as education_details,
            ec.industry as company_industry,
            ec.size as company_size,
            ec.employee_count,
            ec.yale_alumni_count
        FROM clean_yale_profiles p
        LEFT JOIN current_companies cc ON p.person_id = cc.person_id
        LEFT JOIN clean_experiences e ON p.person_id = e.person_id
        LEFT JOIN clean_educations ed ON p.person_id = ed.person_id
        LEFT JOIN enhanced_companies ec ON (cc.name = ec.name OR p.company = ec.name)
        WHERE p.name IS NOT NULL 
        AND p.position IS NOT NULL
        AND p.company IS NOT NULL
        AND p.company != ''
        GROUP BY p.person_id
        ORDER BY p.connections DESC
        LIMIT 5000
        """
        
        cursor.execute(query)
        profiles = cursor.fetchall()
        
        # Convert to list of dictionaries with enhanced parsing
        data = []
        for profile in profiles:
            experience_history = []
            if profile[14]:  # experience_history
                for exp in profile[14].split('||'):
                    if exp and '|' in exp:
                        parts = exp.split('|')
                        if len(parts) >= 4:
                            experience_history.append({
                                'company': parts[0],
                                'title': parts[1],
                                'start_date': parts[2],
                                'end_date': parts[3],
                                'description': parts[4] if len(parts) > 4 else ''
                            })
            
            education_details = []
            if profile[15]:  # education_details
                for edu in profile[15].split('||'):
                    if edu and '|' in edu:
                        parts = edu.split('|')
                        if len(parts) >= 5:
                            education_details.append({
                                'institution': parts[0],
                                'degree': parts[1],
                                'field': parts[2],
                                'start_year': parts[3],
                                'end_year': parts[4]
                            })
            
            data.append({
                'person_id': profile[0],
                'name': profile[1],
                'position': profile[2],
                'company': profile[3],
                'location': profile[4],
                'city': profile[5],
                'country_code': profile[6],
                'about': profile[7],
                'connections': profile[8],
                'followers': profile[9],
                'recommendations_count': profile[10],
                'educations_details': profile[11],
                'current_company_name': profile[12],
                'current_title': profile[13],
                'experience_history': experience_history,
                'education_details': education_details,
                'company_industry': profile[16],
                'company_size': profile[17],
                'employee_count': profile[18],
                'yale_alumni_count': profile[19]
            })
        
        conn.close()
        print(f"✅ Loaded {len(data)} profiles from SQLite database")
        return data
    
    def load_from_postgres(self):
        """Load data from Railway PostgreSQL database"""
        try:
            db_url = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if yale_profiles table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'yale_profiles'
                );
            """)
            table_exists = cursor.fetchone()['exists']
            
            if not table_exists:
                print("⚠️  yale_profiles table not found in PostgreSQL")
                print("💡 Run the migration script first: python migrate_to_railway.py")
                conn.close()
                return self.get_fallback_data()
            
            # Get profiles from PostgreSQL
            query = """
            SELECT 
                person_id, name, position, company, location, city, country_code,
                about, connections, followers, recommendations_count, educations_details,
                current_company_name, current_title, experience_history, education_details,
                company_industry, company_size, employee_count, yale_alumni_count
            FROM yale_profiles
            WHERE name IS NOT NULL 
            AND position IS NOT NULL
            AND (current_company_name IS NOT NULL AND current_company_name != '' OR company IS NOT NULL AND company != '')
            ORDER BY connections DESC
            LIMIT 100000
            """
            
            cursor.execute(query)
            profiles = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for profile in profiles:
                data.append({
                    'person_id': profile['person_id'],
                    'name': profile['name'],
                    'position': profile['position'],
                    'company': profile['company'],
                    'location': profile['location'],
                    'city': profile['city'],
                    'country_code': profile['country_code'],
                    'about': profile['about'],
                    'connections': profile['connections'],
                    'followers': profile['followers'],
                    'recommendations_count': profile['recommendations_count'],
                    'educations_details': profile['educations_details'],
                    'current_company_name': profile['current_company_name'],
                    'current_title': profile['current_title'],
                    'experience_history': profile['experience_history'] or [],
                    'education_details': profile['education_details'] or [],
                    'company_industry': profile['company_industry'],
                    'company_size': profile['company_size'],
                    'employee_count': profile['employee_count'],
                    'yale_alumni_count': profile['yale_alumni_count']
                })
            
            conn.close()
            print(f"✅ Loaded {len(data)} profiles from Railway PostgreSQL")
            return data
            
        except Exception as e:
            print(f"❌ Error loading from PostgreSQL: {e}")
            return self.get_fallback_data()
    
    def get_fallback_data(self):
        """Return minimal fallback data when database is not available"""
        return [
            {
                'person_id': 'fallback_1',
                'name': 'Sample Yale Alumnus',
                'position': 'Software Engineer',
                'company': 'Tech Company',
                'location': 'San Francisco, CA',
                'about': 'Yale graduate working in technology',
                'educations_details': 'Yale University - Computer Science',
                'current_company_name': 'Tech Company',
                'current_company_industry': 'Technology',
                'current_company_size': '1000+',
                'current_company_type': 'Public',
                'current_company_description': 'Leading technology company'
            }
        ]
        
    async def analyze_career(self, user_input: str) -> dict:
        """Main function: dream job → actionable plan (Stockfish for careers)"""
        
        try:
            # Step 1: Process and classify the user query
            processed_query = await self.process_user_query(user_input)
            
            # Step 2: Parse what they want from the processed query
            intent = await self.extract_intent(processed_query['expanded_query'])
            
            # Step 3: Find alumni at target companies
            target_company_alumni = self.find_alumni_at_companies(intent.get("target_companies", []))
            
            # Step 4: Find common career paths to target roles
            career_paths = self.find_career_paths_to_roles(intent.get("target_roles", []))
            
            # Step 5: Find specific people to contact based on major/interests
            people_to_contact = self.find_people_to_contact(intent, target_company_alumni)
            
            # Step 6: Generate comprehensive action plan
            plan = await self.create_comprehensive_plan(intent, target_company_alumni, career_paths, people_to_contact, user_input, processed_query)
            
            return {
                "analysis": intent,
                "processed_query": processed_query,
                "target_company_alumni": target_company_alumni,
                "career_paths": career_paths,
                "people_to_contact": people_to_contact,
                "action_plan": plan,
                "success_odds": self.calculate_odds(target_company_alumni)
            }
            
        except Exception as e:
            import traceback
            return {"error": f"Analysis failed: {str(e)}\nTraceback: {traceback.format_exc()}"}

    async def process_user_query(self, user_input: str) -> dict:
        """Intelligent query processing layer that classifies and expands user queries"""
        
        prompt = f"""
        You are an intelligent career query processor for Yale students. Analyze this query and understand the student's intent, then expand it intelligently.
        
        User Query: "{user_input}"
        
        Think like a career counselor who knows the Yale network. Be smart about:
        
        1. **Understanding Intent:**
           - What is the student really asking for?
           - Are they being specific or general?
           - What's their level of career knowledge?
           - What would be most helpful for them?
        
        2. **Smart Classification:**
           - "specific_company": Clear company mentions (e.g., "work at Google", "Goldman Sachs")
           - "industry": Industry/sector mentions (e.g., "investment banking", "tech", "consulting", "IB")
           - "role": Specific job titles (e.g., "software engineer", "product manager", "consultant")
           - "general": Vague career goals that need guidance
        
        3. **Intelligent Expansion:**
           - For industries: Think about what Yale students typically target
           - For roles: Consider where these roles are most common
           - For companies: Keep as-is but add context
           - For general queries: Suggest the most relevant path based on Yale student patterns
        
        4. **Yale-Specific Industry Mappings:**
           - "IB" or "investment banking" → ["Goldman Sachs", "Morgan Stanley", "J.P. Morgan", "Citigroup", "Bank of America"]
           - "tech" or "technology" → ["Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix"]
           - "consulting" → ["McKinsey", "Bain", "BCG", "Deloitte", "PwC"]
           - "finance" → ["Goldman Sachs", "Morgan Stanley", "J.P. Morgan", "BlackRock", "Vanguard"]
           - "startups" → ["Stripe", "Airbnb", "Uber", "Lyft", "Pinterest"]
           - "PE" or "private equity" → ["KKR", "Blackstone", "Apollo", "Carlyle", "TPG"]
           - "VC" or "venture capital" → ["Andreessen Horowitz", "Sequoia", "Kleiner Perkins", "Accel", "Benchmark"]
        
        Return ONLY valid JSON:
        {{
            "query_type": "specific_company|industry|role|general",
            "original_query": "{user_input}",
            "expanded_query": "intelligent expansion with context",
            "detected_industry": "industry name if detected",
            "detected_companies": ["list of specific companies mentioned or inferred"],
            "detected_roles": ["list of specific roles mentioned or inferred"],
            "confidence": 0.0-1.0,
            "student_intent": "brief description of what the student is really looking for"
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            # Fallback if JSON parsing fails
            return {
                "query_type": "general",
                "original_query": user_input,
                "expanded_query": user_input,
                "detected_industry": "Technology",
                "detected_companies": [],
                "detected_roles": [],
                "confidence": 0.5
            }
    
    async def extract_intent(self, user_input: str) -> dict:
        """Use GPT to parse career goals with better role extraction"""
        
        prompt = f"""
        Parse this Yale student's career goal and return ONLY valid JSON:
        
        "{user_input}"
        
        {{
            "target_companies": ["list specific companies if mentioned"],
            "target_roles": ["list specific job titles - if no specific role mentioned, infer common roles for the company/industry"],
            "industry": "main industry sector",
            "motivation": "brief reason why they want this",
            "timeline": "when they want to achieve this"
        }}
        
        IMPORTANT: If they mention a company but no specific role, infer common entry-level roles for that company/industry.
        For example: "work at Goldman Sachs" → roles: ["Investment Banking Analyst", "Sales & Trading Analyst", "Operations Analyst"]
        For example: "work at Google" → roles: ["Software Engineer", "Product Manager", "Business Analyst"]
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "target_companies": ["Technology Companies"],
                "target_roles": ["Software Engineer"],
                "industry": "Technology",
                "motivation": "Career growth",
                "timeline": "1-2 years"
            }
    
    def find_alumni_at_companies(self, target_companies: List[str]) -> List[dict]:
        """Find all Yale alumni currently at target companies with enhanced details"""
        if not target_companies or not self.yale_data:
            return []
        
        alumni_at_companies = []
        target_companies_lower = [c.lower() for c in target_companies]
        
        
        for alumni in self.yale_data:
            current_company = (alumni.get('current_company_name') or alumni.get('company') or '').lower()
            
            for target_company in target_companies_lower:
                # More flexible matching - check if any significant word matches
                target_words = [word for word in target_company.split() if len(word) > 2]
                company_words = [word for word in current_company.split() if len(word) > 2]
                
                # Check if any target word is in company name or vice versa
                match_found = False
                for target_word in target_words:
                    if any(target_word in company_word or company_word in target_word for company_word in company_words):
                        match_found = True
                        break
                
                # Also check the original simple matching as fallback
                if not match_found:
                    match_found = target_company in current_company or current_company in target_company
                
                if match_found:
                    # Extract detailed education info
                    education_info = self.extract_detailed_education(alumni.get('education_details', []))
                    
                    alumni_at_companies.append({
                        "name": alumni.get('name', 'Yale Alumni'),
                        "position": alumni.get('current_title', alumni.get('position', '')),
                        "company": alumni.get('current_company_name', alumni.get('company', '')),
                        "location": alumni.get('city', alumni.get('location', '')),
                        "connections": alumni.get('connections', 0),
                        "followers": alumni.get('followers', 0),
                        "recommendations": alumni.get('recommendations_count', 0),
                        "major": education_info.get('major', 'Liberal Arts'),
                        "degree": education_info.get('degree', ''),
                        "graduation_year": education_info.get('graduation_year', 'XX'),
                        "about": alumni.get('about', ''),
                        "experience_history": alumni.get('experience_history', []),
                        "company_industry": alumni.get('company_industry', ''),
                        "company_size": alumni.get('company_size', ''),
                        "yale_alumni_at_company": alumni.get('yale_alumni_count', 0),
                        "career_progression": self.analyze_career_progression(alumni.get('experience_history', [])),
                        "key_skills": self.extract_skills_from_experience(alumni.get('experience_history', [])),
                        "networking_score": self.calculate_networking_score(alumni)
                    })
                    break
        
        return alumni_at_companies
    
    def find_career_paths_to_roles(self, target_roles: List[str]) -> List[dict]:
        """Find common career paths to target roles with flexible matching"""
        if not self.yale_data:
            return []
        
        career_paths = []
        
        # If no specific roles provided, find paths to any professional roles
        if not target_roles:
            # Look for any alumni with professional experience
            for alumni in self.yale_data:
                if alumni.get('experience_history'):
                    path = self.build_detailed_career_path(alumni)
                    if path and len(path.split(' → ')) > 1:  # Only include paths with multiple steps
                        career_paths.append({
                            "name": alumni.get('name', 'Yale Alumni'),
                            "current_role": alumni.get('current_title', alumni.get('position', '')),
                            "current_company": alumni.get('current_company_name', alumni.get('company', '')),
                            "career_path": path,
                            "major": self.extract_major(alumni.get('educations_details', '')),
                            "graduation_year": self.extract_graduation_year(alumni.get('educations_details', '')),
                            "location": alumni.get('city', alumni.get('location', ''))
                        })
        else:
            target_roles_lower = [r.lower() for r in target_roles]
            
            for alumni in self.yale_data:
                current_role = (alumni.get('current_title') or alumni.get('position') or '').lower()
                
                # More flexible matching - check if any key words match
                role_match = False
                for target_role in target_roles_lower:
                    target_words = target_role.split()
                    if any(word in current_role for word in target_words if len(word) > 3):  # Only match words longer than 3 chars
                        role_match = True
                        break
                
                if role_match:
                    path = self.build_detailed_career_path(alumni)
                    if path:
                        career_paths.append({
                            "name": alumni.get('name', 'Yale Alumni'),
                            "current_role": alumni.get('current_title', alumni.get('position', '')),
                            "current_company": alumni.get('current_company_name', alumni.get('company', '')),
                            "career_path": path,
                            "major": self.extract_major(alumni.get('educations_details', '')),
                            "graduation_year": self.extract_graduation_year(alumni.get('educations_details', '')),
                            "location": alumni.get('city', alumni.get('location', ''))
                        })
        
        # Group by similar paths and count frequency
        path_groups = {}
        for path in career_paths:
            path_key = f"{path['major']} → {path['career_path']}"
            if path_key not in path_groups:
                path_groups[path_key] = {
                    "path": path_key,
                    "count": 0,
                    "examples": []
                }
            path_groups[path_key]["count"] += 1
            path_groups[path_key]["examples"].append(path)
        
        # Return top 5 most common paths
        sorted_paths = sorted(path_groups.values(), key=lambda x: x["count"], reverse=True)
        return sorted_paths[:5]
    
    def find_people_to_contact(self, intent: dict, target_company_alumni: List[dict]) -> List[dict]:
        """Find specific people to contact based on major and interests"""
        if not target_company_alumni:
            return []
        
        # Sort by relevance (connections, role match, major match)
        def relevance_score(person):
            score = 0
            major = (person.get('major') or '').lower()
            position = (person.get('position') or '').lower()
            
            # Major match bonus
            if 'computer' in major or 'engineering' in major:
                score += 10
            elif 'business' in major or 'economics' in major:
                score += 8
            elif 'liberal' in major:
                score += 5
            
            # Role match bonus
            target_roles = [r.lower() for r in intent.get("target_roles", [])]
            for role in target_roles:
                if any(word in position for word in role.split()):
                    score += 15
            
            # Connection count bonus
            score += min(person.get('connections', 0) / 100, 20)
            
            return score
        
        # Sort and return top 3 people to contact
        sorted_alumni = sorted(target_company_alumni, key=relevance_score, reverse=True)
        return sorted_alumni[:3]
    
    def build_detailed_career_path(self, alumni: dict) -> str:
        """Build detailed career path from experience history"""
        try:
            major = self.extract_major(alumni.get('educations_details', ''))
            graduation_year = self.extract_graduation_year(alumni.get('educations_details', ''))
            
            path_parts = [f"Yale {major} '{graduation_year}"]
            
            # Add experience history (last 3 jobs)
            experience_history = alumni.get('experience_history', [])
            for exp in experience_history[-3:]:
                if exp.get('company') and exp.get('title'):
                    path_parts.append(f"{exp['title']} at {exp['company']}")
            
            # Add current position if different
            current_role = alumni.get('current_title', alumni.get('position', ''))
            current_company = alumni.get('current_company_name', alumni.get('company', ''))
            if current_role and current_company:
                current = f"{current_role} at {current_company}"
                if current not in path_parts:
                    path_parts.append(current)
            
            return " → ".join(path_parts[-4:])  # Keep it concise
            
        except:
            return "Yale → Career Success"

    def find_matching_yale_alumni(self, intent: dict) -> List[dict]:
        """Find relevant Yale alumni from real data using database queries"""
        
        if not self.yale_data:
            return self.get_fallback_paths(intent)
            
        matches = []
        target_companies = [c.lower() for c in intent.get("target_companies", [])]
        target_roles = [r.lower() for r in intent.get("target_roles", [])]
        
        for alumni in self.yale_data:
            score = 0
            
            # Check current company match
            current_company = (alumni.get('current_company_name') or alumni.get('company') or '').lower()
            for company in target_companies:
                if company in current_company or current_company in company:
                    score += 3
            
            # Check current role match
            current_role = (alumni.get('current_title') or alumni.get('position') or '').lower()
            for role in target_roles:
                if any(word in current_role for word in role.split()):
                    score += 2
            
            # Check position field for role matches
            position = (alumni.get('position') or '').lower()
            for role in target_roles:
                if any(word in position for word in role.split()):
                    score += 1
            
            if score > 0:
                # Create career path string
                career_path = self.build_career_path(alumni)
                
                # Extract graduation year from educations_details if available
                graduation_year = self.extract_graduation_year(alumni.get('educations_details', ''))
                
                matches.append({
                    "name": alumni.get('name', 'Yale Alumni'),
                    "major": self.extract_major(alumni.get('educations_details', '')),
                    "path": career_path,
                    "current": f"{alumni.get('current_title', alumni.get('position', 'Unknown'))} at {alumni.get('current_company_name', alumni.get('company', 'Unknown'))}",
                    "score": score,
                    "advice": self.generate_advice(alumni),
                    "graduation_year": graduation_year,
                    "location": alumni.get('city', alumni.get('location', '')),
                    "connections": alumni.get('connections', 0)
                })
        
        # Sort by relevance score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5] if matches else self.get_fallback_paths(intent)
    
    def extract_graduation_year(self, educations_details: str) -> str:
        """Extract graduation year from education details"""
        if not educations_details:
            return "XX"
        
        # Look for years in the education details
        import re
        years = re.findall(r'\b(19|20)\d{2}\b', educations_details)
        if years:
            return str(max(years))[-2:]  # Return last 2 digits of most recent year
        return "XX"
    
    def extract_major(self, educations_details: str) -> str:
        """Extract major/field from education details"""
        if not educations_details:
            return "Unknown"
        
        # Look for common major patterns
        major_patterns = [
            r'Computer Science', r'CS', r'Engineering', r'Mathematics', r'Math',
            r'Economics', r'Business', r'Finance', r'Political Science', r'Psychology',
            r'History', r'English', r'Literature', r'Biology', r'Chemistry',
            r'Physics', r'Art', r'Music', r'Philosophy', r'Sociology'
        ]
        
        for pattern in major_patterns:
            if re.search(pattern, educations_details, re.IGNORECASE):
                # Return the actual major found, not the regex pattern
                match = re.search(pattern, educations_details, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        return "Liberal Arts"
    
    def build_career_path(self, alumni: dict) -> str:
        """Build career progression string from alumni data"""
        
        try:
            major = self.extract_major(alumni.get('educations_details', ''))
            current_role = alumni.get('current_title', alumni.get('position', ''))
            current_company = alumni.get('current_company_name', alumni.get('company', ''))
            graduation_year = self.extract_graduation_year(alumni.get('educations_details', ''))
            
            path_parts = [f"Yale {major} '{graduation_year}"]
            
            # Add current position
            if current_role and current_company:
                path_parts.append(f"{current_role} at {current_company}")
            elif current_role:
                path_parts.append(current_role)
            
            return " → ".join(path_parts[-3:])  # Keep it concise
            
        except:
            return "Yale → Career Success"
    
    def generate_advice(self, alumni: dict) -> str:
        """Generate specific advice based on alumni background"""
        
        major = self.extract_major(alumni.get('educations_details', ''))
        current_company = alumni.get('current_company_name', alumni.get('company', ''))
        current_role = alumni.get('current_title', alumni.get('position', ''))
        connections = alumni.get('connections', 0)
        
        advice_parts = []
        
        # Major-specific advice
        if 'computer' in (major or '').lower() or 'engineering' in (major or '').lower():
            advice_parts.append(f"Build strong technical projects in {major}")
        elif 'business' in (major or '').lower() or 'economics' in (major or '').lower():
            advice_parts.append(f"Develop business acumen through {major} coursework")
        else:
            advice_parts.append(f"Leverage your {major} background for unique perspectives")
        
        # Company-specific advice
        if current_company and current_company != 'Unknown':
            advice_parts.append(f"Network with {current_company} employees through LinkedIn")
        
        # Role-specific advice
        if 'engineer' in (current_role or '').lower() or 'developer' in (current_role or '').lower():
            advice_parts.append("Focus on coding skills and technical problem-solving")
        elif 'banker' in (current_role or '').lower() or 'investment' in (current_role or '').lower():
            advice_parts.append("Master financial modeling and market analysis")
        elif 'manager' in (current_role or '').lower() or 'director' in (current_role or '').lower():
            advice_parts.append("Develop leadership and project management skills")
        elif 'data' in (current_role or '').lower() or 'analyst' in (current_role or '').lower():
            advice_parts.append("Master data analysis tools and statistical methods")
        elif 'policy' in (current_role or '').lower() or 'government' in (current_role or '').lower():
            advice_parts.append("Build policy expertise and government relations skills")
        elif 'law' in (current_role or '').lower() or 'attorney' in (current_role or '').lower():
            advice_parts.append("Develop legal research and advocacy skills")
        elif 'founder' in (current_role or '').lower() or 'ceo' in (current_role or '').lower():
            advice_parts.append("Build entrepreneurial and strategic thinking skills")
        
        # Network advice
        if connections > 500:
            advice_parts.append("Leverage your strong professional network")
        else:
            advice_parts.append("Build your professional network through Yale alumni events")
        
        return " • ".join(advice_parts[:3])  # Return top 3 pieces of advice
    
    def get_fallback_paths(self, intent: dict) -> List[dict]:
        """Fallback paths when no data matches"""
        
        industry = intent.get('industry', 'Technology').lower()
        
        if 'tech' in industry or 'software' in industry:
            return [
                {
                    "name": "Anonymous Yale '20",
                    "major": "Computer Science",
                    "path": "Yale CS → Tech Internship → Software Engineer",
                    "current": "Software Engineer at Major Tech Company",
                    "score": 1,
                    "advice": "Focus on CS fundamentals, build projects, apply to internships early"
                }
            ]
        elif 'finance' in industry or 'banking' in industry:
            return [
                {
                    "name": "Anonymous Yale '19",
                    "major": "Economics",
                    "path": "Yale Econ → Finance Internship → Investment Banking",
                    "current": "Investment Banker at Wall Street Firm",
                    "score": 1,
                    "advice": "Join finance clubs, network with alumni, master financial modeling"
                }
            ]
        else:
            return [
                {
                    "name": "Anonymous Yale Graduate",
                    "major": "Liberal Arts",
                    "path": "Yale → Industry Experience → Leadership Role",
                    "current": "Professional in Target Industry",
                    "score": 1,
                    "advice": "Leverage Yale network, build relevant skills, gain industry experience"
                }
            ]
    
    async def create_comprehensive_plan(self, intent: dict, target_company_alumni: List[dict], career_paths: List[dict], people_to_contact: List[dict], user_input: str = "", processed_query: dict = None) -> dict:
        """Create clean, ChatGPT-style action plan with structured data"""
        
        # Extract student name
        student_name = self.extract_student_name(user_input, intent)
        
        # Count alumni at target companies
        total_alumni = len(target_company_alumni)
        total_paths = len(career_paths)
        top_contacts = len(people_to_contact)
        
        # Get primary target company or industry
        if processed_query and processed_query.get('query_type') == 'industry':
            target_company = processed_query.get('detected_industry', 'your target industry')
        else:
            target_company = intent.get('target_companies', ['your target company'])[0] if intent.get('target_companies') else 'your target company'
        
        # Create the personalized greeting with context about query processing
        if processed_query and processed_query.get('query_type') == 'industry':
            personalized_greeting = f"Hey {student_name}, you want to work in {target_company}? I found Yale alumni at top companies in this industry. Here are the {total_alumni} Yale alumni currently at relevant companies, the {total_paths} most common paths to get hired, and the {top_contacts} people you should talk to first based on your major and interests."
        else:
            personalized_greeting = f"Hey {student_name}, you want to work at {target_company}? Here are the {total_alumni} Yale alumni currently there, the {total_paths} most common paths to get hired, and the {top_contacts} people you should talk to first based on your major and interests."
        
        # Structure the alumni data cleanly
        alumni_summary = self.format_alumni_data(target_company_alumni)
        paths_summary = self.format_career_paths(career_paths)
        contacts_summary = self.format_people_to_contact(people_to_contact)
        
        # Create a much cleaner, more concise response
        context = f"""
        {personalized_greeting}
        
        **QUERY ANALYSIS:**
        Original Query: "{processed_query.get('original_query', user_input) if processed_query else user_input}"
        Query Type: {processed_query.get('query_type', 'general') if processed_query else 'general'}
        Detected Industry: {processed_query.get('detected_industry', 'Not specified') if processed_query else 'Not specified'}
        Expanded Companies: {', '.join(processed_query.get('detected_companies', [])) if processed_query else 'Not specified'}
        
        **YALE ALUMNI AT {target_company.upper()}** ({total_alumni} total)
        {alumni_summary}
        
        **PEOPLE TO CONTACT FIRST** ({top_contacts} prioritized)
        {contacts_summary}
        
        **COMMON CAREER PATHS** ({total_paths} paths)
        {paths_summary}
        """
        
        prompt = f"""
        You are Milo, Yale's AI career strategist. You're having a conversation with a Yale student about their career goals. Be conversational, insightful, and genuinely helpful - like ChatGPT but specialized in Yale career guidance.
        
        {context}
        
        IMPORTANT: Start with exactly this greeting: "{personalized_greeting}"
        
        Then provide a natural, conversational response that feels like you're talking to a friend who happens to be an expert. Here's how to structure it:
        
        **IMMEDIATE ACTIONS (Next 7 Days):**
        - Be conversational: "Here's what I'd do if I were in your shoes this week..."
        - Name specific alumni with context: "I'd start with [Name] - they're perfect for you because..."
        - Give specific outreach advice: "When you reach out, mention that you noticed their transition from [X] to [Y] - it shows you've done your homework"
        - Make it actionable: "Here's exactly what to say in your LinkedIn message..."
        
        **THIS SEMESTER:**
        - Be strategic: "Based on what I see working for Yale students, here's your semester game plan..."
        - Reference real examples: "Take a page from [Name]'s book - they took [specific courses] and it paid off when they..."
        - Give insider tips: "Here's something most students don't know about [industry]..."
        - Be encouraging: "You're in a great position because..."
        
        **CAREER TIMELINE:**
        - Paint a picture: "Here's how I see your path unfolding..."
        - Use real examples: "Look at [Name] - they started exactly where you are and now they're..."
        - Be realistic but optimistic: "The timeline might seem long, but here's why it's worth it..."
        - Give insider knowledge: "Here's what I've learned from watching Yale students succeed..."
        
        **SUCCESS FACTORS:**
        - Share insights: "Here's what separates the successful Yale students from the rest..."
        - Tell stories: "Let me tell you about [Name] - their story is perfect for your situation..."
        - Give practical advice: "Here's the mistake I see students make most often..."
        - End with encouragement: "You've got this - here's why I'm confident you'll succeed..."
        
        Write like you're having a conversation. Use "I," "you," contractions, and natural language. Be encouraging, specific, and genuinely helpful. Make them feel like they have a personal career advisor who knows the Yale network inside and out.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        return {"plan": response.choices[0].message.content}

    def extract_student_name(self, user_input: str, intent: dict) -> str:
        """Extract student name from input"""
        student_name = "there"  # Default
        
        # Check both motivation and the original user input for name patterns
        text_to_check = f"{intent.get('motivation', '')} {user_input}"
        
        # Look for common name patterns
        import re
        name_patterns = [
            r"i'm (\w+)",
            r"im (\w+)", 
            r"my name is (\w+)",
            r"hi, i'm (\w+)",
            r"hello, i'm (\w+)",
            r"hey, i'm (\w+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text_to_check, re.IGNORECASE)
            if match:
                student_name = match.group(1).title()
                break
        
        return student_name

    def format_alumni_data(self, alumni_list: List[dict]) -> str:
        """Format alumni data with detailed career information"""
        if not alumni_list:
            return "No Yale alumni found at this company."
        
        formatted = []
        for i, alumni in enumerate(alumni_list[:5], 1):  # Show top 5
            name = alumni.get('name', 'Yale Alumni')
            position = alumni.get('position', '')
            company = alumni.get('company', '')
            major = alumni.get('major', 'Liberal Arts')
            year = alumni.get('graduation_year', 'XX')
            location = alumni.get('location', '')
            networking_score = alumni.get('networking_score', 0)
            career_progression = alumni.get('career_progression', {})
            key_skills = alumni.get('key_skills', [])
            experience_history = alumni.get('experience_history', [])
            
            entry = f"{i}. **{name}** - {position} at {company}"
            entry += f"\n   {major} '{year} | {location} | Networking Score: {networking_score}/100"
            
            # Add career progression info
            if career_progression:
                career_stage = career_progression.get('career_stage', '')
                years_experience = career_progression.get('years_experience', 0)
                if career_stage and years_experience:
                    entry += f"\n   Career Stage: {career_stage} ({years_experience} years experience)"
            
            # Add key skills
            if key_skills:
                entry += f"\n   Key Skills: {', '.join(key_skills[:3])}"
            
            # Add recent career progression
            if experience_history and len(experience_history) > 1:
                recent_roles = experience_history[:2]  # Last 2 roles
                progression = " → ".join([role.get('title', '') for role in recent_roles if role.get('title')])
                if progression:
                    entry += f"\n   Recent Path: {progression}"
            
            if alumni.get('about'):
                about_preview = alumni['about'][:100] + "..." if len(alumni['about']) > 100 else alumni['about']
                entry += f"\n   About: {about_preview}"
            
            formatted.append(entry)
        
        return "\n\n".join(formatted)

    def format_career_paths(self, career_paths: List[dict]) -> str:
        """Format career paths with detailed examples and progression"""
        if not career_paths:
            return "No common career paths found. Consider exploring different roles or industries."
        
        formatted = []
        for i, path in enumerate(career_paths[:3], 1):  # Show top 3
            path_text = path.get('path', '')
            count = path.get('count', 0)
            examples = path.get('examples', [])
            
            entry = f"{i}. **{path_text}**"
            entry += f"\n   {count} people followed this path"
            
            if examples:
                example = examples[0]
                name = example.get('name', '')
                current_role = example.get('current_role', '')
                current_company = example.get('current_company', '')
                major = example.get('major', '')
                graduation_year = example.get('graduation_year', '')
                
                entry += f"\n   Example: {name} ({major} '{graduation_year})"
                entry += f"\n   Current: {current_role} at {current_company}"
                
                # Add career path details if available
                career_path = example.get('career_path', '')
                if career_path:
                    entry += f"\n   Path: {career_path}"
            
            formatted.append(entry)
        
        return "\n\n".join(formatted)

    def format_people_to_contact(self, people: List[dict]) -> str:
        """Format people to contact with specific outreach strategies"""
        if not people:
            return "No specific people identified for contact."
        
        formatted = []
        for i, person in enumerate(people[:3], 1):  # Show top 3
            name = person.get('name', 'Yale Alumni')
            position = person.get('position', '')
            company = person.get('company', '')
            major = person.get('major', 'Liberal Arts')
            year = person.get('graduation_year', 'XX')
            location = person.get('location', '')
            networking_score = person.get('networking_score', 0)
            skills = person.get('key_skills', [])
            career_progression = person.get('career_progression', {})
            experience_history = person.get('experience_history', [])
            
            entry = f"{i}. **{name}** - {position} at {company}"
            entry += f"\n   {major} '{year} | {location} | Networking Score: {networking_score}/100"
            
            if skills:
                entry += f"\n   Key Skills: {', '.join(skills[:3])}"
            
            # Add career progression for outreach context
            if career_progression:
                career_stage = career_progression.get('career_stage', '')
                if career_stage:
                    entry += f"\n   Career Stage: {career_stage}"
            
            # Add recent career moves for conversation starters
            if experience_history and len(experience_history) > 1:
                recent_role = experience_history[0]
                previous_role = experience_history[1] if len(experience_history) > 1 else None
                if recent_role and previous_role:
                    entry += f"\n   Recent Move: {previous_role.get('title', '')} → {recent_role.get('title', '')}"
            
            # Add specific outreach suggestion
            if networking_score >= 70:
                entry += f"\n   💡 Outreach: High networking score - likely responsive to Yale connections"
            elif major and 'Liberal Arts' not in major:
                entry += f"\n   💡 Outreach: Mention shared {major} background and career transition"
            else:
                entry += f"\n   💡 Outreach: Connect via Yale alumni network, mention shared university experience"
            
            formatted.append(entry)
        
        return "\n\n".join(formatted)

    async def create_action_plan(self, intent: dict, paths: List[dict]) -> dict:
        """Generate specific action plan using real Yale paths"""
        
        context = f"""
        Student Goal: {intent}
        
        Similar Yale Alumni Paths:
        {json.dumps(paths[:3], indent=2)}
        """
        
        prompt = f"""
        You are Milo, Yale's AI career strategist. Create a specific, actionable plan.
        
        {context}
        
        Generate a detailed roadmap with:
        
        **IMMEDIATE ACTIONS (Next 7 Days):**
        - 3 specific things they can do this week
        
        **THIS SEMESTER:**
        - Course recommendations
        - Activities to join
        - Skills to develop
        
        **CAREER TIMELINE:**
        - Internship strategy
        - Network building
        - Post-graduation plan
        
        **SUCCESS FACTORS:**
        - Key requirements for their goal
        - Common mistakes to avoid
        
        Be specific and actionable. Use Yale-specific resources where possible.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        
        return {"plan": response.choices[0].message.content}
    
    def calculate_odds(self, paths: List[dict]) -> int:
        """Calculate success probability based on data"""
        
        if not paths:
            return 45
        
        base_odds = 60  # Base Yale advantage
        path_bonus = min(len(paths) * 5, 25)  # More similar paths = higher odds
        
        return min(base_odds + path_bonus, 85)
    
    def extract_detailed_education(self, education_details: List[dict]) -> dict:
        """Extract detailed education information from structured data"""
        if not education_details:
            return {"major": "Liberal Arts", "degree": "", "graduation_year": "XX"}
        
        # Find Yale education
        yale_edu = None
        for edu in education_details:
            if edu.get('institution', '').lower().find('yale') != -1:
                yale_edu = edu
                break
        
        if not yale_edu and education_details:
            yale_edu = education_details[0]  # Use first if no Yale found
        
        if yale_edu:
            return {
                "major": yale_edu.get('field', 'Liberal Arts'),
                "degree": yale_edu.get('degree', ''),
                "graduation_year": str(yale_edu.get('end_year', 'XX'))[-2:] if yale_edu.get('end_year') else 'XX'
            }
        
        return {"major": "Liberal Arts", "degree": "", "graduation_year": "XX"}
    
    def analyze_career_progression(self, experience_history: List[dict]) -> dict:
        """Analyze career progression patterns"""
        if not experience_history:
            return {"progression_type": "Unknown", "years_experience": 0, "career_stage": "Early"}
        
        # Calculate years of experience
        years_experience = 0
        for exp in experience_history:
            start_date = exp.get('start_date') or ''
            end_date = exp.get('end_date') or ''
            if start_date and end_date:
                try:
                    start_year = int(start_date[:4]) if len(start_date) >= 4 else 0
                    end_year = int(end_date[:4]) if len(end_date) >= 4 else 2024
                    years_experience += max(0, end_year - start_year)
                except (ValueError, TypeError):
                    continue
        
        # Determine career stage
        if years_experience < 3:
            career_stage = "Early Career"
        elif years_experience < 7:
            career_stage = "Mid Career"
        else:
            career_stage = "Senior"
        
        # Analyze progression type
        progression_type = "Linear"
        if len(experience_history) > 2:
            companies = [exp.get('company', '') or '' for exp in experience_history]
            if len(set(companies)) > len(companies) * 0.7:  # High company switching
                progression_type = "Diverse"
        
        return {
            "progression_type": progression_type,
            "years_experience": years_experience,
            "career_stage": career_stage,
            "total_positions": len(experience_history)
        }
    
    def extract_skills_from_experience(self, experience_history: List[dict]) -> List[str]:
        """Extract key skills from experience descriptions"""
        skills = set()
        skill_keywords = {
            'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript', 'react': 'React',
            'machine learning': 'Machine Learning', 'data analysis': 'Data Analysis',
            'project management': 'Project Management', 'leadership': 'Leadership',
            'financial modeling': 'Financial Modeling', 'strategy': 'Strategy',
            'marketing': 'Marketing', 'sales': 'Sales', 'consulting': 'Consulting'
        }
        
        for exp in experience_history:
            description = (exp.get('description', '') + ' ' + exp.get('title', '')).lower()
            for keyword, skill in skill_keywords.items():
                if keyword in description:
                    skills.add(skill)
        
        return list(skills)[:5]  # Return top 5 skills
    
    def calculate_networking_score(self, alumni: dict) -> int:
        """Calculate networking potential score"""
        score = 0
        
        # Connection count
        connections = alumni.get('connections', 0) or 0
        if connections > 500:
            score += 30
        elif connections > 200:
            score += 20
        elif connections > 50:
            score += 10
        
        # Followers
        followers = alumni.get('followers', 0) or 0
        if followers > 1000:
            score += 20
        elif followers > 500:
            score += 15
        elif followers > 100:
            score += 10
        
        # Recommendations
        recommendations = alumni.get('recommendations_count', 0) or 0
        if recommendations > 10:
            score += 20
        elif recommendations > 5:
            score += 15
        elif recommendations > 0:
            score += 10
        
        # About section quality
        about = alumni.get('about', '') or ''
        if len(about) > 200:
            score += 10
        elif len(about) > 100:
            score += 5
        
        return min(score, 100)
    
    def analyze_industry_trends(self, target_company_alumni: List[dict]) -> str:
        """Analyze industry trends from alumni data"""
        if not target_company_alumni:
            return "No industry data available"
        
        # Analyze by industry
        industry_stats = {}
        location_stats = {}
        skill_frequency = {}
        career_stage_distribution = {}
        
        for alumni in target_company_alumni:
            # Industry analysis
            industry = alumni.get('company_industry', 'Unknown') or 'Unknown'
            if industry not in industry_stats:
                industry_stats[industry] = {'count': 0, 'avg_connections': 0, 'avg_networking_score': 0}
            industry_stats[industry]['count'] += 1
            industry_stats[industry]['avg_connections'] += alumni.get('connections', 0) or 0
            industry_stats[industry]['avg_networking_score'] += alumni.get('networking_score', 0) or 0
            
            # Location analysis
            location = alumni.get('location', 'Unknown') or 'Unknown'
            location_stats[location] = location_stats.get(location, 0) + 1
            
            # Skill frequency
            for skill in alumni.get('key_skills', []) or []:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            
            # Career stage distribution
            career_stage = alumni.get('career_progression', {}).get('career_stage', 'Unknown') or 'Unknown'
            career_stage_distribution[career_stage] = career_stage_distribution.get(career_stage, 0) + 1
        
        # Build insights
        insights = []
        
        # Top industries
        if industry_stats:
            top_industries = sorted(industry_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:3]
            insights.append("Top Industries:")
            for industry, stats in top_industries:
                avg_connections = stats['avg_connections'] // stats['count']
                avg_networking = stats['avg_networking_score'] // stats['count']
                insights.append(f"  • {industry}: {stats['count']} alumni (avg {avg_connections} connections, {avg_networking}/100 networking score)")
        
        # Top locations
        if location_stats:
            top_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            insights.append("\nTop Locations:")
            for location, count in top_locations:
                insights.append(f"  • {location}: {count} alumni")
        
        # Most common skills
        if skill_frequency:
            top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
            insights.append("\nMost Common Skills:")
            for skill, count in top_skills:
                insights.append(f"  • {skill}: {count} alumni")
        
        # Career stage distribution
        if career_stage_distribution:
            insights.append("\nCareer Stage Distribution:")
            for stage, count in career_stage_distribution.items():
                percentage = (count / len(target_company_alumni)) * 100
                insights.append(f"  • {stage}: {count} alumni ({percentage:.1f}%)")
        
        return "\n".join(insights) if insights else "No trends data available"
    
    # ===== NEW STREAMING CHAT METHODS =====
    
    def get_or_create_session(self, session_id: str) -> dict:
        """Get or create a conversation session with context"""
        if session_id not in self.conversation_sessions:
            self.conversation_sessions[session_id] = {
                'messages': [],
                'current_step': 1,
                'student_interests': [],
                'career_paths': [],
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        return self.conversation_sessions[session_id]
    
    def update_session(self, session_id: str, **updates):
        """Update session data"""
        if session_id in self.conversation_sessions:
            self.conversation_sessions[session_id].update(updates)
            self.conversation_sessions[session_id]['last_updated'] = datetime.now().isoformat()
    
    async def stream_chat_response(self, user_message: str, session_id: str = "default") -> AsyncGenerator[str, None]:
        """Stream chat response using the new 6-step conversation flow"""
        try:
            # Get or create session
            session = self.get_or_create_session(session_id)
            
            # Add user message to conversation history
            session['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Build conversation context
            conversation_context = self._build_conversation_context(session)
            
            # Create the full prompt with context
            full_prompt = f"{self.master_prompt}\n\n{conversation_context}"
            
            # Stream response from OpenAI
            stream = await self.client.chat.completions.create(
                model="gpt-4o",  # Using latest model
                messages=[
                    {"role": "system", "content": full_prompt}
                ],
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Collect full response for session storage
            full_response = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Add assistant response to conversation history
            session['messages'].append({
                'role': 'assistant',
                'content': full_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update session with extracted information
            self._extract_and_store_session_data(session, user_message, full_response)
            
        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            yield error_msg
            print(f"Chat error: {error_msg}")
    
    def _build_conversation_context(self, session: dict) -> str:
        """Build conversation context from session history"""
        if not session['messages']:
            return "This is the start of a new conversation. Follow Step 1 of the 6-step process."
        
        context_parts = []
        
        # Add conversation history
        context_parts.append("## CONVERSATION HISTORY:")
        for msg in session['messages'][-8:]:  # Last 8 messages for better context
            role = "Student" if msg['role'] == 'user' else "Milo"
            context_parts.append(f"{role}: {msg['content']}")
        
        # Add current step information with more context
        context_parts.append(f"\n## CURRENT STEP: {session['current_step']}")
        
        # Add step-specific instructions with more detailed guidance
        step_instructions = {
            1: "You are in Step 1: DISCOVER. Ask about activities, classes, or projects that make them feel alive or curious. Extract 3-5 core interests. Focus ONLY on this step - do not mention other steps.",
            2: "You are in Step 2: EXPLORE DREAM JOBS. Based on their interests, suggest 3-5 specific career paths with job titles, descriptions, and companies. Focus ONLY on this step - do not mention other steps.",
            3: "You are in Step 3: NEXT MOVES THIS SEMESTER. Suggest 3-4 concrete actions they can take THIS SEMESTER at Yale. Focus ONLY on this step - do not mention other steps.",
            4: "You are in Step 4: REAL OPPORTUNITIES. List actual programs they can apply to, organized by category. Focus ONLY on this step - do not mention other steps.",
            5: "You are in Step 5: CONNECT. Draft 2-3 different networking templates. Focus ONLY on this step - do not mention other steps.",
            6: "You are in Step 6: REFLECT & ITERATE. Ask what excites them most and offer three options. Focus ONLY on this step - do not mention other steps."
        }
        
        if session['current_step'] in step_instructions:
            context_parts.append(f"\n## CURRENT STEP FOCUS: {step_instructions[session['current_step']]}")
        
        # Add explicit instruction to prevent step dumping
        context_parts.append(f"\n## CRITICAL: Focus ONLY on Step {session['current_step']}. Do NOT mention or jump to other steps. Progress naturally through the conversation.")
        
        # Add extracted interests if available
        if session['student_interests']:
            context_parts.append(f"\n## EXTRACTED INTERESTS: {', '.join(session['student_interests'])}")
        
        # Add career paths if available
        if session['career_paths']:
            context_parts.append(f"\n## SUGGESTED CAREER PATHS: {', '.join(session['career_paths'])}")
        
        # Add conversation flow guidance
        context_parts.append(f"\n## IMPORTANT: Continue the conversation naturally based on the current step. Do NOT restart with 'STEP 1: DISCOVER' unless this is truly a new conversation. Build on what the student has already shared.")
        
        return "\n".join(context_parts)
    
    def _extract_and_store_session_data(self, session: dict, user_message: str, ai_response: str):
        """Extract and store relevant data from the conversation"""
        # Extract interests from user message (expanded keyword matching)
        interest_keywords = [
            'data science', 'machine learning', 'artificial intelligence', 'programming', 'coding',
            'writing', 'journalism', 'communication', 'media', 'publishing',
            'business', 'finance', 'consulting', 'entrepreneurship', 'startup',
            'research', 'academia', 'teaching', 'education',
            'healthcare', 'medicine', 'public health', 'policy',
            'law', 'legal', 'government', 'politics', 'public service',
            'art', 'design', 'creative', 'music', 'theater', 'film',
            'environment', 'sustainability', 'climate', 'energy',
            'international', 'global', 'foreign', 'language', 'culture',
            'engineering', 'cars', 'automotive', 'mechanical', 'electrical',
            'computer science', 'software', 'hardware', 'robotics',
            'biology', 'chemistry', 'physics', 'mathematics', 'statistics',
            'psychology', 'sociology', 'economics', 'political science',
            'history', 'literature', 'philosophy', 'languages'
        ]
        
        user_lower = user_message.lower()
        found_interests = [interest for interest in interest_keywords if interest in user_lower]
        
        if found_interests:
            session['student_interests'].extend(found_interests)
            session['student_interests'] = list(set(session['student_interests']))  # Remove duplicates
        
        # Intelligent step progression based on conversation analysis
        current_step = session['current_step']
        message_count = len(session['messages'])
        
        # More conservative step progression - only advance when we have enough information
        if current_step == 1:
            # Move to step 2 only if we have solid interests and the student has engaged
            if len(session['student_interests']) >= 3 and message_count >= 6:
                session['current_step'] = 2
        elif current_step == 2:
            # Move to step 3 only if we've thoroughly discussed career paths
            if ("career" in ai_response.lower() and "path" in ai_response.lower() and 
                message_count >= 8 and len(session['student_interests']) >= 3):
                session['current_step'] = 3
        elif current_step == 3:
            # Move to step 4 only if we've discussed semester actions thoroughly
            if ("semester" in ai_response.lower() and "course" in ai_response.lower() and 
                message_count >= 10):
                session['current_step'] = 4
        elif current_step == 4:
            # Move to step 5 only if we've discussed opportunities thoroughly
            if ("opportunity" in ai_response.lower() and "internship" in ai_response.lower() and 
                message_count >= 12):
                session['current_step'] = 5
        elif current_step == 5:
            # Move to step 6 only if we've discussed networking thoroughly
            if ("network" in ai_response.lower() and "connect" in ai_response.lower() and 
                message_count >= 14):
                session['current_step'] = 6
        
        # Prevent regression unless we're truly missing information
        ai_lower = ai_response.lower()
        
        # Only go back to step 1 if we have very few interests and it's early in conversation
        if (current_step > 1 and len(session['student_interests']) < 2 and message_count < 8 and
            ("what activities" in ai_lower or "make you feel most alive" in ai_lower)):
            session['current_step'] = 1
    
    async def get_chat_history(self, session_id: str = "default") -> List[dict]:
        """Get chat history for a session"""
        session = self.get_or_create_session(session_id)
        return session['messages']
    
    def clear_session(self, session_id: str = "default"):
        """Clear a conversation session"""
        if session_id in self.conversation_sessions:
            del self.conversation_sessions[session_id]
    
    def get_session_info(self, session_id: str = "default") -> dict:
        """Get session information"""
        session = self.get_or_create_session(session_id)
        return {
            'session_id': session_id,
            'current_step': session['current_step'],
            'student_interests': session['student_interests'],
            'career_paths': session['career_paths'],
            'message_count': len(session['messages']),
            'created_at': session['created_at'],
            'last_updated': session['last_updated']
        }