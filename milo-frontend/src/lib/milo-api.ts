/**
 * Milo API Service - Connects to our enhanced Yale alumni backend
 */

export interface StudentProfile {
  name: string;
  class_year: number;
  major: string;
  skills_and_clubs: string[];
  interests: string[];
  constraints: string[];
  current_term: string;
  current_date: string;
  location: string;
}

export interface AlumniProfile {
  name: string;
  position: string;
  company: string;
  location: string;
  connections: number;
  followers: number;
  recommendations: number;
  major: string;
  degree: string;
  graduation_year: string;
  about: string;
  experience_history: Array<{
    company: string;
    title: string;
    start_date: string;
    end_date: string;
    description: string;
  }>;
  company_industry: string;
  company_size: string;
  yale_alumni_at_company: number;
  career_progression: {
    progression_type: string;
    years_experience: number;
    career_stage: string;
    total_positions: number;
  };
  key_skills: string[];
  networking_score: number;
}

export interface CareerPath {
  path: string;
  count: number;
  examples: Array<{
    name: string;
    current_role: string;
    current_company: string;
    career_path: string;
    major: string;
    graduation_year: string;
    location: string;
  }>;
}

export interface MiloResponse {
  analysis: {
    target_companies: string[];
    target_roles: string[];
    industry: string;
    motivation: string;
    timeline: string;
  };
  target_company_alumni: AlumniProfile[];
  career_paths: CareerPath[];
  people_to_contact: AlumniProfile[];
  action_plan: {
    plan: string;
  };
  success_odds: number;
  processed_query?: {
    query_type: string;
    original_query: string;
    expanded_query: string;
    detected_industry?: string;
    detected_companies: string[];
    detected_roles: string[];
    confidence: number;
    student_intent?: string;
  };
  error?: string;
}

export class MiloAPIService {
  private baseUrl = 'http://localhost:8001';

  async generateOpportunities(userInput: string): Promise<MiloResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('🔍 Raw API Response:', data);
      console.log('🔍 Action Plan:', data.action_plan);
      return data;
    } catch (error) {
      console.error('Error calling Milo API:', error);
      // Return a fallback response with proper structure
      return this.getFallbackResponse(userInput);
    }
  }

  private getFallbackResponse(userInput: string): MiloResponse {
    return {
      analysis: {
        target_companies: ["Technology Companies"],
        target_roles: ["Software Engineer"],
        industry: "Technology",
        motivation: "Career growth and development",
        timeline: "1-2 years"
      },
      processed_query: {
        query_type: "general",
        original_query: userInput,
        expanded_query: userInput,
        detected_industry: "Technology",
        detected_companies: [],
        detected_roles: [],
        confidence: 0.5
      },
      target_company_alumni: [],
      career_paths: [],
      people_to_contact: [],
      action_plan: {
        plan: `Hey there, you want to work at your target company? I'm having trouble connecting to the Yale alumni database right now, but I can still help you with your career goals.

**IMMEDIATE ACTIONS (Next 7 Days):**
1. Research companies in your field of interest
2. Update your LinkedIn profile with relevant skills
3. Start networking with professionals in your target industry

**THIS SEMESTER:**
- Take relevant courses to build skills
- Join professional organizations
- Attend career fairs and networking events

**CAREER TIMELINE:**
- Apply for internships in your target field
- Build a strong portfolio of projects
- Network with alumni and professionals

Please try again in a moment, and I'll connect you with specific Yale alumni who can help with your career goals!`
      },
      success_odds: 60,
      error: "Unable to connect to Yale alumni database"
    };
  }
}

export const miloAPIService = new MiloAPIService();
