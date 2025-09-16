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

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface SessionInfo {
  session_id: string;
  current_step: number;
  student_interests: string[];
  career_paths: string[];
  message_count: number;
  created_at: string;
  last_updated: string;
}

export class MiloAPIService {
  private baseUrl = 'https://web-production-ef948.up.railway.app';

  // New streaming chat methods
  async streamChatResponse(
    message: string, 
    sessionId: string = 'default',
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                onError(data.error);
                return;
              }
              
              if (data.done) {
                onComplete();
                return;
              }
              
              if (data.content) {
                onChunk(data.content);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming chat error:', error);
      onError(error instanceof Error ? error.message : 'Unknown error');
    }
  }

  async getChatHistory(sessionId: string = 'default'): Promise<ChatMessage[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/history/${sessionId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data.messages || [];
    } catch (error) {
      console.error('Error getting chat history:', error);
      return [];
    }
  }

  async getSessionInfo(sessionId: string = 'default'): Promise<SessionInfo | null> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/session/${sessionId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting session info:', error);
      return null;
    }
  }

  async clearSession(sessionId: string = 'default'): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/session/${sessionId}`, {
        method: 'DELETE'
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error clearing session:', error);
    }
  }

  // Legacy method for backward compatibility
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
