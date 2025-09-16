import { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { LoadingPage } from './components/LoadingPage';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { TopNavigation } from './components/TopNavigation';
import { SearchSection } from './components/SearchSection';
import { JobCard } from './components/JobCard';
import PeopleTable from './components/PeopleTable';
import Feed from './components/Feed';
import { mockJobCards } from './data/mockJobCards';
import { OnboardingData } from './lib/supabase.ts';
import { DarkModeProvider, useDarkMode } from './contexts/DarkModeContext';
import { miloAPIService, AlumniProfile } from './lib/milo-api.ts';
import ReactMarkdown from 'react-markdown';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  alumniData?: AlumniProfile[];
  peopleToContact?: AlumniProfile[];
  companyData?: any[];
}




function AppContent() {
  const { user } = useUser();
  const [isLoading, setIsLoading] = useState(true);
  
  // Initialize user profile from Clerk user data
  const [userProfile] = useState<OnboardingData | null>(() => {
    const metadata = user?.unsafeMetadata as any;
    if (metadata?.onboarding_completed) {
      return {
        full_name: String(metadata.full_name || user?.fullName || 'Yale Student'),
        graduation_year: parseInt(String(metadata.class_year)) || 2025,
        major: String(metadata.major || 'Liberal Arts'),
        gpa: metadata.gpa || 3.8,
        preferred_locations: Array.isArray(metadata.preferred_locations) ? metadata.preferred_locations : [String(metadata.location || 'New Haven, CT')],
        preferred_industries: Array.isArray(metadata.preferred_industries) ? metadata.preferred_industries : ['Technology'],
        preferred_company_sizes: Array.isArray(metadata.preferred_company_sizes) ? metadata.preferred_company_sizes : ['Startup', 'Mid-size', 'Large'],
        work_model_preference: metadata.work_model_preference || 'hybrid',
        salary_expectation_min: metadata.salary_expectation_min || 80000,
        salary_expectation_max: metadata.salary_expectation_max || 120000,
        skills: Array.isArray(metadata.skills_and_clubs) ? metadata.skills_and_clubs : [],
        interests: Array.isArray(metadata.interests) ? metadata.interests : [],
        career_goals: metadata.career_goals || 'Build a successful career in your chosen field'
      };
    }
    return {
      full_name: user?.fullName || 'Yale Student',
      graduation_year: 2025,
      major: 'Liberal Arts',
      gpa: 3.8,
      preferred_locations: ['New Haven, CT', 'New York, NY', 'San Francisco, CA'],
      preferred_industries: ['Technology', 'Finance', 'Startups', 'AI/ML'],
      preferred_company_sizes: ['Startup', 'Mid-size', 'Large'],
      work_model_preference: 'hybrid',
      salary_expectation_min: 80000,
      salary_expectation_max: 120000,
      skills: ['Python', 'JavaScript', 'React', 'Machine Learning', 'Data Analysis'],
      interests: ['AI/ML', 'Fintech', 'Startups', 'Quantitative Finance'],
      career_goals: 'Work at a leading tech company or fintech startup, focusing on AI/ML applications in finance'
    };
  });
  const [proMode, setProMode] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activePage, setActivePage] = useState<'search' | 'feed'>('search');
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const { isDarkMode } = useDarkMode();


  // Chat functions - Updated to use streaming chat
  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Set chat as started to trigger UI transformation
    setHasStartedChat(true);

    const userMessage = {
      id: `user-${Date.now()}-${Math.random()}`,
      role: 'user' as const,
      content: message,
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    
    // Create assistant message for streaming
    const assistantMessage = {
      id: `assistant-${Date.now()}-${Math.random()}`,
      role: 'assistant' as const,
      content: '',
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, assistantMessage]);
    
    try {
      console.log('🎯 Sending message to streaming chat API:', { message });
      
      // Use the new streaming chat API
      await miloAPIService.streamChatResponse(
        message,
        'default', // session ID
        (chunk: string) => {
          // Update the assistant message with streaming content
          setChatMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: msg.content + chunk }
              : msg
          ));
        },
        () => {
          // Streaming complete
          console.log('✅ Streaming chat completed');
          setIsTyping(false);
        },
        (error: string) => {
          // Handle error
          console.error('❌ Streaming chat error:', error);
          setChatMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: `❌ **Error:** ${error}\n\nPlease try again.` }
              : msg
          ));
          setIsTyping(false);
        }
      );
      
    } catch (error) {
      console.error('❌ Chat error:', error);
      
      // Update the assistant message with error
      setChatMessages(prev => prev.map(msg => 
        msg.id === assistantMessage.id 
          ? { ...msg, content: `❌ **Error:** ${error instanceof Error ? error.message : 'Something went wrong'}\n\nPlease try again or check the server connection.` }
          : msg
      ));
      setIsTyping(false);
    }
  };

  const toggleChat = () => {
    if (!showChat) {
      setShowChat(true);
      setHasStartedChat(false);
      setChatMessages([]);
    } else {
      setShowChat(false);
      setHasStartedChat(false);
      setChatMessages([]);
    }
  };

  const clearChatSession = async () => {
    try {
      await miloAPIService.clearSession('default');
      setChatMessages([]);
      setHasStartedChat(false);
      console.log('✅ Chat session cleared');
    } catch (error) {
      console.error('❌ Error clearing chat session:', error);
    }
  };

  useEffect(() => {
    // Simulate initial loading
    const initializeApp = async () => {
      // Remove auto-complete - only advance when LoadingPage calls onComplete
    };
    
    initializeApp();
  }, []);

  const handleLoadingComplete = () => {
    setIsLoading(false);
  };



  const clearSearch = () => {
    setShowResults(false);
  };


  if (isLoading) {
    return <LoadingPage onComplete={handleLoadingComplete} />;
  }

  return (
    <div className={`min-h-screen flex transition-colors duration-300 ${
      isDarkMode ? 'bg-black text-white' : 'bg-white text-black'
    }`}>
      {/* Sidebar - hidden on mobile, visible on desktop */}
      <div className={`transition-all duration-300 ease-in-out ${
        sidebarOpen ? 'w-64' : 'hidden md:block'
      }`}>
        <Sidebar 
          isOpen={sidebarOpen} 
          onToggle={() => setSidebarOpen(!sidebarOpen)}
          currentPage={activePage}
          onPageChange={setActivePage}
        />
      </div>
      
      <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ease-in-out ${
        sidebarOpen ? 'md:ml-0' : ''
      }`}>
        {activePage === 'search' && (
          <TopNavigation 
            sidebarOpen={sidebarOpen} 
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
          />
        )}
        
        {activePage === 'search' ? (
          // Full-page ChatGPT-style Interface
          <div className="flex-1 flex flex-col h-screen w-full">
            {/* Minimal Header - Only show when chat has started */}
            {hasStartedChat && (
              <div className={`flex items-center justify-between px-4 py-3 border-b ${
                isDarkMode ? 'border-gray-800 bg-black' : 'border-gray-200 bg-white'
              }`}>
                <div className="flex items-center gap-3">
                  <button
                    onClick={toggleChat}
                    className={`p-2 rounded-lg transition-colors ${
                      isDarkMode ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-100 text-gray-600'
                    }`}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                </div>
                <button
                  onClick={toggleChat}
                  className={`p-2 rounded-lg transition-colors ${
                    isDarkMode ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-100 text-gray-600'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}

            {/* Main Content Area - Full height with bottom padding for floating input */}
            <div className={`flex-1 flex ${hasStartedChat ? 'flex-col' : 'flex-col justify-center items-center'} w-full ${hasStartedChat ? 'pb-32' : ''}`}>
              {/* Header - Only show when no chat started */}
              {!hasStartedChat && (
              <Header />
              )}

              {/* Chat Messages - Increased width, markdown rendering, user message styling */}
              {hasStartedChat && (
                <div className="flex-1 overflow-y-auto w-full">
                  {/* Chat Header with Clear Session Button */}
                  <div className="max-w-4xl mx-auto px-4 py-4 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        🎓 Milo - Yale Career Advisor
                      </div>
                      <button
                        onClick={clearChatSession}
                        className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 rounded-md transition-colors"
                      >
                        Clear Session
                      </button>
                    </div>
                  </div>
                  <div className="max-w-4xl mx-auto px-4 py-6 pb-16 space-y-8">
                    {chatMessages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} ${
                          message.role === 'assistant' ? 'items-start gap-3' : ''
                        }`}
                      >
                        {/* Milo square for assistant messages */}
                        {message.role === 'assistant' && (
                          <div className="w-6 h-6 bg-red-600 flex items-center justify-center text-white text-xs font-bold rounded-sm flex-shrink-0 mt-1">
                            人
                          </div>
                        )}
                        <div className={`max-w-[85%] ${
                          message.role === 'user' ? 'text-right' : 'text-left'
                        }`}>
                          {message.role === 'user' ? (
                            <div className={`inline-block px-4 py-3 rounded-2xl border ${
                              isDarkMode 
                                ? 'bg-gray-800/50 border-gray-600 text-gray-200' 
                                : 'bg-gray-100 border-gray-300 text-gray-800'
                            }`}>
                              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                {message.content}
                              </div>
                            </div>
                          ) : (
                            <div className={`text-sm leading-relaxed ${
                              isDarkMode ? 'text-white' : 'text-gray-900'
                            }`}>
       {/* Check if this is a loading message (contains shimmer text) */}
       {message.content.includes('**Thinking ⌄**') || message.content.includes('**Parsing user intent ⌄**') ? (
         <div className={`${
           isDarkMode
             ? 'text-gray-400'
             : 'text-gray-500'
         }`}>
           <div className={`${
             isDarkMode
               ? 'bg-gradient-to-r from-gray-600 via-gray-400 to-gray-600'
               : 'bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300'
           } bg-[length:200%_100%] animate-shimmer bg-clip-text text-transparent`}>
             <ReactMarkdown>
               {message.content}
             </ReactMarkdown>
           </div>
         </div>
       ) : (
                                // Check if this is a pathways message with JSON data
                                message.content.includes('**Companies to Consider**') && (message.content.includes('```json') || message.content.includes('"companies"')) ? (
                                  <div>
                                    {(() => {
                                      try {
                                        // Try to extract JSON from code blocks first
                                        let jsonMatch = message.content.match(/```json\n([\s\S]*?)\n```/);
                                        let jsonString = '';
                                        
                                        if (jsonMatch) {
                                          jsonString = jsonMatch[1];
                                        } else {
                                          // If no code blocks, try to extract JSON from the message content
                                          const jsonStart = message.content.indexOf('{');
                                          const jsonEnd = message.content.lastIndexOf('}') + 1;
                                          if (jsonStart !== -1 && jsonEnd > jsonStart) {
                                            jsonString = message.content.substring(jsonStart, jsonEnd);
                                          }
                                        }
                                        
                                        if (jsonString) {
                                          // Clean the JSON string to handle common issues
                                          let cleanJsonString = jsonString
                                            .replace(/,\s*}/g, '}') // Remove trailing commas before }
                                            .replace(/,\s*]/g, ']') // Remove trailing commas before ]
                                            .replace(/\n/g, ' ') // Replace newlines with spaces
                                            .replace(/\s+/g, ' ') // Replace multiple spaces with single space
                                            .trim();
                                          
                                          const jsonData = JSON.parse(cleanJsonString);
                                          if (jsonData.companies && Array.isArray(jsonData.companies)) {
                                            return (
                                              <div className="mt-4">
                                                {/* Companies to Consider Header */}
                                                <div className="mb-3">
                                                  <div className="text-[10px] text-gray-400 font-light tracking-wider uppercase">
                                                    Companies to Consider
                                                  </div>
                                                </div>
                                                
                                                <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                                                  {jsonData.companies.map((company: any, index: number) => (
                                                    <div key={index} className="flex flex-col">
                                                      {/* Company Card */}
                                                      <div className={`aspect-square p-3 border rounded-lg transition-colors duration-200 flex flex-col bg-black border-gray-700 text-white`}>
                                                        {/* Header with Logo and Match Score */}
                                                        <div className="flex items-start justify-between mb-3">
                                                          {/* Company Logo */}
                                                          <div className="w-14 h-14 rounded flex items-center justify-center flex-shrink-0">
                                                            <img 
                                                              src={`https://img.logo.dev/${company.domain}?token=pk_c2nKhfMyRIOeCjrk-6-RRw`}
                                                              alt={`${company.name} logo`}
                                                              className="w-14 h-14 rounded object-contain"
                                                              onError={(e) => {
                                                                const target = e.target as HTMLImageElement;
                                                                target.style.display = 'none';
                                                                const fallback = target.nextElementSibling as HTMLElement;
                                                                if (fallback) {
                                                                  fallback.style.display = 'flex';
                                                                }
                                                              }}
                                                            />
                                                            <div 
                                                              className="w-14 h-14 rounded bg-gray-600 text-white text-lg font-bold flex items-center justify-center hidden"
                                                              style={{ display: 'none' }}
                                                            >
                                                              {company.name.charAt(0).toUpperCase()}
                                                            </div>
                                                          </div>

                                                          {/* Color-coded Match Score */}
                                                          <div className="flex flex-col items-end">
                                                            <div className="text-[8px] text-gray-400 font-light tracking-wider uppercase mb-0.5">
                                                              MATCH
                                                            </div>
                                                            <div className={`
                                                              px-1.5 py-0.5 rounded font-mono text-white text-xs font-bold
                                                              ${(() => {
                                                                const relevance = company.relevance;
                                                                if (typeof relevance === 'string') {
                                                                  return relevance.toLowerCase() === 'high' ? 'bg-emerald-500' :
                                                                         relevance.toLowerCase() === 'medium' ? 'bg-yellow-500' :
                                                                         'bg-orange-500';
                                                                } else {
                                                                  const numRelevance = Number(relevance) || 0;
                                                                  return numRelevance >= 90 ? 'bg-emerald-500' :
                                                                         numRelevance >= 70 ? 'bg-yellow-500' :
                                                                         numRelevance >= 50 ? 'bg-orange-500' :
                                                                         'bg-red-500';
                                                                }
                                                              })()}
                                                            `}>
                                                              {(() => {
                                                                const relevance = company.relevance;
                                                                if (typeof relevance === 'string') {
                                                                  return relevance === 'High' ? '95' :
                                                                         relevance === 'Medium' ? '75' :
                                                                         '60';
                                                                } else {
                                                                  // Display relevance score as-is (0-100 scale)
                                                                  return Math.round(Number(relevance) || 0);
                                                                }
                                                              })()}
                                                            </div>
                                                          </div>
                                                        </div>

                                                        {/* Company Name and Domain */}
                                                        <div className="flex-1 flex flex-col justify-between">
                                                          <div>
                                                            <h3 className="text-xs font-bold mb-1 truncate text-white">
                                                              {company.name}
                                                            </h3>
                                                            
                                                            <div className="text-[10px] mb-2 text-gray-400">
                                                              {company.domain}
                                                            </div>
                                                          </div>
                                                        </div>
                                                      </div>
                                                      
                                                      {/* Team Tag - Directly below each company card */}
                                                      <div className="mt-2 flex justify-center">
                                                        <div className="w-full px-3 py-1 bg-black text-white text-[10px] rounded border border-gray-600 font-medium text-center leading-tight min-h-[32px] flex items-center justify-center">
                                                          {company.team || 'Team not specified'}
                                                        </div>
                                                      </div>
                                                      
                                                      {/* Apply Button - Below team tag */}
                                                      <div className="mt-2 flex justify-center">
                                                        <a 
                                                          href={company.career_url || `https://${company.domain}/careers`}
                                                          target="_blank"
                                                          rel="noopener noreferrer"
                                                          className="w-full px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-[10px] font-medium rounded transition-colors duration-200 flex items-center justify-center gap-1"
                                                        >
                                                          <div className="w-3 h-3 bg-red-500 rounded-sm flex items-center justify-center">
                                                            <span className="text-[8px] font-bold text-white">人</span>
                                                          </div>
                                                          Apply
                                                        </a>
                                                      </div>
                                                    </div>
                                                  ))}
                                                </div>
                                                
                                                {/* Extra padding for scrolling */}
                                                <div className="mt-8"></div>
                                              </div>
                                            );
                                          }
                                        }
                                      } catch (e) {
                                        console.error('Error parsing companies JSON:', e);
                                        return (
                                          <div className="mt-4">
                                            <div className="text-[10px] text-gray-400 font-light tracking-wider uppercase mb-3">
                                              Companies to Consider
                                            </div>
                                            <div className="text-red-400 text-sm">
                                              Error loading companies. Please try again.
                                            </div>
                                          </div>
                                        );
                                      }
                                      return null;
                                    })()}
                                  </div>
                                ) : message.content.includes('**High-Leverage Next Moves**') && (message.content.includes('```json') || message.content.includes('"moves"')) ? (
                                  <div>
                                    {(() => {
                                      try {
                                        // Try to extract JSON from code blocks first
                                        let jsonMatch = message.content.match(/```json\n([\s\S]*?)\n```/);
                                        let jsonString = '';
                                        
                                        if (jsonMatch) {
                                          jsonString = jsonMatch[1];
                                        } else {
                                          // If no code blocks, try to extract JSON from the message content
                                          const jsonStart = message.content.indexOf('{');
                                          const jsonEnd = message.content.lastIndexOf('}') + 1;
                                          if (jsonStart !== -1 && jsonEnd > jsonStart) {
                                            jsonString = message.content.substring(jsonStart, jsonEnd);
                                          }
                                        }
                                        
                                        if (jsonString) {
                                          // Clean the JSON string to handle common issues
                                          let cleanJsonString = jsonString
                                            .replace(/,\s*}/g, '}') // Remove trailing commas before }
                                            .replace(/,\s*]/g, ']') // Remove trailing commas before ]
                                            .replace(/\n/g, ' ') // Replace newlines with spaces
                                            .replace(/\s+/g, ' ') // Replace multiple spaces with single space
                                            .trim();
                                          
                                          const jsonData = JSON.parse(cleanJsonString);
                                          if (jsonData.moves && Array.isArray(jsonData.moves)) {
                                            return (
                                              <div className="mt-4">
                                                {/* High-Leverage Next Moves Header */}
                                                <div className="mb-3">
                                                  <div className="text-[10px] text-gray-400 font-light tracking-wider uppercase">
                                                    High-Leverage Next Moves
                                                  </div>
                                                </div>
                                                
                                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                  {jsonData.moves.map((move: any, index: number) => (
                                                    <div key={index} className="flex flex-col">
                                                      {/* Move Card */}
                                                      <div className={`p-3 border rounded-lg transition-colors duration-200 bg-black border-gray-700 text-white flex-1 flex flex-col`}>
                                                        {/* Logo and Timeline Badge */}
                                                        <div className="flex items-center justify-between mb-2">
                                                          <div className="w-8 h-8 bg-gray-700 rounded flex items-center justify-center">
                                                            <img 
                                                              src={`https://logo.clearbit.com/${move.domain}`}
                                                              alt={`${move.title} logo`}
                                                              className="w-6 h-6 rounded"
                                                              onError={(e) => {
                                                                const target = e.currentTarget as HTMLImageElement;
                                                                target.style.display = 'none';
                                                                const fallback = target.nextElementSibling as HTMLElement;
                                                                if (fallback) {
                                                                  fallback.style.display = 'flex';
                                                                }
                                                              }}
                                                            />
                                                            <div className="w-6 h-6 bg-gray-600 rounded flex items-center justify-center text-xs font-bold text-white" style={{display: 'none'}}>
                                                              {move.title.charAt(0)}
                                                            </div>
                                                          </div>
                                                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                            move.timeline === 'immediate' ? 'bg-red-500/20 text-red-400' :
                                                            move.timeline === 'this semester' ? 'bg-yellow-500/20 text-yellow-400' :
                                                            'bg-green-500/20 text-green-400'
                                                          }`}>
                                                            {move.timeline}
                                                          </span>
                                                        </div>
                                                        
                                                        {/* Title */}
                                                        <h3 className="font-semibold text-white text-xs mb-2 leading-tight">
                                                          {move.title}
                                                        </h3>
                                                        
                                                        {/* Description as concise bullet points */}
                                                        <div className="text-gray-300 text-xs mb-2 flex-1">
                                                          <ul className="list-disc list-inside space-y-1">
                                                            {move.description.split('. ').filter((point: string) => point.trim()).slice(0, 2).map((point: string, pointIndex: number) => (
                                                              <li key={pointIndex} className="leading-tight">
                                                                {point.trim()}
                                                              </li>
                                                            ))}
                                                          </ul>
                                                        </div>
                                                        
                                                        {/* How to start as concise bullet points */}
                                                        <div className="text-xs text-gray-400">
                                                          <strong>Start:</strong>
                                                          <ul className="list-disc list-inside mt-1 space-y-1">
                                                            {move.how_to_start.split('. ').filter((point: string) => point.trim()).slice(0, 2).map((point: string, pointIndex: number) => (
                                                              <li key={pointIndex} className="leading-tight">
                                                                {point.trim()}
                                                              </li>
                                                            ))}
                                                          </ul>
                                                        </div>
                                                      </div>
                                                    </div>
                                                  ))}
                                                </div>
                                                
                                                {/* Extra padding for scrolling */}
                                                <div className="mt-8"></div>
                                              </div>
                                            );
                                          }
                                        }
                                      } catch (e) {
                                        console.error('Error parsing pathways moves JSON:', e);
                                        return (
                                          <div className="mt-4">
                                            <div className="text-[10px] text-gray-400 font-light tracking-wider uppercase mb-3">
                                              High-Leverage Next Moves
                                            </div>
                                            <div className="text-red-400 text-sm">
                                              Error loading pathways moves. Please try again.
                                            </div>
                                          </div>
                                        );
                                      }
                                      return null;
                                    })()}
                                  </div>
                                ) : message.content.includes('**Yale Alumni at Companies**') || message.content.includes('**Similar Yale Alumni**') ? (
                                  <div>
                                    <div className={`${
                                      isDarkMode ? 'text-white' : 'text-gray-900'
                                    }`}>
                                      <ReactMarkdown>
                                        {message.content.split('```json')[0]}
                                      </ReactMarkdown>
                                    </div>
                                    {(() => {
                                      try {
                                        // Extract JSON from the message content more efficiently
                                        const jsonStart = message.content.indexOf('[');
                                        const jsonEnd = message.content.lastIndexOf(']') + 1;
                                        
                                        if (jsonStart !== -1 && jsonEnd !== -1) {
                                          const jsonString = message.content.substring(jsonStart, jsonEnd);
                                          const alumniData = JSON.parse(jsonString);
                                          
                                          // Validate and filter alumni data
                                          if (Array.isArray(alumniData) && alumniData.length > 0) {
                                            const validAlumni = alumniData.filter(alumni => 
                                              alumni && 
                                              alumni.name && 
                                              alumni.current_role && 
                                              alumni.current_company
                                            );
                                            
                                            if (validAlumni.length > 0) {
                                              return (
                                                <div className="mt-4">
                                                  <PeopleTable 
                                                    people={validAlumni}
                                                    title="Yale Alumni at Target Companies"
                                                    maxRows={10}
                                                  />
                                                </div>
                                              );
                                            } else {
                                              return (
                                                <div className="mt-4 text-sm text-gray-400">
                                                  No valid alumni data found
                                                </div>
                                              );
                                            }
                                          }
                                        }
                                      } catch (e) {
                                        console.error('Error parsing alumni JSON:', e);
                                        return (
                                          <div className="mt-4 text-sm text-red-400">
                                            Error loading alumni data
                                          </div>
                                        );
                                      }
                                      return null;
                                    })()}
                                  </div>
                                ) : message.alumniData ? (
                                  // Handle alumni data with PeopleTable
                                  <div className="mt-4">
                                    <div className="text-sm text-gray-400 mb-4">
                                      {message.content}
                                    </div>
                                    <PeopleTable 
                                      people={message.alumniData}
                                      title="Yale Alumni"
                                      maxRows={10}
                                    />
                                  </div>
                                ) : message.peopleToContact ? (
                                  // Handle people to contact with PeopleTable
                                  <div className="mt-4">
                                    <div className="text-sm text-gray-400 mb-4">
                                      {message.content}
                                    </div>
                                    <PeopleTable 
                                      people={message.peopleToContact}
                                      title="People to Contact First"
                                      maxRows={5}
                                    />
                                  </div>
                                ) : message.companyData ? (
                                  // Handle company cards display
                                  <div className="mt-4">
                                    <div className="text-sm text-gray-400 mb-4">
                                      {message.content}
                                    </div>
                                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                                      {message.companyData.map((company: any, index: number) => (
                                        <div key={index} className={`p-4 border rounded-lg transition-colors duration-200 flex flex-col ${
                                          isDarkMode 
                                            ? 'bg-gray-900 border-gray-800 text-white hover:border-gray-700' 
                                            : 'bg-white border-gray-200 text-gray-900 hover:border-gray-300'
                                        }`}>
                                          {/* Company Logo */}
                                          <div className="w-12 h-12 rounded flex items-center justify-center flex-shrink-0 mb-3 mx-auto">
                                            <img 
                                              src={`https://img.logo.dev/${company.domain}.com?token=pk_c2nKhfMyRIOeCjrk-6-RRw`}
                                              alt={`${company.name} logo`}
                                              className="w-12 h-12 rounded object-contain"
                                              onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.style.display = 'none';
                                                const fallback = target.nextElementSibling as HTMLElement;
                                                if (fallback) {
                                                  fallback.style.display = 'flex';
                                                }
                                              }}
                                            />
                                            <div 
                                              className="w-12 h-12 rounded bg-gray-600 text-white text-lg font-bold flex items-center justify-center hidden"
                                              style={{ display: 'none' }}
                                            >
                                              {company.name.charAt(0).toUpperCase()}
                                            </div>
                                          </div>
                                          
                                          {/* Company Name */}
                                          <h4 className={`text-sm font-bold text-center mb-1 ${
                                            isDarkMode ? 'text-white' : 'text-gray-900'
                                          }`}>
                                            {company.name}
                                          </h4>
                                          
                                          {/* Industry */}
                                          <p className={`text-xs text-center ${
                                            isDarkMode ? 'text-gray-400' : 'text-gray-600'
                                          }`}>
                                            {company.industry}
                                          </p>
                                          
                                          {/* Relevance Score */}
                                          <div className="mt-2 flex justify-center">
                                            <div className={`px-2 py-1 rounded text-xs font-bold ${
                                              company.relevance >= 90 ? 'bg-green-500' :
                                              company.relevance >= 70 ? 'bg-yellow-500' :
                                              'bg-orange-500'
                                            } text-white`}>
                                              {company.relevance}% match
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                ) : (
                                  <ReactMarkdown>
                                    {message.content}
                                  </ReactMarkdown>
                                )
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {/* ChatGPT-style Loading Animation */}
                    {isTyping && (
                      <div className="flex justify-start">
                        <div className="max-w-[80%]">
                          {/* Single white ball loader */}
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Search Input - Only show when no chat started */}
              {!hasStartedChat && (
                <div className="w-full max-w-2xl px-4">
              <SearchSection
                    onSearch={sendMessage}
                onClear={clearSearch}
                isLoading={isTyping}
                proMode={proMode}
                setProMode={setProMode}
                    isChatMode={false}
                    onToggleChat={toggleChat}
              />
                </div>
              )}
            </div>


            {/* Floating Chat Input - Transparent background, increased width */}
            {hasStartedChat && (
              <div className="fixed bottom-0 left-0 right-0 z-50">
                <div className="w-full">
                  <div className="max-w-3xl mx-auto px-4 py-2">
                    <SearchSection
                      onSearch={sendMessage}
                      onClear={clearSearch}
                      isLoading={isTyping}
                      proMode={proMode}
                      setProMode={setProMode}
                      isChatMode={true}
                      onToggleChat={toggleChat}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <Feed userProfile={userProfile} />
        )}

            {showResults && (
              <div className={`rounded-lg p-4 sm:p-6 max-w-6xl mx-auto w-full transition-colors duration-300 ${
                isDarkMode ? 'bg-gray-900/80' : 'bg-white'
              }`}>
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className={`text-xl font-semibold ${
                      isDarkMode ? 'text-white' : 'text-gray-900'
                    }`}>
                      Job Opportunities
                    </h2>
                    <div className={`text-sm ${
                      isDarkMode ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {mockJobCards.length} opportunities found
                    </div>
                  </div>
                  
                  <div className="grid gap-4">
                    {mockJobCards.map((job, index) => (
                      <JobCard
                        key={index}
                        companyLogo={job.companyLogo}
                        companyName={job.companyName}
                        jobTitle={job.jobTitle}
                        description={job.description}
                        location={job.location}
                        salary={job.salary}
                        postedDate={job.postedDate}
                        skills={job.skills}
                        metrics={job.metrics}
                        badges={job.badges}
                        isDark={isDarkMode}
                        type={job.type}
                      />
                    ))}
                  </div>
                </div>
              </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <DarkModeProvider>
      <AppContent />
    </DarkModeProvider>
  );
}

export default App;// Force new deployment - Sun Sep 14 13:57:28 EDT 2025
